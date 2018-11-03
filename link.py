from collections import deque


class Link:
    def __init__(self, connection1, connection2, buffer_size, capacity, static_cost, id, network):

        # The id of the link represented as an integer
        self.id = id

        # Reference to the network object
        self.network = network
        
        # Initialize the capacity of the link
        self.capacity = capacity
        
        # Initalize one connection on one side of the link by setting the field 
        # equal to the host or router object it is connected to
        self.connection1 = connection1
        
        # Initialize the other connection on the other side of the link by 
        # setting the field equal to the host or router object it is 
        # connected to
        self.connection2 = connection2
        
        # Intialize the link buffer
        self.buffer = deque()
        
        # Initialize the bit rate, this will be the current packets divided by
        # the round trip time
        ### NEED Help with this part ####
        self.bit_rate = -1
        
        # Initialize the static cost, which is the length of the link
        self.static_cost = static_cost
        
        # Initialize the dynamic cost - we will probably need a function
        ### Need help with this part, like what exactly is it ?###
        # self.dynamic_cost = dynamic_cost
        
        # Initalize a list that holds all the current packets in the link, this
        # will be updated as packets go into the link and out of it.
        self.current_packets = []


        self.queue_capacity = buffer_size
        


    def update_bit_rate(self):
        '''
        The bit rate should be equal to the amount of bits sent over the 
        previous time stamp divided by the time delta. At most, in will
        equal the capacity of the link. At least, we are able to send everything 
        that was previously in the buffer, so we calculate the total bits over 
        those packets and divide by the time delta.
        '''

        pass 



    def add_packets(self, pkt):
        '''
        This function will take packets that arrived at the link and put them into
        the link buffer. This function will be called by the con 
        '''
        
        # The packet will be put into the buffer
        
        # This will simulate the packet being sent through the link
        
        # Update the congestion and dynamic cost pf the link and bit rate? 
        pass 
    
    def finish_sending_packet(self, packet):
        '''
        This function will be invoked by the router or host or packet when they 
        are supposed to be finished sending. 
        '''
        
        # The packet is removed from the current_packets queue
        
        # The bit rate and dynamic cost of the link should be updated
        
        # The link should call one of the connections that it is connected to 
        # say that the packet has arrived and call that connections recieved 
        # function packet 
        

    def run(self):
        '''
        Called by the network at every interruption
        Check queues to see if any packets has arrived
        '''
        pass
