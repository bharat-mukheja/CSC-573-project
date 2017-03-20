from numpy import inf

global switch_port_mac_dict

sw1 = '00:00:72:40:b2:ac:47:4b'
sw2 = '00:00:da:f5:a7:c4:3a:49'
sw3 = '00:00:56:40:08:c1:cd:43'
sw4 = '00:00:1e:96:5d:c9:b0:49'
sw5 = '00:00:1a:9b:f5:c7:10:47'
sw6 = '00:00:4a:ff:6e:89:e4:42'

eth_tg3 = 'fa:16:3e:00:28:f5'
eth_tg2 = 'fa:16:3e:00:45:f4'

switch_port_mac_dict = {sw1: {'1': 'fa:16:3e:00:fb:38', '2': 'fa:16:3e:00:1e:bc', '3': 'fa:16:3e:00:64:08','4': 'fa:16:3e:00:39:41'}, sw2: {'1': 'fa:16:3e:00:5b:ab', '2': 'fa:16:3e:00:6e:b8', '3': 'fa:16:3e:00:5d:bc','4': 'fa:16:3e:00:75:ec'}, sw3: {'1': 'fa:16:3e:00:64:33', '2': 'fa:16:3e:00:22:04', '3': 'fa:16:3e:00:70:e2','4': 'fa:16:3e:00:19:2a'}, sw4: {'1': 'fa:16:3e:00:11:7c', '2': 'fa:16:3e:00:67:dc', '3': 'fa:16:3e:00:62:a4'}, sw5: {'1': 'fa:16:3e:00:74:73', '2': 'fa:16:3e:00:52:b3', '3': 'fa:16:3e:00:38:e2','4': 'fa:16:3e:00:29:c7'}, sw6: {'1': 'fa:16:3e:00:35:26', '2': 'fa:16:3e:00:53:21', '3': 'fa:16:3e:00:26:e9','4': 'fa:16:3e:00:72:a2'}}

global switch_port_mat
global switch_number_dpid
dpid_switch_number = {sw1: 0, sw2: 1, sw3: 2, sw4: 3, sw5: 4, sw6: 5}
switch_number_dpid = {0: sw1, 1: sw2, 2: sw3, 3: sw4, 4: sw5, 5: sw6}
switch_port_mat = [[0, '4', 0, 0, 0,'3'],['4', 0,'1',0,'3', 0],[0,'1', 0,'2', 0,'4'],[0, 0,'3', 0, '1', 0],[0,'2', 0,'1', 0,'3'],['4', 0,'3', 0,'2', 0]]

cost_matrix = [[inf, 1, inf, inf, inf,1],[1, inf,1,inf,1, inf],[inf,1, inf,1, inf,1],[inf, inf,1, inf,1, inf],[inf,1, inf,1, inf,1],[1, inf,1, inf,1, inf]]

# dictionary of switches with key = dpid
global switch_dict
switch_dict = {}

global paths
paths = {sw1: {
    sw4: [[0, 1, 2, 3], [0, 1, 4, 3], [0, 5, 4, 3], [0, 1, 2, 5, 4, 3], [0, 5, 4, 1, 2, 3], [0, 5, 2, 1, 4, 3],
          [0, 1, 4, 5, 2, 3], [0, 5, 2, 3]]}}
