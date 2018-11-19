from collections import deque
from host import Host
from utils import (
    DEBUG, RENO,
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
        
        # Initialize the received packets queue. This will hold all the packets
        # that the router receives
        self.received_packets = deque()        
        
        # Initialize the routing table as a dictionary so that we can store the
        # next node or link to take asas a value and the destination ip address
        # as a key
        self.routing_table = {}
        
        # Initialize a list of links that the router is connected to
        self.outgoing_links = []
        self.incoming_links = []
        
        # Initalize the current number of packets in the buffer
        self.current_number_pkt_buffer = len(self.outgoing_packets)
    
        # The root that the router thinks is the root of the network
        self.root = id
        
        # The distance from the root that the router thinks it is
        self.distance = 0

        # Field to keep track of current time
        self.curr_time = None

        # list of neighboring hosts/routers
        self.neighbors = []
    
    
    
        
    def update_routing_table(self):
        '''
        This function will perform a shortest path algorithm to figure out the 
        shortest distance from this router to all the other hosts and routers 
        in the network. It will use message passing between routers and the 
        Bellman Ford algorithm to figure out what the routing table will be.
        '''
        # Get each host to generate a packet
        self.network.generate_messages()

    
    def send_packet(self):
        '''
        At every iteration this function will be invoked to see if a packet(s) can
        be sent from the router. 
        '''
    
        # For each packet about to be sent the router should look up which link 
        # to place them on by looking up their destinations in the routing 
        # table	
        # TODO: WTF WTF WTF????
        for packet in list(self.outgoing_packets):
            if packet.packet_type == MESSAGE:
                packet.prev_link.add_packets([packet])
                # Delete the packet from the outgoing queue
                self.outgoing_packets.remove(packet)
                if isinstance(packet.destination, Host):
                    print("Sent message destined for Host " +
                          str(packet.destination.id) + 
                          " and sent it from router " + str(self.id) +
                          " with original starting point being Router" + str(packet.source.id) +
                          " via link " + str(packet.prev_link.id)) 
                else:
                    print("Sent message destined for Router " + str(packet.destination.id) +  " with original starting point being Router" + 
                          str(packet.source.id) + \
                          " and sent it from router " + str(self.id) + \
                          " via link " + str(packet.prev_link.id))
                
            else:
                # Delete the packet from the outgoing queue
                self.outgoing_packets.remove(packet)                
                # Find the link to use to send the packet
                chosen_link = (self.routing_table[packet.destination.ip])[1]
                
                # We want to send the packet by adding it to the link's buffer
                chosen_link.add_packets(packet)
                    
                # Update the current position to be the link
                packet.curr_pos = chosen_link
                
                if DEBUG:
                    print("sent packet = " + str(packet.id) + "of flow id = " + str(packet.id))
                    print("from router " +  str(self.id))
        
    def send_messages(self):
        # Create the message from the host spawn it for all directions that the 
        # router is connected to
        for link in self.outgoing_links: 
            message = self.network.create_packet(MESSAGE_SIZE, MESSAGE,
                                                self, self.neighbors[link], self.curr_time,
                                                False, self)  
            message.prev_link = link
            self.outgoing_packets.append(message)
            if DEBUG:
                if isinstance(self.neighbors[link], Host):
                    print("Created message destined for Host " + str(self.neighbors[link].id) + " and sent it from router " + str(self.id) + " via link " + str(link.id)) 
                else:
                    print("Created message destined for Router " +
                          str(self.neighbors[link].id) + 
                          " and sent it from router " + str(self.id) + 
                          " via link " + str(link.id))                     
            
        
    def receive_packet(self, pkt):
        '''
        This function will have the router receive a packet and then forward it
        to its next destination.
        '''

        # This function will be called when a packet arrives at a router
    
        # Check if the received packet is a message, we want to basically check
        # the minimum spanning tree protocol and send a new packet
        if pkt.packet_type == 2:
            # get node that message as originated from
            orgin = pkt.source
            
            if DEBUG:
                    print("Received message destined for Router " +
                          str(pkt.destination.id) + 
                          " which was sent originally from Router " + str(pkt.source.id) + 
                          " and sent from Router " + str(self.neighbors[pkt.prev_link].id) +
                          " via link " + str(pkt.prev_link.id) + " with a cost of "
                          + str(pkt.current_cost)) 
            
            # if the host does not exist in the routing table or the distance to 
            # this distination is shorter 
            if orgin not in self.routing_table or (self.routing_table[orgin])[1] > pkt.current_cost:
                self.routing_table[orgin] = [pkt.prev_link, pkt.current_cost]    
            
            else:
                # we didn't update the routing table so we don't want to forward
                # this info
                return
            
            print(" -----Table for router " + str(self.id))
            lst = self.routing_table.items()
            for item in lst:
                if isinstance(item[0], Host):
                    print("Host = " + str(item[0].id) + " via link " + 
                          str((item[1])[0].id) + " with a cost of " + str(item[1][1]))
                else:
                
                    print("Router = " + str(item[0].id) + " via link " + 
                            str((item[1])[0].id) + " with a cost of " + str(item[1][1]))                    
            print('')            
            
            
            for link in self.outgoing_links:
                if link != pkt.prev_link:
                    message = self.network.create_packet(MESSAGE_SIZE, MESSAGE,
                                                         pkt.source, self.neighbors[link], self.curr_time,
                                                         False, self)  
                    message.current_cost = pkt.current_cost
                    # Update the current postion of the packet to the current router
                    message.curr_pos = self
                    message.in_transit = 1
                    
                    message.prev_link = link
                    
                    # then it will place the packet in its outgoing packets queue
                    self.outgoing_packets.append(message)  
                    print("Transmitted message destined for Router " +
                          str(message.destination.id) + 
                          " which was sent originally from Router " + str(message.source.id) + 
                          " and sent from Router " + str(self.id) +
                          " via link " + str(link.id) + " with a cost of " +
                          str(message.current_cost)) 
                
        
        else:
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
        #self.update_routing_table()
