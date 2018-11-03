from flow import Flow
from host import Host
from link import Link
from router import Router
from packet import Packet

class Network:

    TIMESTEP = 0.1


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
        self.current_time = 0

    def create_flow(self, size, source, destination, spawn_time):
        flow = Flow(size, source, destination, spawn_time,
                    self.next_flow_id, self)
        self.flows[self.next_flow_id] = flow
        self.next_flow_id += 1
        return flow

    def create_host(self, ip_address, max_window_size, link_connected=None):
        host = Host(ip_address, link_connected, max_window_size,
                    self.next_host_id, self)
        self.hosts[self.next_host_id] = host
        self.next_host_id += 1
        return host

    def create_link(self, connection1, connection2, buffer_size, capcity, static_cost):
        link = Link(connection1, connection2, buffer_size, capcity, static_cost,
                    self.next_link_id, self)
        self.links[self.next_link_id] = link
        self.next_link_id += 1
        return link

    def create_router(self, ip_address):
        router = Router(ip_address, self.next_router_id, self)
        self.routers[self.next_router_id] = router
        self.next_router_id += 1
        return router
    
    def create_packet(self, num_bits, packet_type, source,
                      destination, in_transit, curr_pos,
                      flow_id=None, packet_info=None,
                      packet_no=None, last_packet=None):
        packet = Packet(num_bits, packet_type, source, destination,
                        self.current_time, in_transit, curr_pos,
                        self.next_packet_id, self,
                        flow_id, packet_info, packet_no, last_packet)
        self.packets[self.next_packet_id] = packet
        self.next_packet_id += 1
        return packet

    def run_network(self):
        '''
        Call and run all components of the network
        '''
        for _, flow in self.flows.items():
            flow.run()
        for _, host in self.hosts.items():
            host.run()
        for _, router in self.routers.items():
            router.run()
        for _, link in self.links.items():
            link.run()
        for _, flow in self.flows.items():
            flow.run()
        
        # TODO: book keeping

    
