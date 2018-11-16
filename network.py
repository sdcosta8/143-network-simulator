from flow import Flow
from host import Host
from link import Link
from router import Router
from packet import Packet
from utils import (
    DEBUG, RENO,
    PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)

class Network:

    def __init__(self):
        # All the objects in the network
        # The hash key is the id of the object
        self.flows = {}
        self.hosts = {}
        self.routers = {}
        self.links = {}
        self.curr_time = 0
        self.is_running = False
        self.timestep = 0

    def create_flow(self, size, source, destination, spawn_time, window, flow_id):
        flow = Flow(size, source, destination, spawn_time, window,
                    flow_id, self)
        self.flows[flow_id] = flow
        if DEBUG:
            print("Flow successfully created, id:", flow_id)
        return flow

    def create_host(self, ip_address, host_id, link_connected=None):
        host = Host(ip_address, link_connected, host_id, self)
        self.hosts[host_id] = host
        if DEBUG:
            print("Host successfully created, id:", host_id)
        return host

    def create_link(self, connection1, connection2, buffer_size, capcity, static_cost, link_id):
        link = Link(connection1, connection2, buffer_size, capcity, static_cost,
                    link_id, self)
        self.links[link_id] = link
        if DEBUG:
            print("Link successfully created, id:", link_id)
        return link

    def create_router(self, ip_address, router_id):
        router = Router(ip_address, router_id, self)
        self.routers[router_id] = router
        if DEBUG:
            print("Router successfully created, id:", router_id)
        return router
    
    def create_packet(self, num_bits, packet_type, source,
                      destination, time_spawn, in_transit, curr_pos,
                      flow=None, packet_info=None,
                      packet_no=None, last_packet=False,
                      expecting_packet=None):
        packet = Packet(num_bits, packet_type, source, destination,
                        time_spawn, in_transit, curr_pos,
                        self, flow, 
                        packet_info, packet_no, last_packet, expecting_packet)
        return packet

    def run_network(self):
        '''
        Call and run all components of the network
        '''
        self.is_running = True
        while self.is_running:
            if DEBUG:
                print("current time:", self.curr_time)
            for _, flow in self.flows.items():
                flow.run(self.curr_time)
            for _, host in self.hosts.items():
                host.run(self.curr_time)
            for _, router in self.routers.items():
                router.run(self.curr_time)
            for _, link in self.links.items():
                link.run(self.curr_time)
            
            # Check if all flows are finished
            all_finished = True
            for _, flow in self.flows.items():
                if flow.finished is False:
                    all_finished = False
                    flow.run(self.curr_time)
            if all_finished:
                print("All flows finished!")
                self.is_running = False

            self.curr_time += self.timestep

    
