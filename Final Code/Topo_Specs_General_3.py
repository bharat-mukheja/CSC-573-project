#from numpy import inf

inf = 100000

sw1 = '00:00:de:dc:b4:67:6b:4a'
sw2 = '00:00:0a:8a:41:2d:14:4e'
sw3 = '00:00:2e:dc:85:14:06:4e'
sw4 = '00:00:c6:ad:66:51:df:40'
sw5 = '00:00:de:dd:cf:4e:a4:46'
sw6 = '00:00:32:cc:0e:23:09:46'

global switch_port_mac_dict
switch_port_mac_dict ={'00:00:de:dc:b4:67:6b:4a': {'1': 'fa:16:3e:00:54:a1', '2': 'fa:16:3e:00:4a:a0', '3': 'fa:16:3e:00:56:5f',
                             '4': 'fa:16:3e:00:4f:57'},
 '00:00:0a:8a:41:2d:14:4e': {'4': 'fa:16:3e:00:3d:27', '3': 'fa:16:3e:00:48:45', '2': 'fa:16:3e:00:40:9a',
                             '1': 'fa:16:3e:00:6e:17'},
 '00:00:2e:dc:85:14:06:4e': {'1': 'fa:16:3e:00:3f:f1', '2': 'fa:16:3e:00:3f:ba', '3': 'fa:16:3e:00:48:c3',
                             '4': 'fa:16:3e:00:2c:db'},
 '00:00:c6:ad:66:51:df:40': {'1': 'fa:16:3e:00:3f:dd', '2': 'fa:16:3e:00:75:61', '3': 'fa:16:3e:00:67:d1'},
 '00:00:de:dd:cf:4e:a4:46': {'1': 'fa:16:3e:00:4a:fc', '2': 'fa:16:3e:00:69:6c', '3': 'fa:16:3e:00:5a:06',
                             '4': 'fa:16:3e:00:58:27'},
 '00:00:32:cc:0e:23:09:46': {'1': 'fa:16:3e:00:64:72', '2': 'fa:16:3e:00:60:9e', '3': 'fa:16:3e:00:2e:fa',
                             '4': 'fa:16:3e:00:5c:b2'},
 }


eth_tg3 = 'fa:16:3e:00:7a:15'
eth_tg2 = 'fa:16:3e:00:84:4f'
eth_ms1 = 'fa:16:3e:00:29:84'
eth_ms2 = 'fa:16:3e:00:44:0e'
eth_client = 'fa:16:3e:00:6b:44'


global switch_port_mat
global switch_number_dpid
dpid_switch_number = {sw1: 0, sw2: 1, sw3: 2, sw4: 3, sw5: 4, sw6: 5}
switch_number_dpid = {0: sw1, 1: sw2, 2: sw3, 3: sw4, 4: sw5, 5: sw6}
switch_port_mat = [[0, '2', 0, 0, 0, '3'],
                   ['4', 0, '3', 0, '2', 0],
                   [0, '3', 0, '4', 0, '2'],
                   [0, 0, '2', 0, '3', 0],
                   [0, '2', 0, '4', 0, '1'],
                   ['4', 0, '1', 0, '2', 0],
                   ]

# dictionary of switches with key = dpid
global switch_dict
switch_dict = {}

global paths
paths = {sw1: {
    sw4: [[0, 1, 2, 3], [0, 1, 4, 3], [0, 5, 4, 3], [0, 1, 2, 5, 4, 3], [0, 5, 4, 1, 2, 3], [0, 5, 2, 1, 4, 3],
          [0, 1, 4, 5, 2, 3], [0, 5, 2, 3]]}}

global paths
paths = {sw1: {
    sw4: [[0, 1, 2, 3], [0, 1, 4, 3], [0, 5, 4, 3], [0, 1, 2, 5, 4, 3], [0, 5, 4, 1, 2, 3], [0, 5, 2, 1, 4, 3],
          [0, 1, 4, 5, 2, 3], [0, 5, 2, 3]]}}

inf = 100000
cost_matrix = [[inf, 1, inf, inf, inf,1],[1, inf,1,inf,1, inf],[inf,1, inf,1, inf,1],[inf, inf,1, inf,1, inf],[inf,1, inf,1, inf,1],[1, inf,1, inf,1, inf]]
