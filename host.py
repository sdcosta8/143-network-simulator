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
        self.incoming_link = None
    
        self.outgoing_link = None
    
        # Initialize the recieved acknowledgements queue. This will hold all 
        # the acknowledgements of the packets that this host sent, so it can 
        # keep track of the acknowledgements that it recieves from other hosts
        self.recieved_ack = deque()      
        
        # Initialize the flows list. This will hold all 
        # the current flows that originate from this host
        self.flows = []    
    
        self.waiting_flows = []
    
        # This is the time that a host will wait for an acknowledgement to
        # come back after it sends a packet. If this time is exceeded, the host
        # will resend the packet
        self.maximum_wait_time = 15

        # Field to keep track of current time
        self.curr_time = None
    
    
    def recieve_packet(self, pkt):
        '''
        This function will take in a packet that arrives from the link and then
        updates the queues depending on if the packet recieved is part of a flow
        or an acknowledgement. If it is not an acknowledgement the host will 
        send an acknowledgement back.
        '''
        
        # Recieve packet and see if it is acknowledgement
        if pkt.packet_type == 1:
            # This means that the packet that the host recieves is an ack
            
            # First we want to check that the ack is not associated with a 
            # timeout, which is something that should probably never happen if 
            # the timeout is set accurately
            if pkt.acknowledgement_of_pkt not in self.sent_packets:
                # This acknowledgement corresponds to a dropped packet and we
                # just want to ignore it and move on
                if DEBUG:
                    print(" recieved a dropped pkt ack for {0} in_flow {1}".\
                        format(pkt.id, pkt.flow.id))
                return
            
            # Remove the corresponding packet from the sent packet queue
            for index in range(len(self.sent_packets)):
                # check if the packet objects are the same to find the packet 
                # that the acknowledgement references
                if self.sent_packets[index] == pkt.acknowledgement_of_pkt:
                    if DEBUG:
                        print(" acknowlegement for pkt.id {0} and pkt.no {1} \
                        in_flow {2} recieved".format(pkt.id, pkt.no, pkt.flow.id))
                    
                    # remove the packet from the sent queue
                    del self.sent_packets[index]
                    
                    # add packet to the recieved acknowledgement queue
                    #### I dont think we need this queue tbh ####
                    self.recieved_ack.append(pkt.acknowledgement_of_pkt)
                    
                    # Now we want to update the flow information
                    
                    # Add the packet to the finished round trip packets 
                    pkt.acknowledgement_of_pkt.flow.finished_packets.append(
                        pkt.acknowledgement_of_pkt)
                    
                    # if RENO:	
                    #     # This will come in handy for reno and other protocols to
                    #     # see if we have 3 duplicate ack
                    #     if (pkt.acknowledgement_of_pkt.packet_no == 
                    #         (flow.finished_packets.next_expected_packet_no + 1)):
                    #         ## TODO implement protocols
                    #         pass
                    
                    # Update the window size of the successfully recieved packet 
                    # of the flow
                    pkt.acknowledgement_of_pkt.flow.update_window_size_increase()
                    
                    # check if this packet is the last packet sent and all the
                    # other packets in the flow have been recieved
                    if pkt.acknowledgement_of_pkt.flow.all_packets_recieved():
                    
                        # Change the value to show that flow successfully sent
                        pkt.acknowledgement_of_pkt.flow.RT_success = True
                        
                        if DEBUG:
                            print (" flow no {0} has finished sending".format(\
                                pkt.acknowledgement_of_pkt.flow.id))
        
        # Check if the recieved object is a packet
        elif pkt.packet_type == 0:
            if DEBUG:
                print ( "host no {0} recieved packet number {1} of flow {2} "\
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
            
        
        # Check if the recieved object is a message
        elif pkt.packet_type == 2:
            ### I dont think we need to do anything with the message if a 
            ### host recieves it because it is important for the routers and
            ### links only I thought.
            return 	    
        
        else:
            if DEBUG:
                print ("host id {0} recieved incorrect packet type").\
                    format(self.id)	    
        
    
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
        recieved for protocols like Reno. 
        We will just check when an acknowledgment is recieved that the last 3 
        acknowledgments recieved for a given flow are not the same and if they 
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
