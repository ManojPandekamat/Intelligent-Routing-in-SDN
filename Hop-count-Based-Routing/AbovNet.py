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
import random
import time

class CustomTopology:
    def __init__(self):
        self.net = None
        self.graph = nx.Graph()
        self.cost_matrix = []

    def build_topology(self):
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
        min_val_ms = 0.000199  # Convert to ms
        max_val_ms = 0.000262 # Convert to ms

        for src, dst in links:
            delay = random.uniform(min_val_ms, max_val_ms)
            self.net.addLink(switches[src], switches[dst], bw=10, delay=f'{delay}ms')

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
            weight = float(delay.strip('ms')) if 'ms' in delay else 0
            self.graph.add_edge(src, dst, weight=weight)

    def print_adjacency_matrix(self):
        """Construct and print the adjacency matrix of the graph for switches."""
        def construct_adjacency_matrix(graph, switches):
            """Construct the adjacency matrix for switch-to-switch topology."""
            num_switches = len(switches)
            matrix = [[0] * num_switches for _ in range(num_switches)]

            for i, switch1 in enumerate(switches):
                for j, switch2 in enumerate(switches):
                    if graph.has_edge(switch1, switch2):
                        matrix[i][j] = 1

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
            DEST_IP = f"10.0.0.{dest_no}/24"
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
            self.add_flow_rules(start_node, target_node, path)
        except nx.NetworkXNoPath:
            print(f"No path found between {start_node} and {target_node}")

def main():
    setLogLevel('info')

    # Create and build the topology
    topology = CustomTopology()
    net = topology.build_topology()
    net.start()

    # Build the graph and add flows
    topology.read_mininet_topology()
    topology.cost_matrix=topology.print_adjacency_matrix()

    # Example to find the shortest path from switch s1 to switch s15
    topology.find_shortest_path_from_matrix('s4', 's15')

    # Start the network and CLI
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()

