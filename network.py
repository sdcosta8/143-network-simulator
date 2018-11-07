from flow import Flow
from host import Host
from link import Link
from router import Router
from packet import Packet
from utils import (
    DEBUG, RENO, TIMESTEP,
    PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)

class Network:

    def __init__(self):
        # All the objects in the network
        # The hash key is the id of the object
        self.flows = {}
        self.next_flow_id = 0
        self.hosts = {}
        self.next_host_id = 0
        self.routers = {}
        self.next_router_id = 0
        self.links = {}
        self.next_link_id = 0
        self.packets = {}
        self.next_packet_id = 0
        self.curr_time = 0
        self.is_running = False

    def create_flow(self, size, source, destination, spawn_time, max_window):
        flow = Flow(size, source, destination, spawn_time, max_window,
                    self.next_flow_id, self)
        self.flows[self.next_flow_id] = flow
        if DEBUG:
            print("Flow successfully created, id:", self.next_flow_id)
        self.next_flow_id += 1
        return flow

    def create_host(self, ip_address, link_connected=None):
        host = Host(ip_address, link_connected, self.next_host_id, self)
        self.hosts[self.next_host_id] = host
        if DEBUG:
            print("Host successfully created, id:", self.next_host_id)
        self.next_host_id += 1
        return host

    def create_link(self, connection1, connection2, buffer_size, capcity, static_cost):
        link = Link(connection1, connection2, buffer_size, capcity, static_cost,
                    self.next_link_id, self)
        self.links[self.next_link_id] = link
        if DEBUG:
            print("Link successfully created, id:", self.next_link_id)
        self.next_link_id += 1
        return link

    def create_router(self, ip_address):
        router = Router(ip_address, self.next_router_id, self)
        self.routers[self.next_router_id] = router
        if DEBUG:
            print("Router successfully created, id:", self.next_router_id)
        self.next_router_id += 1
        return router
    
    def create_packet(self, num_bits, packet_type, source,
                      destination, in_transit, curr_pos,
                      flow_id=None, packet_info=None,
                      packet_no=None, last_packet=None):
        packet = Packet(num_bits, packet_type, source, destination,
                        self.curr_time, in_transit, curr_pos,
                        self.next_packet_id, self,
                        flow_id, packet_info, packet_no, last_packet)
        self.packets[self.next_packet_id] = packet
        self.next_packet_id += 1
        return packet

    def run_network(self):
        '''
        Call and run all components of the network
        '''
        self.is_running = True

        # TODO: Need a stopping mechanism
        while self.is_running:
            for _, flow in self.flows.items():
                flow.run(self.curr_time)
            for _, host in self.hosts.items():
                host.run(self.curr_time)
            for _, router in self.routers.items():
                router.run(self.curr_time)
            for _, link in self.links.items():
                link.run(self.curr_time)
            for _, flow in self.flows.items():
                flow.run(self.curr_time)

            self.curr_time += TIMESTEP

    
