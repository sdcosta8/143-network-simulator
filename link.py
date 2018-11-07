from collections import deque
from utils import (
    DEBUG, RENO, TIMESTEP,
    PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)


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

        # Field to keep track of current time
        self.curr_time = 0

        # Use this to keep track of the buffer occupancy over time. 
        # Should map timestamp to number of packets
        self.buffer_occupancy = {}

        # Keep track of the packet loss in this link
        self.packet_loss = {}

        # Keep track of the link rates over time. this should be the 
        # number of bits sent over the timestep
        self.link_rates = {}
        


    def add_packets(self, packets):
        '''
        Takes a list of packets, puts them into the link buffer.
        This function will be called by connection1
        '''
        # Check if the buffer will be full
        buffer_used = 0
        for pkt in self.buffer:
            buffer_used += pkt.num_bits
        
        for pkt in packets:
            buffer_used += pkt.num_bits
            # If we have space, put packet in the buffer
            if buffer_used < self.queue_capacity:
                self.buffer.append(pkt)
            else:
                # We don't need to do anything with the packet reference, but we 
                # should keep track that a packet was dropped at this timestamp
                self.network.packet_loss[curr_time] += 1
            pkt.curr_pos = self
        # TODO: Update the congestion and dynamic cost pf the link and bit rate? 


    def send_packet(self, packet):
        '''
        Takes a packet that is popped from the buffer and schedule it for
        transimision.
        '''
        arrival_time = (
            self.curr_time + 
            (packet.num_bits / self.bit_rate) + 
            self.prop_time)
        self.traveling_packets.append((arrival_time, packet))

    
    def finish_sending_packet(self, packet):
        '''
        This function will be invoked when the packet is supposed to 
        finish sending. 
        '''
        # Tell connection2 that the packet has arrived
        self.connection2.receive_packet(packet)
        packet.curr_pos = self.connection2
        # TODO: The dynamic cost of the link should be updated


        # Link rate = total bits from packets so far + bits of this 
        # packet / TIMESTEP
        self.link_rates[curr_time] = ((self.link_rates[curr_time] * \
            TIMESTEP) + packet.num_bits) / TIMESTEP
        

    def run(self, curr_time):
        '''
        Called by the network at every interruption
        Check queues to see if any packets has arrived
        '''
        # Update internal clock
        self.curr_time = curr_time
        self.packet_loss[curr_time] = 0
        self.link_rates[curr_time] = 0 

        # Check traveling packets and see if any packet should arrive
        while len(self.traveling_packets) > 0:
            arrival_time, packet = self.traveling_packets[0]
            # If this packet should arrive at connection2
            if arrival_time <= self.curr_time:
                self.traveling_packets.popleft()
                self.finish_sending_packet(packet)
            else:
                break
        
        # Check if the capacity is reached to send packets from buffer
        # Number of bits we are planning to send
        bits_planning = 0
        # Number of more bits we can send at this time
        bits_capacity = self.capacity * TIMESTEP
        for _, packet in self.traveling_packets:
            bits_capacity -= packet.num_bits
        while len(self.buffer) > 0:
            bits_planning += self.buffer[0].num_bits
            # If we cannot send this packet, break
            if bits_planning > bits_capacity:
                break
            # If we can, pop it off of the buffer and send this packet
            packet = self.buffer.popleft()
            self.send_packet(packet)

        self.buffer_occupancy[curr_time] = len(self.buffer)


