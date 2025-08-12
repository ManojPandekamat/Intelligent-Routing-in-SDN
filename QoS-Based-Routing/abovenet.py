#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import networkx as nx
import matplotlib.pyplot as plt
import requests
import json
import time
import random
import pandas as pd

class CustomTopology:
    def __init__(self):
        self.net = None
        self.graph = nx.Graph()
        self.cost_matrix = []
        self.route=[]


    def build_topology(self,first_values):
        """Create the topology with 15 switches and hosts."""
        self.net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

        info('*** Adding controller\n')
        self.net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

        info('*** Adding switches\n')
        switches = {
            i+1: self.net.addSwitch(f's{i+1}', protocols='OpenFlow13') for i in range(15)
        }

        info('*** Adding hosts\n')
        hosts = {
            i+1: self.net.addHost(f'h{i+1}', ip=f'10.0.0.{i+1}/24') for i in range(15)
        }

        info('*** Adding links\n')
        links = [
            (1, 2), (1, 3), (2, 4), (2, 5),
            (3, 6), (3, 7), (4, 8), (5, 9),
            (6, 10), (7, 11), (8, 12), (9, 13),
            (10, 14), (11, 15), (13, 7), (7, 10),
            (1, 4), (2, 3), (5, 6), (8, 9),
            (10, 11), (12, 13), (14, 15)
        ]
        
        i=0
        for src, dst in links:
            self.net.addLink(switches[src], switches[dst], bw=10, delay=f'{first_values[i]}ms')
            i+=1

        # Connect hosts to switches
        for i in range(1, 16):
            self.net.addLink(hosts[i], switches[i])

        return self.net

    def read_mininet_topology(self):
        """Read the topology from Mininet and convert it into a NetworkX graph."""
        self.graph.clear()  # Clear the graph to avoid duplicates
        switches = self.net.switches
        links = self.net.links

        # Add switches as nodes
        for switch in switches:
            self.graph.add_node(switch.name)

        # Add links as edges with weights (assuming link delay as weight)
        for link in links:
            src = link.intf1.node.name
            dst = link.intf2.node.name
            delay = link.intf1.params.get('delay', '0ms')
            weight = float(delay.strip('ms')) if 'ms' in delay else 0.0
            self.graph.add_edge(src, dst, weight=weight)

    def modify_link_delay(self,second_values):
        """Modify the delay between two nodes in the existing topology."""
        print(self.route)
        try:
            # Get the node objects
            route = self.route
            for i in range(len(route) - 1):
                node1 = route[i]
                node2 = route[i + 1]
                node1_obj = self.net.get(route[i])
                node2_obj = self.net.get(route[i + 1])
                print(node1,node2,second_values)
                for src,dst,delay in second_values:
                    if (src==node1 and dst==node2) or (dst==node1 and src==node2):
                        actual_delay = delay
                        #print(src,dst,node1,node2,delay)
                new_delay = f"{actual_delay}ms"

                # Find the link between the two nodes
                links = node1_obj.connectionsTo(node2_obj)
                if not links:
                    print(f"Delay between {route[i]} and {route[i + 1]} updated to {new_delay}ms")
                    return
                new_delay_value = float(new_delay.strip('ms'))  # Convert delay to integer
                self.cost_matrix[int(node1[-1]) - 1][int(node2[-1]) - 1] = new_delay_value  # Update the edge weight in the graph
                self.cost_matrix[int(node2[-1]) - 1][int(node1[-1]) - 1] = new_delay_value  # Update the edge weight in the graph
                print(f"Delay between {node1} and {node2} updated to {new_delay_value}ms")

                # Update the link delay
                for link in links:
                    link[0].config(delay=new_delay)
                    link[1].config(delay=new_delay)
		
        except Exception as e:
            print(f"Error while modifying link delay: {e}")

    def print_adjacency_matrix(self):
        """Construct and print the adjacency matrix of the graph for switches."""
        def construct_adjacency_matrix(graph, switches):
            """Construct the adjacency matrix for switch-to-switch topology."""
            num_switches = len(switches)
            matrix = [[0] * num_switches for _ in range(num_switches)]

            for i, switch1 in enumerate(switches):
                for j, switch2 in enumerate(switches):
                    if graph.has_edge(switch1, switch2):
                        matrix[i][j] = graph[switch1][switch2].get('weight', 0)

            return matrix

        switches = [node for node in self.graph.nodes if node.startswith('s')]
        adjacency_matrix = construct_adjacency_matrix(self.graph, switches)

        print("*** Adjacency Matrix ***")
        print(" " * 10 + "  ".join(f"{s:10}" for s in switches))
        for i, row in enumerate(adjacency_matrix):
            print(f"{switches[i]:10}" + "  ".join(f"{val:10}" for val in row))

        return adjacency_matrix

    def add_flow_rules(self, source, destination, path):
        """Add flow rules for the given path."""
        routes = [
    	[0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    	[1, 0, 4, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    	[1, 4, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    	[3, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
    	[0, 1, 0, 0, 0, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0],
    	[0, 0, 1, 0, 3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0],
    	[0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 2, 0, 3, 0, 0],
    	[0, 0, 0, 1, 0, 0, 0, 0, 3, 0, 0, 2, 0, 0, 0],
    	[0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 2, 0, 0],
    	[0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 4, 0, 0, 2, 0],
    	[0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 2],
    	[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 0],
    	[0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 3, 0, 0, 0],
    	[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
    	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0],
 
]

        dest_no = int(destination[1])  # Extract destination switch number

        for i in range(len(path) - 1):
            curr_switch = path[i]  # Current switch in the path
            next_hop_switch = path[i + 1]  # Next hop switch in the path

            curr_switch_no = int(curr_switch[1])
            next_switch_no = int(next_hop_switch[1])

            ODL_HOST = "localhost"
            ODL_PORT = "8181"
            NODE_ID = f"openflow:{curr_switch_no}"
            TABLE_ID = "0"
            FLOW_ID = f"flow_{source}_{destination}_{i + 1}"
            DEST_IP = f"10.0.0.15/24"
            PRIORITY = "1000"
            OUTPUT_PORT = f"{routes[curr_switch_no - 1][next_switch_no - 1]}"

            url = f"http://{ODL_HOST}:{ODL_PORT}/restconf/config/opendaylight-inventory:nodes/node/{NODE_ID}/flow-node-inventory:table/{TABLE_ID}/flow/{FLOW_ID}"

            flow_data = {
                "flow": {
                    "id": FLOW_ID,
                    "table_id": int(TABLE_ID),
                    "priority": int(PRIORITY),
                    "flow-name": "dest-ip-flow",
                    "match": {
                        "ipv4-destination": DEST_IP
                    },
                    "instructions": {
                        "instruction": [
                            {
                                "order": 0,
                                "apply-actions": {
                                    "action": [
                                        {
                                            "order": 0,
                                            "output-action": {
                                                "output-node-connector": OUTPUT_PORT,
                                                "max-length": 65535
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }

            try:
                response = requests.put(url, json=flow_data, auth=("admin", "admin"))
                if response.status_code == 200 or response.status_code == 201:
                    print(f"Flow added successfully: {FLOW_ID}")
                else:
                    print(f"Failed to add flow {FLOW_ID}. Response: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error while adding flow {FLOW_ID}: {e}")

        
        
    def build_graph_from_cost_matrix(self, cost_matrix):
        """Build a NetworkX graph from the cost matrix."""
        graph = nx.Graph()
        num_nodes = len(cost_matrix)

        for i in range(num_nodes):
            for j in range(num_nodes):
                if cost_matrix[i][j] > 0:  # Add edge only if cost is greater than 0
                    graph.add_edge(f's{i+1}', f's{j+1}', weight=cost_matrix[i][j])

        return graph

    def find_shortest_path_from_matrix(self, start_node, target_node):
        """Find and print the shortest path using NetworkX and cost matrix."""
        graph = self.build_graph_from_cost_matrix(self.cost_matrix)

        try:
            # Use Dijkstra's algorithm to find the shortest path
            path = nx.dijkstra_path(graph, source=start_node, target=target_node, weight='weight')
            path_length = nx.dijkstra_path_length(graph, source=start_node, target=target_node, weight='weight')
            print(f"Shortest path from {start_node} to {target_node}: {path}")
            print(f"Path length (total cost): {path_length}")
            self.route=path
            self.add_flow_rules(start_node, target_node, path)
        except nx.NetworkXNoPath:
            print(f"No path found between {start_node} and {target_node}")
            
    def pingDevice(self,node1,node2):
        h1=self.net.get(node1)
        h2=self.net.get(node2)
        print("======================================================")
        print()
        print()
        print("------------------------------------------------------")
        ping_result=h1.cmd(f"ping -c 5 {h2.IP()}")
        print(ping_result)
        print("------------------------------------------------------")
        print()
        #a=h2.cmd("nohup ITGRecv > /dev/null 2>&1 &")
        #b=h1.cmd(f"ITGSend -T UDP -a {h2.IP()} -c 100 -C 15 -t 15000 -l ./sender.log -x ./receiver.log")
        #ditg_result=h2.cmd("ITGDec ./receiver.log")
        print("------------------------------------------------------")
        #print(ditg_result)
        print("------------------------------------------------------")
        print()
        print()
        print("======================================================")

        
def main():
    df = pd.read_csv('Acutal_values.csv')
    df['Avg_Delay(ms)'] = df['Avg_Delay(ms)'].astype(float)  # Ensure 'delay' is of float type
    df_sorted = df.sort_values(by='Avg_Delay(ms)')  # Sort rows by 'delay' column
    print(df_sorted)

    df_sorted.to_csv('sorted_csv.csv', index=False)

    df_reversed = df_sorted.iloc[::-1].reset_index(drop=True)  # Reverse the rows
    print(df_reversed)

    df_reversed.to_csv('reversed_rows.csv', index=False)
    
    #==================================================================================================
    links = [
            (1, 2), (1, 3), (2, 4), (2, 5),
            (3, 6), (3, 7), (4, 8), (5, 9),
            (6, 10), (7, 11), (8, 12), (9, 13),
            (10, 14), (11, 15), (13, 7), (7, 10),
            (1, 4), (2, 3), (5, 6), (8, 9),
            (10, 11), (12, 13), (14, 15)
    ]
    first_values=[]
    
    for src,dst in links:
        try:
            temp1 = df_sorted[(df_sorted['Source'] == src) & (df_sorted['Destination'] == dst)].iloc[0]['Avg_Delay(ms)']
            first_values.append(temp1)
        except Exception as e:
            print(e)
            min_val_ms = 0.000119
            max_val_ms = 0.000152 
            delay = random.uniform(min_val_ms, max_val_ms)
            first_values.append(delay)

            
    print("first values",first_values)
    #==================================================================================================
    
    setLogLevel('info')
    topology = CustomTopology()
    net = topology.build_topology(first_values)
    
    
    net.start()
    print("============================Stabalizing topology=====================================")
    
    print("=====================================================================================")

    info("*** Starting network\n")
    time.sleep(5)
    print("============================Reading topology=====================================")
    topology.read_mininet_topology()
    topology.cost_matrix = topology.print_adjacency_matrix()
    print("=====================================================================================")
    

        
    print("============================Iteration 1==============================================")
    topology.find_shortest_path_from_matrix('s4', 's15')
    print("=====================================================================================")
    time.sleep(3)
    print("==============================ping from h4 to h15======================================")
    topology.pingDevice('h4','h15')
    print("=====================================================================================")
    print("==============================Iteration 1 complete===================================")
        #==================================================================================================
    links = [
            (1, 2), (1, 3), (2, 4), (2, 5),
            (3, 6), (3, 7), (4, 8), (5, 9),
            (6, 10), (7, 11), (8, 12), (9, 13),
            (10, 14), (11, 15), (13, 7), (7, 10),
            (1, 4), (2, 3), (5, 6), (8, 9),
            (10, 11), (12, 13), (14, 15)
    ]
    
    second_values=[]
    for src,dst in links:
        try:
            temp1=df_reversed[(df_reversed['Source'] == src) & (df_reversed['Destination'] == dst)].iloc[0]['Avg_Delay(ms)']
            second_values.append((f"s{src}",f"s{dst}",temp1))
        except Exception as e:
            print(e)
            min_val_ms = 0.000199  # Convert to ms
            max_val_ms = 0.000262  # Convert to ms

            # Generate a random value in the range in milliseconds
            delay = random.uniform(min_val_ms, max_val_ms)
            second_values.append((f"s{src}",f"s{dst}",delay))
            
    print("second values",second_values)
    #==================================================================================================
    print("==============================Modifying delay========================================")
    topology.modify_link_delay(second_values)
    print("==============================Modification Done!=====================================")
    print("****Cost matrix****")
    for row in topology.cost_matrix:
        print(row)
    print("=====================================================================================")
    
    print("============================Iteration 2==============================================")
    time.sleep(3)
    print("==============================ping from h4 to h15======================================")
    topology.pingDevice('h4','h15')
    print("=====================================================================================")
       
    topology.find_shortest_path_from_matrix('s4', 's15')
    print("=====================================================================================")
    time.sleep(3)
    print("****Cost matrix****")
    for row in topology.cost_matrix:
        print(row)
        
    print("==============================ping from h4 to h15======================================")
    topology.pingDevice('h4','h15')
    print("=====================================================================================")
    print("==============================Iteration 2 complete===================================")
    


    info("*** Running CLI\n")
    CLI(net)
    net.stop()


if __name__ == '__main__':
    main()  
