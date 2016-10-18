How to collect data

* ssh to any node, which has ceph access (controller/compute/osd)
* Run 'curl https://raw.githubusercontent.com/Mirantis/ceph-monitoring/master/ceph_monitoring/collect_info.py | python'
* Run 'python visualize_cluster.py TAR_GZ_FILE  -w -g -o OUT_FOLDER
* Open OUT_FOLDER/index.html in browser
