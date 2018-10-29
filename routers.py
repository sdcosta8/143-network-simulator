from collections import deque


class Router:
    
    def __init__(self, ip_address):
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
        
    def update_routing_table(self):
        '''
        This function will perform a shortest path algorithm to figure out the 
        shortest distance from this router to all the other hosts and routers 
        in the network. It will use message passing between routers and the 
        Bellman Ford algorithm to figure out what the routing table will be.
        '''
        # Perform the minimum spanning tree protocol??
        
        # Preform the bell man ford algorithm to update the routing table
        
        # Unclear how often this function will be preformed.
        
        pass
    
    def send_packet(self):
        '''
        At every iteration this function will be invoked to see if a packet(s) can
        be sent from the router. 
        '''

        # If there are no packets to send in the out_going packet queue,
        # the function should return
        
        # The router will send all the packets in its outgoing packet queue.
        
        # For each packet about to be sent the router should look up which link 
        # to place them on by looking up their destinations in the routing 
        # table
        
        # These newly sent packets should call a method of each link that the router
        # picked for the packets to let it know that packets are waiting
        # to be sent on it so that it can be put in the link's buffer
        
        # Update flows associated with these packets???
        pass
        
    def recieve_packet(self, pkt):
        '''
        This function will have the router recieve a packet and then forward it
        to its next destination.
        '''

        # This function will be called when a packet arrives at a router
        
        # The router will look at the packet for its final destination and then
        # it will look up the final destination its its routing table and place
        # the packet in its outgoing packets queue.