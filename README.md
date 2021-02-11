# Monitoring system for an SDN with Prometheus and Grafana
Setting up [prometheus](https://prometheus.io/) to monitor an SDN Controller ([ONOS](https://opennetworking.org/onos/)) and its topology.

### Set up a topology on mininet
You can create your topology on mininet following the example file in this repository.

To run it\
`$ sudo mn --custom path-to-file/topology.py --topo mytopo`

Set all the switches to use OpenFlow protocol\
`$ sudo ovs-vsctl set bridge <switch-name> protocols=OpenFlow14,OpenFlow13`

Download and Run the Controller on the local machine, e.g.\
`$ sudo ./onos-2.0.0/apache-karaf-4.2.2/bin/start`\
`$ sudo ./onos-2.0.0/apache-karaf-4.2.2/bin/client`\
and inside the onos cli run this final command\
`app activate org.onosproject.fwd org.onosproject.openflow`

Now connect all the switches to the controller\
`$ sudo ovs-vsctl set-controller <switch-name> tcp:localhost`\
and set the secure mode `$ sudo ovs-vsctl set-fail-mode <switch-name> secure`

By running `$ sudo ovs-vsctl show` you can see the topology.\
And at `http://localhost:8181/onos/ui` you can access the ONOS's UI.

### Set up Prometheus
[Download Prometheus](https://prometheus.io/download/) in your preferred environment.\
e.g. `wget https://github.com/prometheus/prometheus/releases/download/v2.24.0/prometheus-2.24.0.linux-amd64.tar.gz`

For linux:\
`$ cd download-folder`\
`$ tar -xzf prometheus-<version>.linux-amd64.tar.gz`

To run it:\
`$ cd download-folder/prometheus-<version>.linux-amd64/`\
`$ ./prometheus`

Once it is running, you can connect to `localhost:9090` to see the dashboard.

### Set up the exporters
#### Node Exporter
To have general information about the heath of the machine get the node_exporter. E.g.\
`wget https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz`\
unzip it: `tar -xzf node_exp..[TAB]`\
`cd node_exp..[TAB]` and run it\
`./node_exporter`

Then, in the prometheus folder, modify `prometheus.yml` and add a new job for the node_exporter (port 9100). Check the file in this repo for a full example.
```
- job_name: 'node-exporter'
    static_configs:
    - targets: ['localhost:9100']
```

Run: `kill -s HUP $(pidof prometheus)` to refresh prometheus without any scraping downtime.

#### ONOS Exporter
Set the `onos-config.json` with the required information to access the ONOS controller.

Install the requirements of the onos-exporter with\
`$ pip install requirements`\
then run `python3 exporter.py`

Add another job to the prometheus configuration file (port 9091).
```
- job_name: 'onos-exporter'
    static_configs:
    - targets: ['localhost:9091']
```
Run again `kill -s HUP $(pidof prometheus)`.
This onos exporter was build from the great work of [Zufar Dhiyaulhaq](https://github.com/zufardhiyaulhaq/onos-prometheus-exporter).

### Set up Grafana
Download and run grafana: `./bin/grafana-server`
On the grafana UI: 
- add rometheus as data source
- import the dashboard in this repo.
 

#### References
Great introduction to set-up prometheus with node exporter [here](https://www.youtube.com/watch?v=4WWW2ZLEg74).
