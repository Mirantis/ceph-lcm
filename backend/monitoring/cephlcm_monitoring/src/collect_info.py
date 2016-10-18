import re
import sys
import time
import json
import uuid
import Queue
import pipes
import shutil
import socket
import logging
import os.path
import argparse
import warnings
import datetime
import threading
import subprocess
import collections


logger = logging.getLogger('collect')


class CollectSettings(object):
    def __init__(self):
        self.disabled = []

    def disable(self, pattern):
        self.disabled.append(re.compile(pattern))

    def allowed(self, path):
        for pattern in self.disabled:
            if pattern.search(path):
                return False
        return True


def check_output(cmd, log=True):
    if log:
        logger.debug("CMD: %r", cmd)

    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out = p.communicate()
    code = p.wait()

    if 0 == code:
        return True, out[0]
    else:
        return True, out[0] + out[1]


# This variable is updated from main function
SSH_OPTS = "-o LogLevel=quiet -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
SSH_OPTS += "-o ConnectTimeout={0} -l {1} -i {2}"


def check_output_ssh(host, opts, cmd, no_retry=False, max_retry=3):
    cmd = pipes.quote(cmd)
    logger.debug("SSH:%s: %s", host, cmd)
    while True:
        ok, res = check_output("ssh {0} {1} -- sudo -s -- {2}".format(SSH_OPTS, host, cmd), False)
        if no_retry or res != "" or max_retry == 1:
            return ok, res

        max_retry -= 1
        time.sleep(1)
        logger.warning("Retry SSH:%s: %r", host, cmd)


def get_device_for_file(host, opts, fname):
    ok, dev_str = check_output_ssh(host, opts, "df " + fname)
    assert ok

    dev_str = dev_str.strip()
    dev_link = dev_str.strip().split("\n")[1].split()[0]

    if dev_link == 'udev':
        dev_link = fname

    abs_path_cmd = (
        "set -e; "
        'path="{0}"; '
        'while [ -h "$path" ]; do'
        '  path=$(readlink "$path"); '
        '  path=$(readlink -f "$path"); '
        "done; "
        "echo $path;"
    ).format(dev_link)
    ok, dev = check_output_ssh(host, opts, abs_path_cmd)
    assert ok

    root_dev = dev = dev.strip()
    while root_dev[-1].isdigit():
        root_dev = root_dev[:-1]

    return root_dev, dev


class Collector(object):
    name = None
    run_alone = False

    def __init__(self, opts, collect_settings, res_q):
        self.collect_settings = collect_settings
        self.opts = opts
        self.res_q = res_q

    def run2emit(self, path, format, cmd, check=True):
        if check:
            if not self.collect_settings.allowed(path):
                return
        ok, out = check_output(cmd)
        if not ok:
            logger.warning("Cmd {0} failed locally".format(cmd))
        self.emit(path, format, ok, out, check=False)

    def ssh2emit(self, host, path, format, cmd, check=True):
        if check:
            if not self.collect_settings.allowed(path):
                return
        ok, out = check_output_ssh(host, self.opts, cmd)
        if not ok:
            logger.warning("Cmd {0} failed on node {1}".format(cmd, host))
        self.emit(path, format, ok, out, check=False)

    def emit(self, path, format, ok, out, check=True):
        if check:
            if not self.collect_settings.allowed(path):
                return
        self.res_q.put((ok, path, (format if ok else 'err'), out))

    # should provides set of on_XXX methods
    # where XXX - node role role
    # def collect_XXX(self, path, node, **params):
    #    pass

    # util functions, used in different classes
    def get_host_interfaces(self, host):
        ok, net_devs = check_output_ssh(host, self.opts, 'ls -l /sys/class/net')
        if not ok:
            logger.warning("'ls -l /sys/class/net' failed %s", net_devs)
            return

        for line in net_devs.strip().split("\n")[1:]:
            if not line.startswith('l'):
                continue

            params = line.split()

            if len(params) < 11:
                logger.warning("Strange line in 'ls -l /sys/class/net' node %s: %r",
                               host, line)
                continue

            yield ('devices/pci' in params[10]), params[8]


class CephDataCollector(Collector):

    name = 'ceph'
    run_alone = False

    def __init__(self, *args, **kwargs):
        Collector.__init__(self, *args, **kwargs)
        self.ceph_cmd = "ceph -c {0.conf} -k {0.key} --format json ".format(self.opts)

        self.osd_devs = {}
        self.osd_devs_lock = threading.Lock()

    def collect_master(self, path=None, node=None):
        path = path + "/master/"

        curr_data = "{0}\n{1}\n{2}".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            time.time())

        self.emit(path + "collected_at", 'txt', True, curr_data)

        ok, status = check_output(self.ceph_cmd + "status")
        self.emit(path + "status", 'json', ok, status)
        assert ok

        cmds = ['osd tree', 'df', 'auth list', 'osd dump',
                'health', 'mon_status', 'osd lspools',
                'osd perf']

        if json.loads(status)['pgmap']['num_pgs'] > self.opts.max_pg_dump_count:
            logger.warning(
                ("pg dump skipped, as num_pg ({0}) > max_pg_dump_count ({1})." +
                 " Use --max-pg-dump-count NUM option to change the limit").format(
                    json.loads(status)['pgmap']['num_pgs'],
                    self.opts.max_pg_dump_count))
        else:
            cmds.append('pg dump')

        for cmd in cmds:
            self.run2emit(path + cmd.replace(" ", "_"), 'json',
                          self.ceph_cmd + cmd)

        self.run2emit(path + "rados_df", 'json',
                      "rados df -c {0.conf} -k {0.key} --format json".format(self.opts))

        ok, out = check_output(self.ceph_cmd + 'health detail')
        if not ok:
            self.emit(path + 'health_detail', 'err', ok, out)
        else:
            self.emit(path + 'health_detail', 'json', ok, out)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out_file = os.tempnam()

        ok, out = check_output(self.ceph_cmd + "osd getcrushmap -o " + out_file)
        if not ok:
            self.emit(path + 'crushmap', 'err', ok, out)
        else:
            data = open(out_file, "rb").read()
            os.unlink(out_file)
            self.emit(path + 'crushmap', 'bin', ok, data)

    def emit_device_info(self, host, path, device_file):
        ok, dev_str = check_output_ssh(host, self.opts, "df " + device_file)
        assert ok
        dev_data = dev_str.strip().split("\n")[1].split()

        used = int(dev_data[2]) * 1024
        avail = int(dev_data[3]) * 1024

        root_dev, dev = get_device_for_file(host, self.opts, device_file)

        cmd = "cat /sys/block/{0}/queue/rotational".format(os.path.basename(root_dev))
        ok, is_ssd_str = check_output_ssh(host, self.opts, cmd)
        assert ok
        is_ssd = is_ssd_str.strip() == '0'

        self.ssh2emit(host, path + '/hdparm', 'txt', "sudo hdparm -I " + root_dev)
        self.ssh2emit(host, path + '/smartctl', 'txt', "sudo smartctl -a " + root_dev)
        self.emit(path + '/stats', 'json', True,
                  json.dumps({'dev': dev,
                              'root_dev': root_dev,
                              'used': used,
                              'avail': avail,
                              'is_ssd': is_ssd}))
        return root_dev

    def collect_osd(self, path, host, osd_id):
        path = "{0}/osd/{1}/".format(path, osd_id)
        ok, out = check_output_ssh(host, self.opts, "ps aux | grep ceph-osd")

        for line in out.split("/n"):
            if '-i ' + str(osd_id) in line and 'ceph-osd' in line:
                osd_running = True
                break
            elif '--id ' + str(osd_id) in line and 'ceph-osd' in line:
                osd_running = True
                break
        else:
            osd_running = False
            logger.warning("osd-{0} in node {1} is down.".format(osd_id, host) +
                           " No config available, will use default data and journal path")

        self.emit(path + "osd_daemons", 'txt', ok, out)
        self.ssh2emit(host, path + "log", 'txt',
                      "tail -n {0} /var/log/ceph/ceph-osd.{1}.log".format(
                          self.opts.ceph_log_max_lines, osd_id))

        if osd_running:
            osd_cfg_cmd = "sudo ceph -f json --admin-daemon /var/run/ceph/ceph-osd.{0}.asok config show"
            ok, data = check_output_ssh(host, self.opts, osd_cfg_cmd.format(osd_id))

            self.emit(path + "config", 'json', ok, data)
            assert ok

            osd_cfg = json.loads(data)

            data_dev = osd_cfg.get('osd_data')
            jdev = osd_cfg.get('osd_journal')

            if data_dev is not None:
                data_dev = str(data_dev)

            if jdev is not None:
                jdev = str(jdev)

        else:
            data_dev = None
            jdev = None

        if data_dev is None:
            data_dev = "/var/lib/ceph/osd/ceph-{0}".format(osd_id)

        if jdev is None:
            jdev = "/var/lib/ceph/osd/ceph-{0}/journal".format(osd_id)

        self.ssh2emit(host, path + "storage_ls", 'txt',
                      "ls -1 " + os.path.join(data_dev, 'current'))
        data_root_dev = self.emit_device_info(host, path + "data", data_dev)
        jroot_dev = self.emit_device_info(host, path + "journal", jdev)

        with self.osd_devs_lock:
            self.osd_devs[osd_id] = (host, data_root_dev, jroot_dev)

    def collect_monitor(self, path, host, name):
        path = "{0}/mon/{1}/".format(path, host)
        self.ssh2emit(host, path + "mon_daemons", 'txt', "ps aux | grep ceph-mon")
        self.ssh2emit(host, path + "mon_log", 'txt',
                      "tail -n {0} /var/log/ceph/ceph-mon.{1}.log".format(
                          self.opts.ceph_log_max_lines, name))
        self.ssh2emit(host, path + "ceph_log", 'txt',
                      "tail -n {0} /var/log/ceph/ceph.log".format(
                          self.opts.ceph_log_max_lines, name))
        self.ssh2emit(host, path + "ceph_audit", 'txt',
                      "tail -n {0} /var/log/ceph/ceph.audit.log".format(
                          self.opts.ceph_log_max_lines, name))


class NodeCollector(Collector):

    name = 'node'
    run_alone = False

    node_commands = [
        ("lshw", "xml", "lshw -xml"),
        ("lsblk", "txt", "lsblk -a"),
        ("diskstats", "txt", "cat /proc/diskstats"),
        ("uname", "txt", "uname -a"),
        ("dmidecode", "txt", "dmidecode"),
        ("meminfo", "txt", "cat /proc/meminfo"),
        ("loadavg", "txt", "cat /proc/loadavg"),
        ("cpuinfo", "txt", "cat /proc/cpuinfo"),
        ("mount", "txt", "mount"),
        ("ipa", "txt", "ip -o -4 a"),
        ("netdev", "txt", "cat /proc/net/dev"),
        ("ceph_conf", "txt", "cat /etc/ceph/ceph.conf"),
        ("uptime", "txt", "cat /proc/uptime"),
        ("dmesg", "txt", "cat /var/log/dmesg"),
        ("netstat", "txt", "netstat -nap")
    ]

    def collect_node(self, path, host):
        path = 'hosts/' + host + '/'
        for path_off, frmt, cmd in self.node_commands:
            self.ssh2emit(host, path + path_off, frmt, cmd)
        self.collect_interfaces_info(path, host)

    def collect_interfaces_info(self, path, host):
        interfaces = {}
        for is_phy, dev in self.get_host_interfaces(host):
            interface = {'dev': dev, 'is_phy': is_phy}
            interfaces[dev] = interface

            if not is_phy:
                continue

            speed = None
            ok, data = check_output_ssh(host, self.opts, "ethtool " + dev)
            if ok:
                for line in data.split("\n"):
                    if 'Speed:' in line:
                        speed = line.split(":")[1].strip()
                    if 'Duplex:' in line:
                        interface['duplex'] = line.split(":")[1].strip() == 'Full'

            ok, data = check_output_ssh(host, self.opts, "iwconfig " + dev)
            if ok and 'Bit Rate=' in data:
                br1 = data.split('Bit Rate=')[1]
                if 'Tx-Power=' in br1:
                    speed = br1.split('Tx-Power=')[0]

            if speed is not None:
                mults = {
                    'Kb/s': 125,
                    'Mb/s': 125000,
                    'Gb/s': 125000000,
                }
                for name, mult in mults.items():
                    if name in speed:
                        speed = int(speed.replace(name, '')) * mult
                        break
                else:
                    logger.warning("Node %s - can't transform %s interface speed %r to Bps",
                                   host, dev, speed)

                if isinstance(speed, int):
                    interface['speed'] = speed
                else:
                    interface['speed_s'] = speed

        self.emit(path + 'interfaces', 'json', True, json.dumps(interfaces))


class NodeResourseUsageCollector(Collector):
    name = 'resource'
    run_alone = True

    def collect_node(self, path, host):
        cpath = '{0}/rusage/{1}/{2}-disk'.format(path, host, int(time.time()))
        self.ssh2emit(host, cpath, "txt", "cat /proc/diskstats")

        cpath = '{0}/rusage/{1}/{2}-net'.format(path, host, int(time.time()))
        self.ssh2emit(host, cpath, "txt", "cat /proc/net/dev")


performance_monitor_code_templ = """#!/bin/bash
function monitor_ceph_io() {
    date
    for i in $(seq __runtime__) ; do
        grep -E '__devs_grep_pattern__' /proc/diskstats
        sleep 1
    done
}

function monitor_ceph_cpu() {
    date
    for i in $(seq __runtime__) ; do
        ps -p __osd_pids__ -o pid,cputime | grep -v PID
        sleep 1
    done
}

function monitor_ceph_net() {
    date
    for i in $(seq __runtime__) ; do
        grep -E '__net_grep_pattern__' /proc/net/dev | tr -d ':'
        sleep 1
    done
}

monitor_ceph_io > __io_file__ &
monitor_ceph_cpu > __cpu_file__ &
monitor_ceph_net > __net_file__

wait
"""


class CephPerformanceCollector(Collector):
    name = 'performance'

    def __init__(self, *args, **kwargs):
        super(CephPerformanceCollector, self).__init__(*args, **kwargs)
        self.run_uuid = str(uuid.uuid1())
        self.io_file = "/tmp/io_{0}.txt".format(self.run_uuid)
        self.cpu_file = "/tmp/cpu_{0}.txt".format(self.run_uuid)
        self.net_file = "/tmp/net_{0}.txt".format(self.run_uuid)
        self.remote_file = "/tmp/{0}.sh".format(self.run_uuid)

    def start_performance_monitoring(self, path, host, osd_devs):
        local_file = "/tmp/{0}_{1}.sh".format(host, self.run_uuid)

        osd_devs = map(os.path.basename, osd_devs)
        uniq_devs = " ".join(set(osd_devs))
        grep_re = "|".join(map("\\b{0}\\b".format, set(osd_devs)))

        ok, osd_pids = check_output_ssh(host, self.opts, "ps aux")
        assert ok
        osd_pid_list = []
        for process in osd_pids.strip().split("\n"):
            vals = process.split()
            if 'ceph-osd' in vals[10]:
                osd_pid_list.append(vals[1])

        all_devs = []
        phy_devs = []

        for is_phy, dev in self.get_host_interfaces(host):
            all_devs.append(dev)
            if is_phy:
                phy_devs.append(dev)

        all_devs_re = "|".join(map("\\b{0}\\b".format, all_devs))

        performance_monitor_code = performance_monitor_code_templ \
            .replace('__runtime__', str(self.opts.performance_collect_seconds)) \
            .replace('__io_file__', self.io_file) \
            .replace('__net_file__', self.net_file) \
            .replace('__cpu_file__', self.cpu_file) \
            .replace('__uniq_osd_devs__', uniq_devs) \
            .replace('__devs_grep_pattern__', grep_re) \
            .replace('__osd_pids__', ",".join(osd_pid_list)) \
            .replace('__net_grep_pattern__', all_devs_re)

        open(local_file, "w").write(performance_monitor_code)
        try:
            scp_cmd = "scp {0} {1} {2}:{3}".format(SSH_OPTS, local_file,
                                                   host, self.remote_file)

            ok, _ = check_output(scp_cmd)
            assert ok
        finally:
            os.unlink(local_file)

        start_cmd = 'screen -S ceph_monitor -d -m bash ' + self.remote_file
        check_output_ssh(host, self.opts, start_cmd, no_retry=True)

    def collect_performance_data(self, path, host):
        all_files = {'io': self.io_file,
                     'cpu': self.cpu_file,
                     'net': self.net_file}

        for tp, fname in all_files.items():
            self.ssh2emit(host,
                          "{0}/perf_monitoring/{1}/{2}".format(path, host, tp),
                          "txt", 'cat ' + fname)
        check_output_ssh(host, self.opts, "rm -f " +
                         " ".join(all_files.values() + [self.remote_file]),
                         no_retry=True)


class CephDiscovery(object):
    def __init__(self, opts):
        self.opts = opts
        self.ceph_cmd = "ceph -c {0.conf} -k {0.key} --format json ".format(self.opts)

    def discover(self):
        ok, res = check_output(self.ceph_cmd + "mon_status")
        assert ok
        for node in json.loads(res)['monmap']['mons']:
            yield 'monitor', str(node['name']), {'name': node['name']}

        ok, res = check_output(self.ceph_cmd + "osd tree")
        assert ok
        for node in json.loads(res)['nodes']:
            if node['type'] == 'host':
                for osd_id in node['children']:
                    yield 'osd', str(node['name']), {'osd_id': osd_id}


def save_results_th_func(opts, res_q, out_folder):
    try:
        while True:
            val = res_q.get()
            if val is None:
                break

            ok, path, frmt, out = val

            while '//' in path:
                path.replace('//', '/')

            while path.startswith('/'):
                path = path[1:]

            while path.endswith('/'):
                path = path[:-1]

            fname = os.path.join(out_folder, path + '.' + frmt)
            dr = os.path.dirname(fname)

            if not os.path.exists(dr):
                os.makedirs(dr)

            if frmt == 'bin':
                open(fname, "wb").write(out)
            elif frmt == 'json':
                if not opts.no_pretty_json:
                    try:
                        out = json.dumps(json.loads(out), indent=4, sort_keys=True)
                    except Exception:
                        pass
                open(fname, "w").write(out)
            else:
                open(fname, "w").write(out)
    except Exception:
        logger.exception("In save_results_th_func thread")


def discover_nodes(opts):
    discovers = [
        CephDiscovery
    ]

    nodes = collections.defaultdict(
        lambda: collections.defaultdict(lambda: []))

    for discover_cls in discovers:
        discover = discover_cls(opts)
        for role, node, args in discover.discover():
            nodes[role][node].append(args)
            nodes['node'][node] = [{}]
    return nodes


def run_all(opts, run_q):
    def pool_thread():
        val = run_q.get()
        while val is not None:
            try:
                func, path, node, kwargs = val
                func(path, node, **kwargs)
            except Exception:
                logger.exception("In worker thread")
            val = run_q.get()

    running_threads = []
    for i in range(opts.pool_size):
        th = threading.Thread(target=pool_thread)
        th.daemon = True
        th.start()
        running_threads.append(th)
        run_q.put(None)

    while True:
        time.sleep(0.01)
        if all(not th.is_alive() for th in running_threads):
            break


def setup_loggers(default_level=logging.INFO, log_fname=None):
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(default_level)

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    colored_formatter = logging.Formatter(log_format, datefmt="%H:%M:%S")

    sh.setFormatter(colored_formatter)
    logger.addHandler(sh)

    if log_fname is not None:
        fh = logging.FileHandler(log_fname)
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format, datefmt="%H:%M:%S")
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)


ALL_COLLECTORS = [
    CephDataCollector,
    NodeCollector,
    NodeResourseUsageCollector,
    CephPerformanceCollector
]


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("-c", "--conf",
                   default="/etc/ceph/ceph.conf",
                   help="Ceph cluster config file")

    p.add_argument("-k", "--key",
                   default="/etc/ceph/ceph.client.admin.keyring",
                   help="Ceph cluster key file")

    p.add_argument("--username",
                   default="ansible",
                   help="Username to login on nodes with.")

    p.add_argument("--ssh-private-key",
                   default="~/.ssh/id_rsa",
                   help="Path to SSH private key to use.")

    p.add_argument("-l", "--log-level",
                   choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                   default="INFO",
                   help="Colsole log level")

    p.add_argument("-p", "--pool-size",
                   default=16, type=int,
                   help="Worker pool size")

    p.add_argument("-t", "--ssh-conn-timeout",
                   default=60, type=int,
                   help="SSH connection timeout")

    p.add_argument("-s", "--performance-collect-seconds",
                   default=60, type=int, metavar="SEC",
                   help="Collect performance stats for SEC seconds")

    p.add_argument("-u", "--usage-collect-interval",
                   default=60, type=int, metavar="SEC",
                   help="Collect usage for at lease SEC seconds")

    p.add_argument("-d", "--disable", default=[],
                   nargs='*', help="Disable collect pattern")

    p.add_argument("--ceph-log-max-lines", default=1000,
                   type=int, help="Max lines from osd/mon log")

    p.add_argument("--collectors", default="ceph,node,resource,performance",
                   help="Coma separated list of collectors" +
                   "select from : " +
                   ",".join(coll.name for coll in ALL_COLLECTORS))

    p.add_argument("--max-pg-dump-count", default=2 ** 15,
                   type=int,
                   help="maximum PG count to by dumped with 'pg dump' cmd")

    p.add_argument("-o", "--result", default=None, help="Result file")

    p.add_argument("-n", "--dont-remove-unpacked", default=False,
                   action="store_true",
                   help="Keep unpacked data")

    p.add_argument("-j", "--no-pretty-json", default=False,
                   action="store_true",
                   help="Don't prettify json data")

    return p.parse_args(argv[1:])


logger_ready = False


def prun(runs, thcount):
    res_q = Queue.Queue()
    input_q = Queue.Queue()
    map(input_q.put, enumerate(runs))

    def worker():
        while True:
            try:
                pos, (func, args, kwargs) = input_q.get(False)
            except Queue.Empty:
                return

            try:
                res_q.put((pos, True, func(*args, **kwargs)))
            except Exception as exc:
                res_q.put((pos, False, exc))

    ths = [threading.Thread(target=worker) for i in range(thcount)]

    for th in ths:
        th.daemon = True
        th.start()

    for th in ths:
        th.join()

    results = []
    while not res_q.empty():
        results.append(res_q.get())

    return [(ok, val) for _, ok, val in sorted(results)]


def pmap(func, data, thcount):
    return prun([(func, [val], {}) for val in data], thcount)


def get_sshable_hosts(hosts, thcount=32):
    cmd = "ssh {0} ".format(SSH_OPTS)

    def check_host(host):
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            return None
        ok, out = check_output(cmd + host + ' pwd')
        if ok:
            return host
        return None

    results = pmap(check_host, hosts, thcount=thcount)
    return [res for ok, res in results if ok and res is not None]


def main(argv):
    if not check_output('which ceph')[0]:
        logger.error("No 'ceph' command available. Run this script from node, which has ceph access")
        return

    # TODO: Logs from down OSD
    opts = parse_args(argv)
    res_q = Queue.Queue()
    run_q = Queue.Queue()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out_folder = os.tempnam()

    os.makedirs(out_folder)

    setup_loggers(getattr(logging, opts.log_level),
                  os.path.join(out_folder, "log.txt"))

    global logger_ready
    logger_ready = True

    global SSH_OPTS
    SSH_OPTS = SSH_OPTS.format(opts.ssh_conn_timeout, opts.username,
                               opts.ssh_private_key)

    collector_settings = CollectSettings()
    map(collector_settings.disable, opts.disable)

    allowed_collectors = opts.collectors.split(',')
    collectors = []

    if CephDataCollector.name in allowed_collectors:
        ceph_collector = CephDataCollector(opts, collector_settings, res_q)
        collectors.append(ceph_collector)
    else:
        ceph_collector = None

    if NodeCollector.name in allowed_collectors:
        node_collector = NodeCollector(opts, collector_settings, res_q)
        collectors.append(node_collector)
    else:
        node_collector = None

    if NodeResourseUsageCollector.name in allowed_collectors:
        node_resource_collector = NodeResourseUsageCollector(opts, collector_settings, res_q)
    else:
        node_resource_collector = None

    if CephPerformanceCollector.name in allowed_collectors:
        if CephDataCollector.name not in allowed_collectors:
            logger.error("Can't collect performance info without ceph info collected")
            exit(1)
        else:
            ceph_performance_collector = CephPerformanceCollector(opts, collector_settings, res_q)
    else:
        ceph_performance_collector = None

    nodes = discover_nodes(opts)
    nodes['master'][None] = [{}]

    for role, nodes_with_args in nodes.items():
        if role == 'node':
            continue
        logger.info("Found %s hosts with role %s", len(nodes_with_args), role)
        logger.info("Found %s services with role %s",
                    sum(map(len, nodes_with_args.values())), role)

    logger.info("Found %s hosts total", len(nodes['node']))

    good_hosts = set(get_sshable_hosts(nodes['node'].keys()))
    bad_hosts = set(nodes['node'].keys()) - good_hosts

    if len(bad_hosts) != 0:
        logger.warning("Next hosts aren't awailable over ssh and would be skipped: %s",
                       ",".join(bad_hosts))

    res_q.put((True, "bad_hosts", 'json', json.dumps(list(bad_hosts))))

    new_nodes = collections.defaultdict(lambda: {})

    for role, role_objs in nodes.items():
        if role == 'master':
            new_nodes[role] = role_objs
        else:
            for node, args in role_objs.items():
                if node in good_hosts:
                    new_nodes[role][node] = args

    nodes = new_nodes

    # collect data at the beginning
    if node_resource_collector is not None:
        for node, _ in nodes['node'].items():
            run_q.put((node_resource_collector.collect_node, "", node, {}))

    for role, nodes_with_args in nodes.items():
        for collector in collectors:
            if hasattr(collector, 'collect_' + role):
                coll_func = getattr(collector, 'collect_' + role)
                for node, kwargs_list in nodes_with_args.items():
                    for kwargs in kwargs_list:
                        run_q.put((coll_func, "", node, kwargs))

    save_results_thread = threading.Thread(target=save_results_th_func,
                                           args=(opts, res_q, out_folder))
    save_results_thread.daemon = True
    save_results_thread.start()

    t1 = time.time()
    try:
        run_all(opts, run_q)

        # collect data at the end
        if node_resource_collector is not None:
            dt = opts.usage_collect_interval - (time.time() - t1)
            if dt > 0:
                logger.info("Will wait for {0} seconds for usage data collection".format(int(dt)))
                for i in range(int(dt / 0.1)):
                    time.sleep(0.1)
            logger.info("Start final usage collection")
            for node, _ in nodes['node'].items():
                run_q.put((node_resource_collector.collect_node, "", node, {}))
            run_all(opts, run_q)

        if ceph_performance_collector is not None:
            logger.info("Start performace monitoring.")
            with ceph_collector.osd_devs_lock:
                osd_devs = ceph_collector.osd_devs.copy()

            per_node = collections.defaultdict(lambda: [])
            for node, data_dev, j_dev in osd_devs.values():
                per_node[node].extend((data_dev, j_dev))

            # start monitoring
            for node, data in per_node.items():
                run_q.put((ceph_performance_collector.start_performance_monitoring,
                          "", node, {'osd_devs': data}))
            run_all(opts, run_q)

            dt = opts.performance_collect_seconds
            logger.info("Will wait for {0} seconds for performance data collection".format(int(dt)))
            for i in range(int(dt / 0.1)):
                time.sleep(0.1)

            # collect results
            for node, data in per_node.items():
                run_q.put((ceph_performance_collector.collect_performance_data,
                          "", node, {}))
            run_all(opts, run_q)
    except Exception:
        logger.exception("When collecting data:")
    finally:
        res_q.put(None)
        # wait till all data collected
        save_results_thread.join()

    if opts.result is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out_file = os.tempnam() + ".tar.gz"
    else:
        out_file = opts.result

    check_output("cd {0} ; tar -zcvf {1} *".format(out_folder, out_file))
    logger.info("Result saved into %r", out_file)
    if opts.log_level in ('WARNING', 'ERROR', "CRITICAL"):
        print "Result saved into %r" % (out_file,)

    if not opts.dont_remove_unpacked:
        shutil.rmtree(out_folder)
    else:
        logger.info("Temporary folder %r", out_folder)
        if opts.log_level in ('WARNING', 'ERROR', "CRITICAL"):
            print "Temporary folder %r" % (out_folder,)


if __name__ == "__main__":
    try:
        exit(main(sys.argv))
    except Exception:
        if logger_ready:
            logger.exception("During main")
        else:
            raise
