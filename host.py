from collections import deque


class Host:
    def __init__(self, ip_address, link_connected, max_window_size, id, network):
        # Initialize the ip_address of the host
        self.ip = ip_address
        
        # The id of the host represented as an integer
        self.id = id

        # Reference to the network object
        self.network = network
        
        # Initialize the recieved packets queue. This will hold all the packets
        # that the host recieves
        self.recieved_packets = deque()
        
        # Initialize the outgoing packets queue. This will hold all the packets
        # that the host needs to send, which will be based on the window size
        self.outgoing_packets = deque()
        
        # Initialize the sent packets queue. This will hold all the packets
        # that are sent but have not recieved acknowledgements
        self.sent_packets = deque()
        
        # The link object that the host is connected to         
        self.links = []
        
        # Initialize the recieved acknowledgements queue. This will hold all 
        # the acknowledgements of the packets that this host sent, so it can 
        # keep track of the acknowledgements that it recieves from other hosts
        self.recieved_ack = deque()      
        
        # Initialize the flows list. This will hold all 
        # the current flows that originate from this host
        self.flows = []    
        
        self.current_window = 0
    
        self.max_window = max_window_size
        
        # This is the time that a host will wait for an acknowledgement to
        # come back after it sends a packet. If this time is exceeded, the host
        # will resend the packet
        self.maximum_wait_time = 15
        
    def initialize_flow(self, size):
        # Initialize the flow, by passing in the size of the transfer of info,
        # and get the packets returned by the flow
        
        # Place packets returned by the flow into the outgoing_packets queue
        
        # Place the flow into the host's flow queue
        pass
    
    
    def recieve_packet(self, pkt):
        '''
        This function will take in a packet that arrives from the link and then
        updates the queues depending on if the packet recieved is part of a flow
        or an acknowledgement. If it is not an acknowledgement the host will 
        send an acknowledgement back.
        '''
        
        # Recieve packet and see if it is acknowledgement
        
        # If it is a packet add it to the recieved packet queue
        # Send an acknowlegment by initalizing an acknowledgment packet and
        # putting it into the outgoing_packets queue. 
        
        # If the packet is an acknowledgement:
        
        # We want to first check that it 
        # is not associated with a timeout that is that the acknowledgment 
        # corresponds with a packet in the sent queue and if it is associated 
        # with a timeout we should just ignore it
        
        # Adjust the current window size
        
        # Add the acknowledgment to the acknowledgment queue for the host
        
        # Remove the packet from the sent packets queue
        
        # Remove the flow from the flow queue
        ##### QUESTION: How do we keep the acknowledge queue from getting
        ##### too big. 
        pass
    
    def send_packets(self):
        '''
        This function will be called at every iteration of the global timer to
        see if there are any packets that can be sent by the host.
        '''
        
        # At the timer interrupt, the host will check its current window size 
        # and see if it is possible to send more packets
        
        # If there are no packets to send or the window size is at its maximum,
        # the function should return
        
        # The packets will then be placed into the sent packets queue from the
        # outgoing queue until the outgoing queue is empty or the max window size
        # is reached ( so we need to update the max window size).
        
        # These newly sent packets should call a method of the host's link 
        # to let it know that packets are waiting to be sent on it so that it 
        # can be put in the link's buffer
        
        # Update the flow information for the packets that are going to be sent
        # in the flow queue for the host
        pass
    
    def check_for_timeouts(self):
        '''
        This function we want to see if a packet was dropped due to a timeout. 
        This will occur if the max waiting time of the host is greater than the
        time delta of the time that the packet was sent at.
        '''
        # Go through the queue of sent packets and see if any of them have a 
        # time stamp ( time that they were sent - current time) that is greater
        # than the max time stamp. If not, you want to update the time stamp for
        # each package by incrementing it for the iteration and then moving to 
        # the next packet. 
        
        # If a packet in the queue has exceeded the timeout time, we want to 
        # remove it from the queue, and place it on the outgoing packets queue
        # in order to be resent. We should also perform the appropriate update 
        # to the window size based on our protocol. We also want to mark 
        # somewhere that this packet has timed out for bookkeeping.
        
        pass
    
    def check_for_three_ack(self):
        '''
        This function we want to see if a three of the same acknowledgements are
        recieved for protocols like Reno. 
        We will just check when an acknowledgment is recieved that the last 3 
        acknowledgments recieved for a given flow are not the same and if they 
        are we should perform the appropriate update to the window size for our
        protocol.
        '''    
        
        pass

    def run(self):
    	'''
		Called by the network at every interruption
        Check queues to see if any packets can be sent
		'''
    	pass
