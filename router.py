from collections import deque
from utils import (
    DEBUG, RENO, TIMESTEP,
    PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)


class Router:
    
    def __init__(self, ip_address, id, network):

        # The id of the router represented as an integer
        self.id = id

        # Reference to the network object
        self.network = network

        # Initialize the ip_address of the router
        self.ip = ip_address        
        
        # Initialize the router's buffer queue. This will hold all the packets
        # that the router is waiting to send 
        self.outgoing_packets = deque()        
        
        # Initialize the recieved packets queue. This will hold all the packets
        # that the router recieves
        self.recieved_packets = deque()        
        
        # Initialize the routing table as a dictionary so that we can store the
        # next node or link to take asas a value and the destination ip address
        # as a key
        self.routing_table = {}
        
        # Initialize a list of links that the router is connected to
        self.links = []
        
        # Initalize the current number of packets in the buffer
        self.current_number_pkt_buffer = len(self.outgoing_packets)
    
        # The root that the router thinks is the root of the network
        self.root = id
        
        # The distance from the root that the router thinks it is
        self.distance = 0

        # Field to keep track of current time
        self.curr_time = None
    
        
    def update_routing_table(self):
        '''
        This function will perform a shortest path algorithm to figure out the 
        shortest distance from this router to all the other hosts and routers 
        in the network. It will use message passing between routers and the 
        Bellman Ford algorithm to figure out what the routing table will be.
        '''
        # Perform the minimum spanning tree protocol??
        
        # Get the sum of the dynamic and static cost of all the links
        
        # Preform the bell man ford algorithm to update the routing table
        
        # Unclear how often this function will be preformed.
        
        pass
    
    def send_packet(self):
        '''
        At every iteration this function will be invoked to see if a packet(s) can
        be sent from the router. 
        '''
    
        # For each packet about to be sent the router should look up which link 
        # to place them on by looking up their destinations in the routing 
        # table	
        # TODO: WTF WTF WTF????
        for packet in self.outgoing_packets:
        
            # Delete the packet from the outgoing queue
            self.outgoing_packets.remove(packet)
            
            # Find the link to use to send the packet
            chosen_link = self.routing_table[packet.destination.ip]
            
            # We want to send the packet by adding it to the link's buffer
            chosen_link.add_packets(packet)
                
            # Update the current position to be the link
            self.curr_pos = chosen_link
            
            if DEBUG:
                print("sent packet = " + packet.id + "of flow id = " + packet.id)
                print("from router " +  self.id)
        
    def recieve_packet(self, pkt):
        '''
        This function will have the router recieve a packet and then forward it
        to its next destination.
        '''

        # This function will be called when a packet arrives at a router
    
        # Check if the recieved packet is a message, we want to basically check
        # the minimum spanning tree protocol and send a new packet
        if pkt.packet_type == 2:
            #### Get the previous link that the pkt was sent from
            
            info = pkt.packet_info
            # from_ip_address = info[0]
            root = info[1]
            distance_from_root = info[2]
            
            if root < self.root:
                # update the info that the router sees 
                self.root = root
                self.distance = distance_from_root + 1
            
            info = [self.id, self.root, self.distance]
            
            # find the routers that the router is connected to and send this 
            # info
            # for routers in neighboring_routers:
            #     #### TODO ROUTER Minimum spanning tree protocol
            #     pass
            
        # Update the current postion of the packet to the current router
        pkt.curr_pos = self
        pkt.in_transit = 1
        
        # then it will place the packet in its outgoing packets queue
        self.outgoing_packets.append(pkt)
        
    
    def run(self, curr_time):
        '''
        Called by the network at every interruption
        Check queues to see if any packets can be sent
        '''
        # Update internal clock
        self.curr_time = curr_time
        
        self.send_packet()
        self.update_routing_table()
