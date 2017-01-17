# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import os.path
import datetime
import functools
import collections

from ipaddr import IPNetwork, IPAddress
from hw_info import get_hw_info, ssize2b
from multiprocessing import Pool as MPExecutorPool


class CephOSD(object):
    def __init__(self):
        self.id = None
        self.status = None
        self.host = None
        self.daemon_runs = None
        self.pg_count = None
        self.config = None
        self.pgs = {}
        self.data_stor_stats = None
        self.j_stor_stats = None


class CephMonitor(object):
    def __init__(self):
        self.name = None
        self.status = None
        self.host = None
        self.role = None


class Pool(object):
    def __init__(self):
        self.id = None
        self.name = None


class NetworkAdapter(object):
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.is_phy = None
        self.speed = None
        self.duplex = None
        self.perf_stats = None
        self.perf_delta = None
        self.perf_stats_curr = None


class Disk(object):
    def __init__(self, dev):
        self.dev = dev
        self.perf_stats = None
        self.perf_delta = None


class Host(object):
    def __init__(self, name):
        self.name = name
        self.cluster_net = None
        self.public_net = None
        self.net_adapters = {}
        self.disks = {}
        self.uptime = None
        self.perf_monitoring = None
        self.rusage_stats = None


class TabulaRasa(object):
    def __init__(self, **attrs):
        self.__dict__.update(attrs)

    def get(self, name, default=None):
        try:
            return self.__dict__.get(name, default)
        except KeyError:
            raise AttributeError(name)

    def __contains__(self, name):
        return name in self.__dict__


class DevLoadLog(object):
    def __init__(self, name, start_timstamp):
        self.name = name
        self.values = []
        self.start_timstamp = start_timstamp


diskstat_fields = [
    "major",
    "minor",
    "device",
    "reads_completed",
    "reads_merged",
    "sectors_read",
    "read_time",
    "writes_completed",
    "writes_merged",
    "sectors_written",
    "write_time",
    "in_progress_io",
    "io_time",
    "weighted_io_time"]

DiskStats = collections.namedtuple("DiskStats", diskstat_fields)


netstat_fields = ("rbytes rpackets rerrs rdrop rfifo rframe rcompressed" +
                  " rmulticast sbytes spackets serrs sdrop sfifo scolls" +
                  " scarrier scompressed").split()

NetStats = collections.namedtuple("NetStats", netstat_fields)


def parse_netdev(netdev):
    info = {}
    for line in netdev.strip().split("\n")[2:]:
        adapter, data = line.split(":")
        adapter = adapter.strip()
        assert adapter not in info
        info[adapter] = NetStats(*map(int, data.split()))

    return info


def parse_diskstats(diskstats):
    info = {}
    for line in diskstats.strip().split("\n"):
        data = line.split()
        data_i = map(int, data[:2]) + [data[2]] + map(int, data[3:])
        info[data[2].strip()] = DiskStats(*data_i)
    return info


def find(lst, check, default=None):
    for obj in lst:
        if check(obj):
            return obj
    return default


def load_performance_log_file(str_data, fields, skip=0, field_types=None):
    # first line - collection start time
    lines = iter(str_data.split("\n"))

    # Mon Sep  7 21:08:26 UTC 2015
    sdate = datetime.datetime.strptime(next(lines), "%a %b %d %H:%M:%S UTC %Y")
    timestamp = (sdate - datetime.datetime(1970, 1, 1)).total_seconds()

    per_dev = {}

    if field_types is None:
        fied_tr = functools.partial(map, float)
    else:
        def fied_tr(data):
            return [func(val) for func, val in zip(field_types, data)]

    for line in lines:
        line = line.strip()
        if line == '':
            continue

        items = line.split()[skip:]
        dev = items[0]

        if dev not in per_dev:
            per_dev[dev] = obj = DevLoadLog(dev, timestamp)
        else:
            obj = per_dev[items[0]]

        obj.values.append(TabulaRasa(**dict(zip(fields, fied_tr(items[1:])))))

    return per_dev


class CephCluster(object):
    def __init__(self, jstorage, storage):
        self.osds = []
        self.mons = []
        self.pools = {}
        self.hosts = {}

        self.osd_tree = {}
        self.osd_tree_root_id = None
        self.report_collected_at_local = None
        self.report_collected_at_gmt = None

        self.cluster_net = None
        self.public_net = None

        self.storage = storage
        self.jstorage = jstorage
        self.settings = TabulaRasa()

    def get_alive_osd(self):
        # try to find alive osd
        for osd in self.osds:
            if osd.status == 'up' and osd.daemon_runs:
                return osd
        return None

    def load(self):
        self.load_osd_tree()
        self.load_PG_distribution()
        self.load_osds()
        self.load_cluster_networks()
        self.load_pools()
        self.load_monitors()
        self.load_hosts()

        for host in self.hosts.values():
            host.rusage_stats = self.get_rusage_stats(host.name)
            host.perf_monitoring = self.get_perf_monitoring(host.name)

        self.fill_io_devices_usage_stats()
        self.fill_net_devices_usage_stats()

        data = self.storage.get('master/collected_at')
        assert data is not None
        self.report_collected_at_local, \
            self.report_collected_at_gmt, _ = data.strip().split("\n")

        mstorage = self.jstorage.master

        self.overall_status = mstorage.status['health']['overall_status']
        self.health_summary = mstorage.status['health']['summary']
        self.num_pgs = mstorage.status['pgmap']['num_pgs']

        self.bytes_used = mstorage.status['pgmap']["bytes_used"]
        self.bytes_total = mstorage.status['pgmap']["bytes_total"]
        self.bytes_avail = mstorage.status['pgmap']["bytes_avail"]
        self.data_bytes = mstorage.status['pgmap']["data_bytes"]
        self.write_bytes_sec = mstorage.status['pgmap'].get("write_bytes_sec", 0)
        self.op_per_sec = mstorage.status['pgmap'].get("op_per_sec", 0)

        for osd in self.osds:
            if osd.status == 'up':
                self.settings.__dict__.update(osd.config)
                break
        else:
            self.settings = None

        self.pgmap_stat = mstorage.status['pgmap']

    def fill_net_devices_usage_stats(self):
        for host in self.hosts.values():

            perf_m = host.perf_monitoring
            if perf_m is not None:
                perf_m = perf_m.get('net')

            nets = [host.cluster_net, host.public_net] + \
                [adapter for adapter in host.net_adapters.values()
                 if adapter.is_phy]

            for net in nets:
                if net is None:
                    continue

                if perf_m is not None and net.name in perf_m:
                    sd = perf_m[net.name].values[0]
                    ed = perf_m[net.name].values[-1]
                    dtime = len(perf_m[net.name].values) - 1
                elif host.rusage_stats is not None and 'net' in host.rusage_stats:
                    start_time, start_data = host.rusage_stats['net'][0]
                    end_time, end_data = host.rusage_stats['net'][-1]
                    dtime = end_time - start_time
                    sd = start_data[net.name]
                    ed = end_data[net.name]
                else:
                    continue

                net.perf_stats_curr = TabulaRasa()
                net.perf_stats_curr.sbytes = (ed.sbytes - sd.sbytes) / dtime
                net.perf_stats_curr.rbytes = (ed.rbytes - sd.rbytes) / dtime
                net.perf_stats_curr.spackets = (ed.spackets - sd.spackets) / dtime
                net.perf_stats_curr.rpackets = (ed.rpackets - sd.rpackets) / dtime

    def fill_io_devices_usage_stats(self):
        for osd in self.osds:
            host = self.hosts[osd.host]

            perf_m = host.perf_monitoring
            if perf_m is not None:
                perf_m = perf_m.get('io')

            if 'disk' in host.rusage_stats:
                start_time, start_data = host.rusage_stats['disk'][0]
                end_time, end_data = host.rusage_stats['disk'][-1]
                rusage_dtime = end_time - start_time
            else:
                dtime = end_data = start_data = None

            for dev_stat in (osd.data_stor_stats, osd.j_stor_stats):
                if dev_stat is None:
                    continue

                dev = os.path.basename(dev_stat.root_dev)
                if perf_m is not None and dev in perf_m:
                    sd = perf_m[dev].values[0]
                    ed = perf_m[dev].values[-1]
                    dtime = len(perf_m[dev].values) - 1
                elif start_data is not None and dev in start_data:
                    dtime = rusage_dtime
                    sd = start_data[dev]
                    ed = end_data[dev]
                else:
                    continue

                dev_stat.read_bytes_curr = (ed.sectors_read - sd.sectors_read) * 512 / dtime
                dev_stat.write_bytes_curr = (ed.sectors_written - sd.sectors_written) * 512 / dtime
                dev_stat.read_iops_curr = (ed.reads_completed - sd.reads_completed) / dtime
                dev_stat.write_iops_curr = (ed.writes_completed - sd.writes_completed) / dtime
                dev_stat.io_time_curr = 0.001 * (ed.io_time - sd.io_time) / dtime
                dev_stat.w_io_time_curr = 0.001 * (ed.weighted_io_time - sd.weighted_io_time) / dtime

                # derived stats
                dev_stat.iops_curr = dev_stat.read_iops_curr + dev_stat.write_iops_curr
                dev_stat.queue_depth_curr = dev_stat.w_io_time_curr

                if dev_stat.iops_curr > 1E-5:
                    dev_stat.lat_curr = dev_stat.w_io_time_curr / dev_stat.iops_curr
                else:
                    dev_stat.lat_curr = 0

                dev_stat.read_bytes_uptime = (sd.sectors_read) * 512 / host.uptime
                dev_stat.write_bytes_uptime = (sd.sectors_written) * 512 / host.uptime
                dev_stat.read_iops_uptime = sd.reads_completed / host.uptime
                dev_stat.write_iops_uptime = (sd.writes_completed) / host.uptime
                dev_stat.io_time_uptime = 0.001 * sd.io_time / host.uptime
                dev_stat.w_io_time_uptime = 0.001 * sd.weighted_io_time / host.uptime

    def load_cluster_networks(self):
        self.cluster_net = None
        self.public_net = None

        osd = self.get_alive_osd()
        if osd is not None:
            cluster_net_str = osd.config.get('cluster_network')
            if cluster_net_str is not None and cluster_net_str != "":
                self.cluster_net = IPNetwork(cluster_net_str)

            public_net_str = osd.config.get('public_network', None)
            if public_net_str is not None and public_net_str != "":
                self.public_net = IPNetwork(public_net_str)

    def load_osd_tree(self):
        nodes = self.jstorage.master.osd_tree['nodes']

        self.osd_tree_root_id = nodes[0]['id']
        self.osd_tree = dict((node['id'], node) for node in nodes)

        # set backtrack links
        def fill_parent(obj, parent_id=None):
            obj['parent'] = parent_id
            if 'children' in obj:
                for child_id in obj['children']:
                    fill_parent(self.osd_tree[child_id], obj['id'])

        # set hosts
        def fill_host(obj, host=None):
            obj['host'] = host
            if obj['type'] == 'host':
                host = obj['name']
            if 'children' in obj:
                for child_id in obj['children']:
                    fill_host(self.osd_tree[child_id], host)

        fill_parent(self.osd_tree[self.osd_tree_root_id])
        fill_host(self.osd_tree[self.osd_tree_root_id])

    def find_host_for_node(self, node):
        cnode = node
        while cnode['type'] != 'host':
            if cnode['parent'] is None:
                raise IndexError("Can't found host for " + str(node['id']))
            cnode = self.osd_tree[cnode['parent']]
        return cnode

    def load_osds(self):
        for node in self.osd_tree.values():
            if node['type'] != 'osd':
                continue

            osd = CephOSD()
            self.osds.append(osd)
            osd.__dict__.update(node)
            osd.host = node['host']

            try:
                osd_data = getattr(self.jstorage.osd, str(node['id']))
                osd.data_stor_stats = TabulaRasa(**osd_data.data.stats)
                osd.j_stor_stats = TabulaRasa(**osd_data.journal.stats)
            except AttributeError:
                osd.data_stor_stats = None
                osd.j_stor_stats = None

            osd.osd_perf = find(self.jstorage.master.osd_perf["osd_perf_infos"],
                                lambda x: x['id'] == osd.id)["perf_stats"]

            data = self.storage.get('osd/{0}/osd_daemons'.format(osd.id))
            if data is None:
                osd.daemon_runs = None
            else:
                for line in data.split("\n"):
                    if 'ceph-osd' in line and '-i {0}'.format(osd.id) in line:
                        osd.daemon_runs = True
                        break
                else:
                    osd.daemon_runs = False

            data = self.storage.get('osd/{0}/osd_daemons'.format(osd.id))

            if self.sum_per_osd is not None:
                osd.pg_count = self.sum_per_osd[osd.id]
            else:
                osd.pg_count = None

            osd.config = self.jstorage.osd.get("{0}/config".format(osd.id))

        self.osds.sort(key=lambda x: x.id)

    def load_pools(self):
        self.pools = {}

        for pool_part in self.jstorage.master.osd_dump['pools']:
            pool = Pool()
            pool.id = pool_part['pool']
            pool.name = pool_part['pool_name']
            pool.__dict__.update(pool_part)
            self.pools[int(pool.id)] = pool

        for pool_part in self.jstorage.master.rados_df['pools']:
            if 'categories' not in pool_part:
                self.pools[int(pool_part['id'])].__dict__.update(pool_part)
            else:
                assert len(pool_part['categories']) == 1
                cat = pool_part['categories'][0].copy()
                del cat['name']
                self.pools[int(pool_part['id'])].__dict__.update(cat)

    def load_monitors(self):
        srv_health = self.jstorage.master.status['health']['health']['health_services']
        assert len(srv_health) == 1
        for srv in srv_health[0]['mons']:
            mon = CephMonitor()
            mon.health = srv["health"]
            mon.name = srv["name"]
            mon.host = srv["name"]
            mon.kb_avail = srv["kb_avail"]
            mon.avail_percent = srv["avail_percent"]
            self.mons.append(mon)

    def get_node_net_stats(self, host_name):
        return parse_netdev(self.storage.get('hosts/{0}/netdev'.format(host_name)))

    def get_node_disk_stats(self, host_name):
        return parse_netdev(self.storage.get('hosts/{0}/diskstats'.format(host_name)))

    def load_PG_distribution(self):
        try:
            pg_dump = self.jstorage.master.pg_dump
        except AttributeError:
            pg_dump = None

        self.osd_pool_pg_2d = collections.defaultdict(lambda: collections.Counter())
        self.sum_per_pool = collections.Counter()
        self.sum_per_osd = collections.Counter()
        pool_id2name = dict((dt['poolnum'], dt['poolname'])
                            for dt in self.jstorage.master.osd_lspools)

        if pg_dump is None:
            pg_re = re.compile(r"(?P<pool_id>[0-9a-f]+)\.(?P<pg_id>[0-9a-f]+)_head$")
            for node in self.osd_tree.values():
                if node['type'] == 'osd':
                    osd_num = node['id']
                    storage_ls = self.storage.get('osd/{0}/storage_ls'.format(osd_num))
                    for pg in storage_ls.split():
                        mobj = pg_re.match(pg)
                        if mobj is None:
                            continue

                        pool_name = pool_id2name[int(mobj.group('pool_id'))]
                        self.osd_pool_pg_2d[osd_num][pool_name] += 1
                        self.sum_per_pool[pool_name] += 1
                        self.sum_per_osd[osd_num] += 1
        else:
            for pg in pg_dump['pg_stats']:
                pool = int(pg['pgid'].split('.', 1)[0])
                for osd_num in pg['acting']:
                    pool_name = pool_id2name[pool]
                    self.osd_pool_pg_2d[osd_num][pool_name] += 1
                    self.sum_per_pool[pool_name] += 1
                    self.sum_per_osd[osd_num] += 1

    def parse_meminfo(self, meminfo):
        info = {}
        for line in meminfo.split("\n"):
            line = line.strip()
            if line == '':
                continue
            name, data = line.split(":", 1)
            data = data.strip()
            if " " in data:
                data = data.replace(" ", "")
                assert data[-1] == 'B'
                val = ssize2b(data[:-1])
            else:
                val = int(data)
            info[name] = val
        return info

    def load_hosts(self):
        for host_name in self.storage.hosts[2]:
            stor_node = self.storage.get("hosts/" + host_name, expected_format=None)

            host = Host(host_name)
            self.hosts[host.name] = host

            lshw_xml = stor_node.get('lshw', expected_format='xml')

            if lshw_xml is None:
                host.hw_info = None
            else:
                try:
                    host.hw_info = get_hw_info(lshw_xml)
                except:
                    host.hw_info = None

            info = self.parse_meminfo(stor_node.get('meminfo'))
            host.mem_total = info['MemTotal']
            host.mem_free = info['MemFree']
            host.swap_total = info['SwapTotal']
            host.swap_free = info['SwapFree']
            loadavg = stor_node.get('loadavg')

            host.load_5m = None if loadavg is None else float(loadavg.strip().split()[1])

            ipa = self.storage.get('hosts/%s/ipa' % host.name)
            ip_rr_s = r"\d+:\s+(?P<adapter>.*?)\s+inet\s+(?P<ip>\d+\.\d+\.\d+\.\d+)/(?P<size>\d+)"

            info = collections.defaultdict(lambda: [])
            for line in ipa.split("\n"):
                match = re.match(ip_rr_s, line)
                if match is not None:
                    info[match.group('adapter')].append(
                        (IPAddress(match.group('ip')), int(match.group('size'))))

            for adapter, ips_with_sizes in info.items():
                for ip, sz in ips_with_sizes:
                    if self.public_net is not None and ip in self.public_net:
                        host.public_net = NetworkAdapter(adapter, ip)

                    if self.cluster_net is not None and ip in self.cluster_net:
                        host.cluster_net = NetworkAdapter(adapter, ip)

            interfaces = getattr(self.jstorage.hosts, host_name).interfaces
            for name, adapter_dct in interfaces.items():
                adapter_dct = adapter_dct.copy()

                dev = adapter_dct.pop('dev')
                adapter = NetworkAdapter(dev, None)
                adapter.__dict__.update(adapter_dct)
                host.net_adapters[dev] = adapter

            net_stats = self.get_node_net_stats(host.name)
            perf_adapters = [host.cluster_net, host.public_net] + list(host.net_adapters.values())

            for net in perf_adapters:
                if net is not None and net.name is not None:
                    net.perf_stats = net_stats.get(net.name)

            host.uptime = float(stor_node.get('uptime').split()[0])

    def get_rusage_stats(self, host_name):
        stats = collections.defaultdict(lambda: [])
        host_stats = self.storage.get("rusage/" + host_name, expected_format=None)
        if host_stats is None:
            return {}

        for stat_name in host_stats:
            collect_time, stat_type = stat_name.split("-")

            if stat_type == 'disk':
                stat = parse_diskstats(host_stats.get(stat_name))
            elif stat_type == 'net':
                stat = parse_netdev(host_stats.get(stat_name))
            else:
                raise ValueError("Unknown stat type - {!r}".format(stat_type))

            stats[stat_type].append([int(collect_time), stat])

        for stat_list in stats.values():
            stat_list.sort()

        return stats

    def get_perf_monitoring(self, host_name):
        path = "perf_monitoring/" + host_name + '/'

        res = {}

        for name, fields, skip in [('io', diskstat_fields[3:], 2),
                                   ('net', netstat_fields, 0)]:
            stats_s = self.storage.get(path + name)
            if stats_s is not None:
                res[name] = load_performance_log_file(stats_s, fields, skip)

        # mp_pool = MPExecutorPool(processes=2)
        # futures = {}
        # futures[name] = mp_pool.apply_async(load_performance_log_file,
        #                                     [stats_s, fields, skip])
        # for name, future in futures.items():
        #     res[name] = future.get()

        def to_seconds(val):
            if '-' in val:
                days, rest = val.split('-')
            else:
                days, rest = 0, val

            h, m, s = map(int, rest.split(":"))
            return int(days) * 24 * 3600 + h * 3600 + m * 60 + s

        stats_s = self.storage.get(path + 'cpu')
        if stats_s is not None:
            res['cpu'] = load_performance_log_file(stats_s, ['pid', 'cpu'], 0,
                                                   [to_seconds])

        return res
