import time
import json
import requests

from requests.auth import HTTPBasicAuth
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class onos():
    def __init__(self,ip,username,password):
        self.ip = ip
        self.username = username
        self.password = password
    
    def get_data(self,path):
        url = 'http://'+self.ip+':8181/onos/v1'+path
        data = requests.get(url, auth=HTTPBasicAuth(self.username,self.password)).text
        return json.loads(data)
    
    def get_devices(self):
        data = []
        tmp = self.get_data('/devices')
        for device in tmp['devices']:
            data.append(device['id'])
        return data

    class device():
        def __init__(self,id, outer_instance):
            self.id = id
            self.outer_instance = outer_instance
        
        def get_port_statistic(self):
            data = self.outer_instance.get_data('/statistics/ports/'+self.id)
            return data
        
        def get_table_statistic(self):
            data = self.outer_instance.get_data('/statistics/flows/tables/'+self.id)
            return data

class prometheusCollector():

    def collect(self):

        self.metric = {
        'packetsReceived': GaugeMetricFamily('onos_device_packets_received','packets received per seconds', labels=["node","port"]),
        'packetsSent': GaugeMetricFamily('onos_device_packets_sent','packets sent per seconds', labels=["node","port"]),
        'bytesReceived': GaugeMetricFamily('onos_device_bytes_received','bytes received per seconds', labels=["node","port"]),
        'bytesSent': GaugeMetricFamily('onos_device_bytes_sent','bytes sends per seconds', labels=["node","port"]),
        'packetsRxDropped': GaugeMetricFamily('packetsRxDropped','received packet drop  per seconds', labels=["node","port"]),
        'packetsTxDropped': GaugeMetricFamily('packetsTxDropped','sent packet drop sent per seconds', labels=["node","port"]),
        'packetsRxErrors': GaugeMetricFamily('packetsRxErrors',' received packet errors  per seconds', labels=["node","port"]),
        'packetsTxErrors': GaugeMetricFamily('packetsTxErrors','sent packet errors per seconds', labels=["node","port"]),
        'packetsMatched': GaugeMetricFamily('onos_table_packets_matched','packets matched per table', labels=["node","table"]),
        'packetsLookedUp': GaugeMetricFamily('onos_table_packets_lookedUp','packet lookups per table', labels=["node","table"]),

        }

        onos_config = json.loads(open("onos-config.json","r").read())
        onos_instance = onos(onos_config["ipaddress"],onos_config["username"],onos_config["password"])
        device_data = onos_instance.get_devices()
        
        for line in device_data:

            device = onos_instance.device(line,onos_instance)
            data = device.get_port_statistic()["statistics"][0]

            port_length = len(data['ports'])
            for number in range(0,port_length):
                self.metric['packetsReceived'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["packetsReceived"])
                self.metric['packetsSent'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["packetsSent"])
                self.metric['bytesReceived'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["bytesReceived"])
                self.metric['bytesSent'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["bytesSent"])
                self.metric['packetsRxDropped'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["packetsRxDropped"])
                self.metric['packetsTxDropped'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["packetsTxDropped"])
                self.metric['packetsRxErrors'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["packetsRxErrors"])
                self.metric['packetsTxErrors'].add_metric([data["device"],str(data["ports"][number]['port'])], data["ports"][number]["packetsTxErrors"])
            
            tables = device.get_table_statistic()["statistics"][0]
            tables_length = len(tables['table'])
            for number in range(0, tables_length):
                if tables["table"][number]["activeEntries"] > 0:
                    self.metric['packetsMatched'].add_metric([tables["device"],str(tables["table"][number]['tableId'])], tables["table"][number]["packetsMatched"])
                    self.metric['packetsLookedUp'].add_metric([tables["device"],str(tables["table"][number]['tableId'])], tables["table"][number]["packetsLookedUp"])

            

        for metric in self.metric.values():
            yield metric

if __name__ == "__main__":

    REGISTRY.register(prometheusCollector())
    start_http_server(9091)
    
    while True:
        time.sleep(1)
    

