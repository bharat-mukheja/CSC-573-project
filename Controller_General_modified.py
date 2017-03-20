#!/usr/bin/python

import json
import requests
import time
import threading
import thread
from numpy import inf

# master dictionary of switches with key = dpid
global switch_dict
switch_dict = {}

#All the spcifications related to the topology are stored in Topo_Specs
from Topo_Specs_General_2 import switch_port_mac_dict as mac_dict,dpid_switch_number as sw_num,switch_port_mat, switch_number_dpid as sw_dpid, switch_dict, paths as path_list, cost_matrix as cm, eth_tg2, eth_tg3


from Dijkstra2 import test_Dijkstra as tD
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
                                              'tx': int(port['transmit_bytes']), 'rx': int(port['receive_bytes']),'link_util':0}
            switch_dict[switch['switchDPID']]['ports'].update(port_dict)

    # get mac and ip for every port for each switch
    #r = requests.get('http://127.0.0.1:8080/wm/device/')
    #data = json.loads(r.text)
    #devices = data['devices']
    #for entity in devices:
        # print(entity)
    #    dpid = entity['attachmentPoint'][0]['switch']
    #    port = entity['attachmentPoint'][0]['port']
    #    ip = entity['ipv4'][0]
    #    mac = entity['mac'][0]
    #    print(dpid, port, ip, mac)
        # store
   #     d = {'mac': mac, 'ip': ip}
   #     switch_dict[dpid]['ports'][port].update(d)


    # computes bandwidth utilization and updates the value of 'bandwodth_utilization' in the switch_dict for every port of every switch
    def computeStats():

        dest_mac = switch_dict

        curr_time = int(time.time())
        for switch in switch_dict:
            # store_port stats
            #print "-----------"
            #print "switch_dpid:", switch
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
                # print(int(port_stats[port]['tx']))
                # print(int(port_stats[port]['rx']))
                # print(curr_time)

                bw = float(bw / 1000 / 125)
                bw = int((bw * 100) + 0.5) / 100.0
                if int(bw) > 6:
                    l_util = float((bw - 7)/bw)
                else:
                    l_util = 0
                ports[port]['bandwidth_util'] = bw
                ports[port]['tx'] = port_stats[port]['tx']
                ports[port]['rx'] = port_stats[port]['rx']
                ports[port]['time'] = curr_time
                ports[port]['link_util'] = l_util
                # print "port id\t", port, "\tbandwidth_util\t", bw, "\tMbits/sec"
                #print "port id\t\t", port, "\tbandwidth_util\t", ports[port]['bandwidth_util'], "\tMbits/sec"
            #print "-----------"
        #print switch_dict

    class StatsManager(threading.Thread):

        def __init__(self, delay):
            threading.Thread.__init__(self)
            self.delay = delay

        def run(self):
            count = 0
            while True:
                time.sleep(self.delay)
                print(count)
                computeStats()
                count += 1

    stat_collector_thread = StatsManager(1)
    stat_collector_thread.daemon = True
    stat_collector_thread.start()

    while True:
        time.sleep(1)


# A class to manage all the works, related to routes
class RouteManagement():
    #Give every flow a new name based on a counter
    flow_counter = 0 
    cost_matrix = cm
    t = None    #set a thread handle outside the function scope to be able to control thread from outside
    
    #Calculate the best Dijkstra path
    def DijkstraPath(self, path_pair):
        path = tD(path_pair[0],path_pair[1])
        return path

    def findPathPairs(self, n_switches):
        pairs = []
        for i in range(n_switches):
            for j in range(i+1,n_switches):
                pairs.append([i,j])
        return pairs

    #Create Dijkstra flows compatible with the REST API
    def createDijkstraFlows(self, djkpairs):
        flows = defaultdict(list)
        for pair in djkpairs:
            path = self.DijkstraPath(pair)
            dst = len(path) - 1
            for i in range(dst):
                # Egress port and Ingress port are stored in the switch_port_mat
                # Using an already stored data in switch_port_mat
                forward_flow_egress_port = switch_port_mat[path[i]][path[i + 1]]
                backward_flow_egress_port = switch_port_mat[path[i + 1]][path[i]]
                # Forward flow = flow along the path
                # IP DSCP and ETH Type allow us to categorize flows as qos flows
                forward_flow1 = '{"switch":"' + sw_dpid[path[i]] + '","name":"' + str(
                    self.flow_counter) + '", "eth_dst":"fa:16:3e:00:14:17", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=' + forward_flow_egress_port + ':0"}'
                self.flow_counter += 1
                forward_flow2 = '{"switch":"' + sw_dpid[path[i]] + '","name":"' + str(
                    self.flow_counter) + '", "eth_dst":"fa:16:3e:00:14:17", "actions":"enqueue=' + forward_flow_egress_port + ':1"}'
                self.flow_counter += 1
                # print "forward flow: src=",path[i],", dst=",path[i+1],", flow = ",forward_flow1
                # print "forward flow: src=",path[i],", dst=",path[i+1],", flow = ",forward_flow2
                # Backward flow = flow along reverse of the path, needed to setup a two-way connection
                backward_flow1 = '{"switch":"' + sw_dpid[path[i + 1]] + '","name":"' + str(
                    self.flow_counter) + '", "eth_dst":"fa:16:3e:00:1b:7c", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=' + backward_flow_egress_port + ':0"}'
                self.flow_counter += 1
                backward_flow2 = '{"switch":"' + sw_dpid[path[i + 1]] + '","name":"' + str(
                    self.flow_counter) + '", "eth_dst":"fa:16:3e:00:1b:7c", "actions":"enqueue=' + backward_flow_egress_port + ':1"}'
                self.flow_counter += 1
                backward_flow3 = '{"switch":"' + sw_dpid[path[i + 1]] + '","name":"' + str(
                    self.flow_counter) + '", "eth_dst":"fa:16:3e:00:45:76", "actions":"enqueue=' + backward_flow_egress_port + ':1"}'
                self.flow_counter += 1
                # print "bckward flow: src=", path[i+1], ", dst=", path[i], ", flow = ", backward_flow1
                # print "bckward flow: src=", path[i+1], ", dst=", path[i], ", flow = ", backward_flow2
                # print "bckward flow: src=", path[i+1], ", dst=", path[i], ", flow = ", backward_flow3
                flows[sw_dpid[path[i]]].append(forward_flow1)
                flows[sw_dpid[path[i]]].append(forward_flow2)
                flows[sw_dpid[path[i + 1]]].append(backward_flow1)
                flows[sw_dpid[path[i + 1]]].append(backward_flow2)
                flows[sw_dpid[path[i + 1]]].append(backward_flow3)
        return flows

    #Create flows compatible with the REST API 
    def createFlow(self, path):
        flows = defaultdict(list)
        dst = len(path)-1
        for i in range(dst):
            #Egress port and Ingress port are stored in the switch_port_mat
            #Using an already stored data in switch_port_mat
            forward_flow_egress_port = switch_port_mat[path[i]][path[i+1]]
            backward_flow_egress_port = switch_port_mat[path[i+1]][path[i]]
            #Forward flow = flow along the path
            #IP DSCP and ETH Type allow us to categorize flows as qos flows
            forward_flow1 = '{"switch":"'+sw_dpid[path[i]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"fa:16:3e:00:14:17", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue='+forward_flow_egress_port+':1"}'
            self.flow_counter += 1
            #forward_flow2 = '{"switch":"' + sw_dpid[path[i]] + '","name":"' + str(self.flow_counter) + '", "eth_dst":"fa:16:3e:00:14:17", "actions":"enqueue=' + forward_flow_egress_port + ':0"}'
            #self.flow_counter += 1
            #print "forward flow: src=",path[i],", dst=",path[i+1],", flow = ",forward_flow1
            #print "forward flow: src=",path[i],", dst=",path[i+1],", flow = ",forward_flow2
            #Backward flow = flow along reverse of the path, needed to setup a two-way connection
            backward_flow1 = '{"switch":"'+sw_dpid[path[i+1]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"fa:16:3e:00:1b:7c", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue='+backward_flow_egress_port+':1"}'
            self.flow_counter += 1
            #backward_flow2 = '{"switch":"'+sw_dpid[path[i+1]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"fa:16:3e:00:1b:7c", "actions":"enqueue='+backward_flow_egress_port+':0"}'
            #self.flow_counter += 1
            #backward_flow3 = '{"switch":"'+sw_dpid[path[i+1]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"fa:16:3e:00:45:76", "actions":"enqueue='+backward_flow_egress_port+':0"}'
            #self.flow_counter += 1
            #print "bckward flow: src=", path[i+1], ", dst=", path[i], ", flow = ", backward_flow1
            #print "bckward flow: src=", path[i+1], ", dst=", path[i], ", flow = ", backward_flow2
            #print "bckward flow: src=", path[i+1], ", dst=", path[i], ", flow = ", backward_flow3
            flows[sw_dpid[path[i]]].append(forward_flow1)
            #flows[sw_dpid[path[i]]].append(forward_flow2)
            flows[sw_dpid[path[i+1]]].append(backward_flow1)
            #flows[sw_dpid[path[i+1]]].append(backward_flow2)
            #flows[sw_dpid[path[i+1]]].append(backward_flow3)
        return flows

    # Include the endpoints - Client, Multimedia Servers, Traffic Generators in the flows
    def createEndpointFlow(self,src,dst):
        #Adding the flows for endpoints separately to keep them out of routing graph
        flows = defaultdict(list)
        #Flow for Multimedia server1
        flow1 = '{"switch":"00:00:72:40:b2:ac:47:4b","name":"0", "eth_dst":"72:40:b2:ac:47:4b", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=1:1"}'
        #flow2 = '{"switch":"00:00:72:40:b2:ac:47:4b","name":"1", "eth_dst":"72:40:b2:ac:47:4b", "actions":"enqueue=1:0"}'
        flows[sw_dpid[src]].append(flow1)
        #flows[sw_dpid[src]].append(flow2)
        #Leaving Multimedia server2 out of QoS categorization
        #flow = '{"switch":"00:00:72:40:b2:ac:47:4b","name":"2", "eth_dst":"fa:16:3e:00:45:76", "actions":"enqueue=2:0"}'
        #flows[sw_dpid[src]].append(flow)
        #Flow for client
        flow1 = '{"switch": "00:00:1e:96:5d:c9:b0:49", "name": "3", "eth_dst": "fa:16:3e:00:14:17", "eth_type":"0x0800", "ip_dscp":"40", "actions": "enqueue=2:1"}'
        #flow2 = '{"switch": "00:00:1e:96:5d:c9:b0:49", "name": "4", "eth_dst": "fa:16:3e:00:14:17", "actions":"enqueue=2:0"}'
        flows[sw_dpid[dst]].append(flow1)
        #flows[sw_dpid[dst]].append(flow2)
        self.flow_counter+=5
        return flows

    #Push the flows via the REST API
    def flowPusher(self, flows):
        #Asumming flows to be a list of flow dictionaries, each dictionary having two keys, switch name and flow string
        for switch in flows.keys():
            for flow in flows[switch]:
                print flow
                r = requests.post(flow_pusher_url, data = flow)
                #Push flow here
        return r

    def setQoSCrossTraffic(self, src, dst):
        flows = defaultdict(list)
        forward_flow1 = '{"switch":"'+sw_dpid[src]+'","name":"5", "eth_src":"'+eth_tg3+'", "eth_dst":"'+eth_tg2+'", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=3:1"}'
        bckward_flow1 = '{"switch":"'+sw_dpid[src]+'","name":"6", "eth_src":"'+eth_tg2+'", "eth_dst":"'+eth_tg3+'", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=2:1"}'
        flows[sw_dpid[src]].append(forward_flow1)
        flows[sw_dpid[src]].append(bckward_flow1)
        forward_flow2 = '{"switch":"'+sw_dpid[dst]+'","name":"7", "eth_src":"'+eth_tg2+'", "eth_dst":"'+eth_tg3+'", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=2:1"}'
        bckward_flow2 = '{"switch":"'+sw_dpid[dst]+'","name":"8", "eth_src":"'+eth_tg3+'", "eth_dst":"'+eth_tg2+'", "eth_type":"0x0800", "ip_dscp":"40", "actions":"enqueue=4:1"}'
        flows[sw_dpid[src]].append(forward_flow2)
        flows[sw_dpid[src]].append(bckward_flow2)
        self.flow_counter+=4
        r = self.flowPusher(flows)
        return r


    #Create Route Management a running process
    def program_run(self,interval):
        global t
        t = Timer(interval, self.program_run, args=[interval])
        t.daemon = True
        t.start()
        route_manager = RouteManagement()
        route_manager.createCostMatrix()
        route_manager.calculatePath()
    
    #A handle to stop the route manager when from outside
    def program_stop(self):
        self.t.cancel()
        print("Stopping Route Manager ...")

    #Calculate minimum cost routes, where cost = modified cost
    def FCpath(self,switch_dict, src, dst): #Dmax = length of longest path i.e. maximum number of hops
        #print switch_dict
        min_cost_path = []
        min_cost  = 10000
        Dmax=6
        for path in path_list[sw_dpid[src]][sw_dpid[dst]]:
            cost = 0
            for i in range(len(path) - 1):
                egress_sw = sw_dpid[path[i]]
                ingress_sw = sw_dpid[path[i + 1]]
                #print path
                #print switch_dict
                #print "egress_sw=", egress_sw, "ingress_sw=", ingress_sw, "port = " ,switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]
                #try:
                cost += switch_dict[egress_sw]['ports'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]]['link_util']
                #except:
                cost += 1
            #print path
            #print "cost=",cost
            #print "min cost=",min_cost
            if cost< min_cost and (len(path)-1)< Dmax:
                min_cost = cost
                min_cost_path = path
        if len(min_cost_path):
            return min_cost_path
        else:
            return "No path found"


if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    route_manager = RouteManagement()
    thread.start_new_thread(stats_collector,())
    time.sleep(5)
    endpoint_flows = route_manager.createEndpointFlow(0, 3)
    r = route_manager.flowPusher((endpoint_flows))
    print r
    r = route_manager.setQoSCrossTraffic(1,4)
    print r
    while(1):
        #print switch_dict
        #print "Yes"
        fcpath = route_manager.FCpath(switch_dict,0,3)
        print fcpath
        flows = route_manager.createFlow(fcpath)
        #print flows
        r = route_manager.flowPusher(flows)
        print r
        time.sleep(2)
