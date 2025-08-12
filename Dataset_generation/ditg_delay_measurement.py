#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import networkx as nx
import time
import csv

#Abilene topology
class CustomTopology:
    def __init__(self):
        self.net = None
        self.graph = nx.Graph()

    def build_topology(self):
        """Create the topology with 15 switches and hosts."""
        self.net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

        info('*** Adding controller\n')
        self.net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

        info('*** Adding switches\n')
        switches = {
            i + 1: self.net.addSwitch(f's{i+1}', protocols='OpenFlow13') for i in range(15)
        }

        info('*** Adding hosts\n')
        hosts = {
            i + 1: self.net.addHost(f'h{i+1}', ip=f'10.0.0.{i+1}/24') for i in range(15)
        }

        info('*** Adding links\n')
        links = [(1, 2, 0.092), (1, 3, 0.094), (2, 4, 0.094), (2, 5, 0.1), (3, 5, 0.084), (4, 6, 0.1), (5, 6, 0.090), (5, 7, 0.097), (6, 8, 0.097), (7, 9, 0.101), (8, 10, 0.105), (9, 11, 0.104)]

        for src, dst, delay in links:
            self.net.addLink(switches[src], switches[dst], bw=10, delay=f'{delay}ms')

        # Connect hosts to switches
        for i in range(1, 16):
            self.net.addLink(hosts[i], switches[i])

        return self.net

    def measure_delay_ditg(self):
        net = self.net
        try:
            links = [(1, 2, 0.092), (1, 3, 0.094), (2, 4, 0.094), (2, 5, 0.1), (3, 5, 0.084), (4, 6, 0.1), (5, 6, 0.090), (5, 7, 0.097), (6, 8, 0.097), (7, 9, 0.101), (8, 10, 0.105), (9, 11, 0.104)]

            for src, dst,x in links:
                switch1 = f"s{src}"
                switch2 = f"s{dst}"
                s1 = net.get(switch1)
                s2 = net.get(switch2)
                s1.cmd('ifconfig {} 10.0.0.100 netmask 255.0.0.0'.format(switch1))
                s2.cmd('ifconfig {} 10.0.0.101 netmask 255.0.0.0'.format(switch2))

                # Start ITGRecv on one switch
                s2.cmd("nohup ITGRecv > /dev/null 2>&1 &")
                time.sleep(1)  # Allow ITGRecv to initialize

                # Send traffic using ITGSend from the other switch
                itg_send_command = (
                    "ITGSend -T UDP -a 10.0.0.101 -c 100 -C 10 "
                    "-t 15000 -l sender.log -x receiver.log"
                )

                s1.cmd("ping -c 4 10.0.0.101")
                s1.cmd(itg_send_command)

                # Decode the log files using ITGDec
                decode_result = s2.cmd("ITGDec receiver.log")

                # Parse the delay result from ITGDec output
                avg_delay = None
                for line in decode_result.splitlines():
                    if "average bitrate" in line.lower():
                        avg_delay = line.split("=")[-1].strip().split()[0]  # Extract only the delay value
                        print(f"Avg delay from {switch1} to {switch2}: {avg_delay}")
                        break
                else:
                    print(f"Failed to get delay result for {switch1} -> {switch2}")

                # Write the result for this src-dst pair to CSV
                with open('demo.csv', mode='a', newline="") as fd:
                    csv_writer = csv.writer(fd)
                    if avg_delay:
                        csv_writer.writerow([src, dst, avg_delay])

                # Cleanup log files and stop ITGRecv
                s1.cmd("rm -f sender.log receiver.log")
                s2.cmd("pkill ITGRecv")

        except Exception as e:
            print(f"Error during D-ITG delay measurement: {e}")


def main():
    setLogLevel('info')
    topology = CustomTopology()
    net = topology.build_topology()

    with open('demo.csv', mode='w', newline="") as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["Source", "Destination", "Avg_Delay(ms)"])

    print("============================Stabilizing topology=====================================")
    time.sleep(5)
    print("=====================================================================================")

    info("*** Starting network\n")
    net.start()

    for i in range(100):  # Measure delay 100 times
        topology.measure_delay_ditg()

    info("*** Running CLI\n")
    CLI(net)
    net.stop()


if __name__ == '__main__':
    main()

