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
import xml.etree.ElementTree as ET


def get_data(rr, data):
    match_res = re.search("(?ims)" + rr, data)
    return match_res.group(0)


SMAP = dict(k=1024, m=1024 ** 2, g=1024 ** 3, t=1024 ** 4)


def ssize2b(ssize):
    try:
        if isinstance(ssize, (int, long)):
            return ssize

        ssize = ssize.lower()
        if ssize[-1] in SMAP:
            return int(ssize[:-1]) * SMAP[ssize[-1]]
        return int(ssize)
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Unknow size format {0!r}".format(ssize))


RSMAP = [('K', 1024),
         ('M', 1024 ** 2),
         ('G', 1024 ** 3),
         ('T', 1024 ** 4)]

RSMAP2 = [('K', 1000),
          ('M', 1000 ** 2),
          ('G', 1000 ** 3),
          ('T', 1000 ** 4)]


def b2ssize(size, add_i=True, base=1024):
    assert base in (1024, 1000)
    if size < base:
        if size == 0:
            return "0"
        elif size < 1:
            return "{0:.2e}".format(size)
        elif isinstance(size, float):
            return "{0:.1f}".format(size)
        else:
            return str(size)

    i = 'i' if (add_i and base == 1024) else ''

    for name, scale in (RSMAP if base == 1024 else RSMAP2):
        if size < base * scale:
            if size % scale == 0:
                val = size // scale
                return "{0} {1}{2}".format(val, name, i)
            else:
                return "{0:.1f} {1}{2}".format(float(size) / scale, name, i)

    return "{0} {1}{2}".format(size // scale, name, i)


class HWInfo(object):
    def __init__(self):
        self.hostname = None
        self.cores = []

        # /dev/... devices
        self.disks_info = {}

        # real disks on raid controller
        self.disks_raw_info = {}

        # name => (speed, is_full_diplex, ip_addresses)
        self.net_info = {}

        self.ram_size = 0
        self.sys_name = None
        self.mb = None
        self.raw = None

        self.storage_controllers = []

    def get_HDD_count(self):
        # SATA HDD COUNT, SAS 10k HDD COUNT, SAS SSD count, PCI-E SSD count
        return []

    def get_summary(self):
        cores = sum(count for _, count in self.cores)
        disks = sum(size for _, size in self.disks_info.values())

        return {'cores': cores,
                'ram': self.ram_size,
                'storage': disks,
                'disk_count': len(self.disks_info)}

    def __str__(self):
        res = []

        summ = self.get_summary()
        summary = "Simmary: {cores} cores, {ram}B RAM, {disk}B storage"
        res.append(summary.format(cores=summ['cores'],
                                  ram=b2ssize(summ['ram']),
                                  disk=b2ssize(summ['storage'])))
        res.append(str(self.sys_name))
        if self.mb is not None:
            res.append("Motherboard: " + self.mb)

        if self.ram_size == 0:
            res.append("RAM: Failed to get RAM size")
        else:
            res.append("RAM " + b2ssize(self.ram_size) + "B")

        if self.cores == []:
            res.append("CPU cores: Failed to get CPU info")
        else:
            res.append("CPU cores:")
            for name, count in self.cores:
                if count > 1:
                    res.append("    {0} * {1}".format(count, name))
                else:
                    res.append("    " + name)

        if self.storage_controllers != []:
            res.append("Disk controllers:")
            for descr in self.storage_controllers:
                res.append("    " + descr)

        if self.disks_info != {}:
            res.append("Storage devices:")
            for dev, (model, size) in sorted(self.disks_info.items()):
                ssize = b2ssize(size) + "B"
                res.append("    {0} {1} {2}".format(dev, ssize, model))
        else:
            res.append("Storage devices's: Failed to get info")

        if self.disks_raw_info != {}:
            res.append("Disks devices:")
            for dev, descr in sorted(self.disks_raw_info.items()):
                res.append("    {0} {1}".format(dev, descr))
        else:
            res.append("Disks devices's: Failed to get info")

        if self.net_info != {}:
            res.append("Net adapters:")
            for name, (speed, dtype, _) in self.net_info.items():
                res.append("    {0} {2} duplex={1}".format(name, dtype, speed))
        else:
            res.append("Net adapters: Failed to get net info")

        return str(self.hostname) + ":\n" + "\n".join("    " + i for i in res)


def get_hw_info(lshw_out):
    res = HWInfo()

    res.raw = lshw_out
    lshw_et = ET.fromstring(lshw_out)

    try:
        res.hostname = lshw_et.find("node").attrib['id']
    except:
        pass

    try:
        res.sys_name = (lshw_et.find("node/vendor").text + " " +
                        lshw_et.find("node/product").text)
        res.sys_name = res.sys_name.replace("(To be filled by O.E.M.)", "")
        res.sys_name = res.sys_name.replace("(To be Filled by O.E.M.)", "")
    except:
        pass

    core = lshw_et.find("node/node[@id='core']")
    if core is None:
        return

    try:
        res.mb = " ".join(core.find(node).text
                          for node in ['vendor', 'product', 'version'])
    except:
        pass

    for cpu in core.findall("node[@class='processor']"):
        try:
            model = cpu.find('product').text
            threads_node = cpu.find("configuration/setting[@id='threads']")
            if threads_node is None:
                threads = 1
            else:
                threads = int(threads_node.attrib['value'])
            res.cores.append((model, threads))
        except:
            pass

    res.ram_size = 0
    for mem_node in core.findall(".//node[@class='memory']"):
        descr = mem_node.find('description')
        try:
            if descr is not None and descr.text == 'System Memory':
                mem_sz = mem_node.find('size')
                if mem_sz is None:
                    for slot_node in mem_node.find("node[@class='memory']"):
                        slot_sz = slot_node.find('size')
                        if slot_sz is not None:
                            assert slot_sz.attrib['units'] == 'bytes'
                            res.ram_size += int(slot_sz.text)
                else:
                    assert mem_sz.attrib['units'] == 'bytes'
                    res.ram_size += int(mem_sz.text)
        except:
            pass

    for net in core.findall(".//node[@class='network']"):
        try:
            link = net.find("configuration/setting[@id='link']")
            if link.attrib['value'] == 'yes':
                name = net.find("logicalname").text
                speed_node = net.find("configuration/setting[@id='speed']")

                if speed_node is None:
                    speed = None
                else:
                    speed = speed_node.attrib['value']

                dup_node = net.find("configuration/setting[@id='duplex']")
                if dup_node is None:
                    dup = None
                else:
                    dup = dup_node.attrib['value']

                res.net_info[name] = (speed, dup, [])
        except:
            pass

    for controller in core.findall(".//node[@class='storage']"):
        try:
            description = getattr(controller.find("description"), 'text', "")
            product = getattr(controller.find("product"), 'text', "")
            vendor = getattr(controller.find("vendor"), 'text', "")
            dev = getattr(controller.find("logicalname"), 'text', "")
            if dev != "":
                res.storage_controllers.append(
                    "{0}: {1} {2} {3}".format(dev, description,
                                              vendor, product))
            else:
                res.storage_controllers.append(
                    "{0} {1} {2}".format(description,
                                         vendor, product))
        except:
            pass

    for disk in core.findall(".//node[@class='disk']"):
        try:
            lname_node = disk.find('logicalname')
            if lname_node is not None:
                dev = lname_node.text.split('/')[-1]

                if dev == "" or dev[-1].isdigit():
                    continue

                sz_node = disk.find('size')
                assert sz_node.attrib['units'] == 'bytes'
                sz = int(sz_node.text)
                res.disks_info[dev] = ('', sz)
            else:
                description = disk.find('description').text
                product = disk.find('product').text
                vendor = disk.find('vendor').text
                version = disk.find('version').text
                serial = disk.find('serial').text

                full_descr = "{0} {1} {2} {3} {4}".format(
                    description, product, vendor, version, serial)

                businfo = disk.find('businfo').text
                res.disks_raw_info[businfo] = full_descr
        except:
            pass

    return res
