from collections import deque
from utils import (
    DEBUG, RENO, PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)

class Host:
    def __init__(self, ip_address, link_connected, id, network):
        # Initialize the ip_address of the host
        self.ip = ip_address
        
        # The id of the host represented as an integer
        self.id = id

        # Reference to the network object
        self.network = network

        # Initialize the received packets queue. This will hold all the packets
        # that the host receives
        # self.received_packets = deque()
        
        # Initialize the outgoing packets queue. This will hold all the packets
        # that the host needs to send, which will be based on the window size
        # self.outgoing_packets = deque()
        
        # All packets that are sent but have not received acknowledgements
        # self.sent_packets = deque()
        
        # The link object that the host is connected to         
        self.incoming_link = None
        self.outgoing_link = None
    
        # Initialize the received acknowledgements queue. This will hold all 
        # the acknowledgements of the packets that this host sent, so it can 
        # keep track of the acknowledgements that it receives from other hosts
        # self.received_ack = deque()
        
        # Flows
        self.flows = []

        # Field to keep track of current time
        self.curr_time = None

        # Keep track of the router that the host is attached to 
        self.router = None
        
    
    def receive_packet(self, pkt):
        '''
        Called by the link.
        Receives a packet. Calls the flow's receive packet function
        '''
        if pkt.packet_type == MESSAGE:
            if DEBUG:
                print(" host " + str(self.id) + " received message from " +
                      str(pkt.source.id) + " with cost of " + str(pkt.current_cost))
            return        
        else:
            pkt.flow.receive_packet(pkt)

    def run(self, curr_time):
        '''
        Called by the network at every interruption
        Check queues to see if any packets can be sent
        '''
        # Update internal clock
        self.curr_time = curr_time

        pass
