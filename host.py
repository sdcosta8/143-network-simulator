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
        self.received_packets = deque()
        
        # Initialize the outgoing packets queue. This will hold all the packets
        # that the host needs to send, which will be based on the window size
        self.outgoing_packets = deque()
        
        # All packets that are sent but have not received acknowledgements
        self.sent_packets = deque()
        
        # The link object that the host is connected to         
        self.incoming_link = None
    
        self.outgoing_link = None
    
        # Initialize the received acknowledgements queue. This will hold all 
        # the acknowledgements of the packets that this host sent, so it can 
        # keep track of the acknowledgements that it receives from other hosts
        self.received_ack = deque()      
        
        # Active flows
        self.flows = []
        # Flows that have not been spawned
        self.waiting_flows = []
    
        # This is the time that a host will wait for an acknowledgement to
        # come back after it sends a packet. If this time is exceeded, the host
        # will resend the packet
        self.maximum_wait_time = 15

        # Field to keep track of current time
        self.curr_time = None
    
    
    def receive_packet(self, pkt):
        '''
        Take a packet/ack that arrives from the link, update the queues
        Send an ack back if a packet is received
        '''
        # See if it is acknowledgement
        if pkt.packet_type == ACK:
            orig_pkt = pkt.acknowledgement_of_pkt

            # Find the index of original packet in sent packets
            try:
                index = self.sent_packets.index(orig_pkt)
            except ValueError:
                # When a timeout happens, sent packets is cleared.
                # If the ack is for a packet cleared during a timeout, ignore
                if DEBUG:
                    print(" received a dropped pkt ack for {0} in_flow {1}".
                          format(pkt.id, pkt.flow.id))
                return

            if DEBUG:
                print(" acknowlegement for pkt.id {0} and pkt.no {1} \
                in_flow {2} received".format(pkt.id, pkt.no, pkt.flow.id))

            # Remove the packet from the sent queue
            del self.sent_packets[index]
                    
            # add packet to the received acknowledgement queue
            #### I dont think we need this queue tbh ####
            self.received_ack.append(orig_pkt)
            
            # Add the packet to the finished round trip packets of the flow
            orig_pkt.flow.finished_packets.append(orig_pkt)
            
            if RENO:
                # This will come in handy for reno and other protocols to
                # see if we have 3 duplicate ack
                if (orig_pkt.packet_no == 
                    orig_pkt.flow.next_expected_packet_no + 1):
                    ## TODO implement protocols
                    pass
            
            # Update the window size of the flow
            orig_pkt.flow.update_window_size_increase()
            
            # Check if all the packets in the flow have been received
            if orig_pkt.flow.all_packets_received():
                # Change the value to show that flow successfully sent
                orig_pkt.flow.RT_success = True
                if DEBUG:
                    print(" flow no {0} has finished sending".format(\
                        orig_pkt.flow.id))
        
        # Check if the received object is a packet
        elif pkt.packet_type == PACKET:
            if DEBUG:
                print (" host no {0} received packet number {1} of flow {2} "\
                        + " from host no {3}").format(self.id, pkt.packet_no, \
                                                    pkt.flow, pkt.source)
            
            # Create an acknowledgement for the packet 
            ack_packet = self.network.create_packet(
                ACK_SIZE, ACK,
                pkt.destination, pkt.source, self.curr_time,
                self, acknowledgement_of_pkt=pkt)	    
            
            # Put this acknowledgment into the outgoing packets queue of the 
            # host to be sent
            self.outgoing_packets.append(ack_packet)
            
            ##### DO we have to move the acknowledgement packet to the 
            ##### sent queue, I want to say no because we dont care if it is 
            ##### dropped
            
            if DEBUG:
                print ( "acknowledgement packet for pkt no {0} flow {1} was \
                placed in host {2}'s  outgoing queue to be sent").\
                    format(pkt.packet_no, pkt.flow, self.id)		
            
        
        # Check if the received object is a message
        elif pkt.packet_type == 2:
            ### I dont think we need to do anything with the message if a 
            ### host receives it because it is important for the routers and
            ### links only I thought.
            return
        
        else:
            if DEBUG:
                print ("host id {0} received incorrect packet type {1}").\
                    format(self.id, pkt.packet_type)	    
        
    
    def send_packets(self):
        '''
        This function will be called at every iteration of the global timer to
        see if there are any packets that can be sent by the host.
        '''
        # See if there are any packets to be sent by the host
        if len(self.outgoing_packets) == 0:
            return
        
        for packet in self.outgoing_packets:
            # Get the flow info for the packet in the outgoing queue
            flow_of_packet = packet.flow
            
            # Check the flows current window size and see if it is
            # possible to send more packets	
            #### TODO (?)
            #### instead of comparing window to max window
            #### we should compare the number of sent packets to current window
            #### max window should only be relevant to window control protocol
            if flow_of_packet.current_window <= flow_of_packet.max_window:
            
                # Remove the packet from outgoing queue because it can be sent
                pkt = packet
                
                # Delete the packet from the outgoing queue
                self.outgoing_packets.remove(pkt)
                
                
                # We want to send the packet
                self.outgoing_link.append(pkt)
                
                # Place the packet on to the sent queue
                self.sent_packets.append(pkt)
                
                # Update the packets timer in the queue
                pkt.time_in_queue = 0
                
                # Update the window size for the flow by adding one to it
                flow_of_packet.window_size_update_when_pkt_sent()
                
                if DEBUG:
                    print ("sent packet = " + pkt.id + "of flow id = " + flow_of_packet.id)
                    print("flow's window size is " +  flow_of_packet.current_window)
        

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
        
        # Go through the packets in the queue and update their waiting times in
        # the queue
    
        for index in range(len(self.sent_packets)):
            packet = self.sent_packets[index]
            packet.time_in_queue += 1

        # Go through again and check if any of the packets have been waiting 
        # for an acknowledgement that they should be timed out 
        for packet in self.sent_packets:
            if packet.time_in_queue > self.maximum_wait_time:
                # We want to remove the packet from the sent queue and resend 
                # it 
                ### I just reset the fields of the packet and put it in the 
                ### outgoing packet queue of the host to simulate "resending"
                self.sent_packets.remove(packet)
                packet.time_spawn = self.curr_time
                packet.curr_pos = packet.source
                packet.sent = None
                packet.time_next_move = None
                packet.time_in_queue = None
                
                # Put the timed out packet back into the outgoing packet queue
                self.outgoing_packets.append(packet)
                if DEBUG:
                    print ( " pkt no {0} flow {1} has timed out and was \
                    placed in host {2}'s  outgoing queue to be sent").\
                    format(packet.packet_no, packet.flow, self.id)			
        
    
    
    def check_for_three_ack(self):
        '''
        This function we want to see if a three of the same acknowledgements are
        received for protocols like Reno. 
        We will just check when an acknowledgment is received that the last 3 
        acknowledgments received for a given flow are not the same and if they 
        are we should perform the appropriate update to the window size for our
        protocol.
        '''    
        
        pass

    def run(self, curr_time):
        '''
        Called by the network at every interruption
        Check queues to see if any packets can be sent
        '''
        # Update internal clock
        self.curr_time = curr_time

        # Check if any sent packets exceed the timeout
        self.check_for_timeouts()

        # See if it is possible to send any packets from the host's outgoing 
        # queue
        self.send_packets()

        pass
