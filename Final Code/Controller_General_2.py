#!/usr/bin/python

import json
import requests
import time
import threading
import thread
#from numpy import inf

# master dictionary of switches with key = dpid
global switch_dict
switch_dict = {}
eth_type = 0x800
ip_dscp = 40

# All the spcifications related to the topology are stored in Topo_Specs
from Topo_Specs_General_3 import switch_port_mac_dict as mac_dict, dpid_switch_number as sw_num, switch_port_mat, \
    switch_number_dpid as sw_dpid, switch_dict, paths as path_list, cost_matrix as cm, eth_tg2, eth_tg3, eth_client, eth_ms1, eth_ms2

#from Dijkstra2 import test_Dijkstra as tD
from threading import Timer
from collections import defaultdict

# REST API  url to use in pushing flows
flow_pusher_url = "http://127.0.0.1:8080/wm/staticentrypusher/json"


def stats_collector():
    # REST API call to get switch-details
    req_get_switch_details = requests.get('http://127.0.0.1:8080/wm/core/controller/switches/json')
    # parse json
    switch_details_json = json.loads(req_get_switch_details.text)
    # store switch details for each switch
    for switch in switch_details_json:
        switch_dict[switch['switchDPID']] = {'ports': {}}
        # get port details
        port_details_req = requests.get('http://127.0.0.1:8080/wm/core/switch/' + switch['switchDPID'] + '/port/json')
        port_details_json = json.loads(port_details_req.text)
        port_dict = {}
        # print (port_details_json['port_reply'][0]['port'][0])
        # store details for each port
        for port in port_details_json['port_reply'][0]['port']:
            port_dict[port['port_number']] = {'bandwidth_util': 0, 'time': int(time.time()),
                                              'tx': int(port['transmit_bytes']), 'rx': int(port['receive_bytes']),
                                              'link_util': 0}
            switch_dict[switch['switchDPID']]['ports'].update(port_dict)


    # computes bandwidth utilization and updates the value of 'bandwodth_utilization' in the switch_dict for every port of every switch
    def computeStats():

        dest_mac = switch_dict

        curr_time = int(time.time())
        print "----------------------------------------------------"
        for switch in switch_dict:
            # store_port stats
            #print "-----------"
            # print "switch_dpid:", switch
            port_stats = {}
            # get current_port_stats
            port_details_req = requests.get('http://127.0.0.1:8080/wm/core/switch/' + switch + '/port/json')
            port_details_json = json.loads(port_details_req.text)
            for port in port_details_json['port_reply'][0]['port']:
                port_stats[port['port_number']] = {'tx': int(port['transmit_bytes']), 'rx': int(port['receive_bytes'])}

            ports = switch_dict[switch]['ports']
            for port in ports:
                prev_tx = ports[port]['tx']
                prev_rx = ports[port]['rx']
                # calculate bw
                bw = float(port_stats[port]['tx'] + port_stats[port]['rx'] - prev_tx - prev_rx) / (
                    curr_time - ports[port]['time'])

                bw = float(bw / 1000 / 125)
                bw = int((bw * 100) + 0.5) / 100.0
                if float(bw) >= 7:
                    l_util = float(10*(bw - 7) / bw)
                else:
                    l_util = 0
                ports[port]['bandwidth_util'] = bw
                ports[port]['tx'] = port_stats[port]['tx']
                ports[port]['rx'] = port_stats[port]['rx']
                ports[port]['time'] = curr_time
                ports[port]['link_util'] = l_util
                if port != 'local' and ports[port]['bandwidth_util']!=0:    
                    print "switch\t", sw_num[switch], "\tport id\t\t", port, "\tbandwidth_util\t", ports[port]['bandwidth_util'], "\tMbits/sec"


    #run the stats manager every 1 second. Use threading class for running it as a daemon process
    class StatsManager(threading.Thread):
        def __init__(self, delay):
            threading.Thread.__init__(self)
            self.delay = delay

        def run(self):
            count = 0
            while True:
                time.sleep(self.delay)
                #print(count)
                computeStats()
                count += 1

    stat_collector_thread = StatsManager(1)
    stat_collector_thread.daemon = True
    stat_collector_thread.start()

    while True:
        time.sleep(1)


# A class to manage all the works, related to routes
class RouteManagement():
    # Give every flow a new name based on a counter
    flow_counter = 0
    cost_matrix = cm

    # Calculate the best Dijkstra path
    def DijkstraPath(self, path_pair):
        path = tD(path_pair[0], path_pair[1])
        return path

    def findPathPairs(self, n_switches):
        pairs = []
        for i in range(n_switches):
            for j in range(i + 1, n_switches):
                pairs.append([i, j])
        return pairs

    # Create flows compatible with the REST API
    def createFlow(self, path):
        flows = defaultdict(list)
        dst = len(path) - 1
        for i in range(dst):
            # Egress port and Ingress port are stored in the switch_port_mat
            # Using an already stored data in switch_port_mat
            forward_flow_egress_port = switch_port_mat[path[i]][path[i + 1]]
            backward_flow_egress_port = switch_port_mat[path[i + 1]][path[i]]
            # Forward flow = flow along the path
            # IP DSCP and ETH Type allow us to categorize flows as qos flows
            forward_flow1 = '{"switch":"' + sw_dpid[path[i]] + '","name":"' + str(
                self.flow_counter) + '", "eth_dst":"'+eth_client+'", "eth_type":"'+eth_type+'", "ip_dscp":"40", "actions":"output=' + forward_flow_egress_port + '"}'
            self.flow_counter += 1
            backward_flow1 = '{"switch":"' + sw_dpid[path[i + 1]] + '","name":"' + str(
                self.flow_counter) + '", "eth_dst":"'+eth_ms1+'", "eth_type":"'+eth_type+'", "ip_dscp":"40", "actions":"output=' + backward_flow_egress_port + '"}'
            self.flow_counter += 1
            flows[sw_dpid[path[i]]].append(forward_flow1)
            flows[sw_dpid[path[i + 1]]].append(backward_flow1)
        return flows

    # Include the endpoints - Client, Multimedia Servers, Traffic Generators in the flows
    # Needed because the endpoints are not part of route calculation, hence their flows would be mostly fixed
    def createEndpointFlow(self, src, dst):
        # Adding the flows for endpoints separately to keep them out of routing graph
        flows = defaultdict(list)
        # Flow for Multimedia server1
        flow1 = '{"switch":"'+sw_dpid[src]+'","name":"'+self.flow_counter+'", "eth_dst":"'+eth_ms1+'", "eth_type":"'+eth_type+'", "ip_dscp":"'+ip_dscp+'", "actions":"output=1"}'
        flows[sw_dpid[src]].append(flow1)
        self.flow_counter += 1
        # Leaving Multimedia server2 out of QoS categorization
        # Flow for client
        flow1 = '{"switch": "'+sw_dpid[dst]+'", "name": "'+self.flow_counter+'", "eth_dst": "'+eth_client+'", "eth_type":"'+eth_type+'", "ip_dscp":"'+ip_dscp+'", "actions": "output=1"}'
        flows[sw_dpid[dst]].append(flow1)
        self.flow_counter += 1
        return flows

    # Push the flows via the REST API
    def flowPusher(self, flows):
        # Asumming flows to be a list of flow dictionaries, each dictionary having two keys, switch name and flow string
        for switch in flows.keys():
            for flow in flows[switch]:
                #print flow
                r = requests.post(flow_pusher_url, data=flow)
                # Push flow here
        return r

s   # Calculate minimum cost routes, where cost = modified cost
    def LARAC(self, switch_dict, src, dst):  # Dmax = length of longest path i.e. maximum number of hops
        min_cost_path = []
        min_cost = 10000
        Dmax = 6
        for path in path_list[sw_dpid[src]][sw_dpid[dst]]:
            cost = 0
            for i in range(len(path) - 1):
                egress_sw = sw_dpid[path[i]]
                ingress_sw = sw_dpid[path[i + 1]]
                cost += switch_dict[egress_sw]['ports'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]][
                    'link_util']
                cost += 1
            if cost < min_cost and (len(path) - 1) < Dmax:
                min_cost = cost
                min_cost_path = path
        if len(min_cost_path):
            return min_cost_path
        else:
            return "No path found"


if __name__ == "__main__":
    # stuff only to execute when this module is directly run
    route_manager = RouteManagement()
    thread.start_new_thread(stats_collector, ())
    time.sleep(5)
    endpoint_flows = route_manager.createEndpointFlow(0, 3)
    r = route_manager.flowPusher((endpoint_flows))
    print r
    while (1):
        fcpath = route_manager.LARAC(switch_dict, 0, 3)
        print fcpath
        flows = route_manager.createFlow(fcpath)
        r = route_manager.flowPusher(flows)
        time.sleep(3)
