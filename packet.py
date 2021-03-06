from utils import (
    DEBUG, RENO,
    PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)

class Packet:

    def __init__(self, num_bits, packet_type, source, destination, 
        time_spawn, in_transit, curr_pos, network,
        flow, packet_info, packet_no, last_packet, 
        expecting_packet):

        # Reference to the network object
        self.network = network

        # number of bits in the packet. should be Packet.PACKET_SIZE, 
        # Packet.MESSAGE_SIZE, or Packet.ACK_SIZE
        self.num_bits = num_bits

        # packet_type should be Packet.PACKET, Packet.ACK, or Packet.MESSAGE
        self.packet_type = packet_type

        # A reference to the host from which the packet spawned
        self.source = source

        # A reference to the destination host
        self.destination = destination

        # The time that this packet was spawned.
        # If this is ack, the time the original packet was spawned.
        self.time_spawn = time_spawn

        # 0 if the packet is at a host or router. 1 if the packet is in a link
        self.in_transit = in_transit

        # Reference to the object (link, host, or router) that the packet 
        # is currently in
        self.curr_pos = curr_pos

        # This should be a reference to the flow object or None. For the cases
        # where routers are passing messages to determine shortest path, the 
        # packets won't have a flow id 
        self.flow = flow

        # If self is ack, the next packet the receiver is expecting
        self.expecting_packet = expecting_packet

        # For message passing, this will be the information used for the 
        # shortest path algorithm represented as an array. For other packet 
        # types, this is None
        self.packet_info = packet_info

        # The packet number relative to the start of the flow. This will be 
        # none if the packet doesn't have a flow id
        self.packet_no = packet_no

        # 1 if the packet is the last packet in the flow. 0 otherwise. This
        # should be none if the packet doesn't have a flow id
        self.last_packet = last_packet

        # This should be the time that the last curr_pos object started sending
        # the packet
        self.time_sent = None

        # The next time at which we should do something with the packet. This should 
        # be calculated outside of the packet class 
        self.time_next_move = None
        
        # Time in received packets queue
        self.time_in_queue = None

        self.current_cost = 0.0
        
        self.prev_link = None