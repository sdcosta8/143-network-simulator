from collections import deque


class Link:
    def __init__(self, connection1, connection2, buffer_size, 
                 capacity, prop_time, id, network):

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
        
        # Initialize the bit rate
        self.bit_rate = -1
        
        # Initialize the static cost, which is the propagation time
        self.prop_time = prop_time
        
        # Initialize the dynamic cost - we will probably need a function
        ### Need help with this part, like what exactly is it ?###
        # self.dynamic_cost = dynamic_cost
        
        # Initalize a deque that holds all the traveling packets in the link
        # Each entry is a TUPLE, of the form (arrival time, packet object)
        # This will be updated as packets go into the link and out of it.
        self.traveling_packets = deque()


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

    def send_packet(self, curr_time, packet):
        '''
        Takes a packet that is popped from the buffer and schedule it for
        transimision.
        '''
        arrival_time = (
            curr_time +(packet.num_bits / self.bit_rate) + self.prop_time)
        self.traveling_packets.append((arrival_time, packet))

    
    def finish_sending_packet(self, packet):
        '''
        This function will be invoked when the packet is supposed to 
        finish sending. 
        '''
        # Tell connection2 that the packet has arrived
        self.connection2.receive_packet(packet)
        
        # TODO: The dynamic cost of the link should be updated
        

    def run(self, curr_time):
        '''
        Called by the network at every interruption
        Check queues to see if any packets has arrived
        '''
        # Check traveling packets and see if any packet should arrive
        while len(self.traveling_packets) > 0:
            arrival_time, packet = self.traveling_packets[0]
            # If this packet should arrive at connection2
            if arrival_time <= curr_time:
                self.traveling_packets.popleft()
                self.finish_sending_packet(packet)
            else:
                break
        
        # Check if the capacity is reached to send packets from buffer
        # Number of bits we are planning to send
        bits_planning = 0
        # Number of more bits we can send at this time
        bits_capacity = self.capacity * self.network.TIMESTEP
        for _, packet in self.traveling_packets:
            bits_capacity -= packet.num_bits
        while len(self.buffer) > 0:
            bits_planning += self.buffer[0].num_bits
            # If we cannot send this packet, break
            if bits_planning > bits_capacity:
                break
            # If we can, pop it off of the buffer and send this packet
            packet = self.buffer.popleft()
            self.send_packet(curr_time, packet)
            


