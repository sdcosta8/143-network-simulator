from utils import (
    DEBUG, RENO, PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)
from math import ceil
import random

class Flow:

    def __init__(self, size, source, destination, time_spawn, window, protocol,
                 id, network):

        # The time at which the flow is initialized
        self.time_spawn = time_spawn
        # The flow id for the flow represented as an integer
        self.id = id
        # The total size of the flow. Lets represent this in bits
        self.size = size
        # The number of packets for the flow
        self.num_packets = ceil(self.size / PACKET_SIZE)
        # The source and destination hosts
        self.source = source
        self.destination = destination
        # Reference to the network object
        self.network = network
        # This value tells us if the flow has been spawned
        self.spawned = False
        # If all packets are acknowledged by receiver
        self.finished = False
        # Field to keep track of current time
        self.curr_time = 0

        # ================ Source host =============================
        # Protocol, "", "RENO" or "FAST"
        self.protocol = protocol
        # Current phase: "SS", "CA", "FR"
        self.tcp_phase = "SS"
        # Slow start threshold
        self.ssthresh = float("inf")
        # alpha for FAST
        self.alpha = 10
        # gamma for FAST
        self.gamma = 0.5
        # Max of all acks' expecting_packet so far
        # Used as reference to reset next_packet_to_send during timeout
        self.expecting_packet = 1
        # Counter for duplicate acks
        self.repeated_ack_count = 0
        # The next packet to send in normal situations
        self.next_packet_to_send = 1
        # Unacknowledged packets of the sender
        self.unack_packets = []
        # The current window size
        self.window = window
        # Most current round trip time
        self.rtt = float("inf")
        self.min_rtt = float("inf")
        # Retransmission timeout time
        # Compared to (curr_time - rto_timer) to determine timeout
        self.rto = 3
        # Timeout timer, reset to curr_time at successful acks and timeouts
        self.rto_timer = 0

        # ================ Destination host ========================
        # Received packets of the receiver
        self.received_packets = {}
        # The smallest packet that the receiver has not received
        self.next_missing_packet = 1

        # ================ Graphing logs ===========================
        # Keep track of the window sizes over time
        self.window_sizes = []
        # keep track of the packet delays (time between spawning and arriving)
        # at destination host
        self.packet_delays = []
        # Flow rate of the bits recived per time step
        self.flow_rates = []
        # Number of packets received over a particular time period
        self.num_packets_received = 0
    

    def send_packets(self):
        '''
        This function will be called at every iteration of the global timer to
        see if there are any packets that can be sent by the flow.
        '''
        # See if any packets can be sent based on window size
        while (len(self.unack_packets) < self.window and
        self.next_packet_to_send <= self.num_packets):
            # Send packet
            self.send_single_packet(self.next_packet_to_send)

            if self.tcp_phase == "FR":
                print(" sent packet", self.next_packet_to_send, "of flow", self.id)

            # Update flow's unacknowledged packets list & next packet to send
            self.unack_packets.append(self.next_packet_to_send)
            self.next_packet_to_send += 1


    def send_single_packet(self, packet_no):
        '''
        Takes the number of the single packet and sends it
        '''
        # Create packet
        pkt = self.network.create_packet(
            PACKET_SIZE, PACKET,
            self.source, self.destination, self.curr_time,
            False, self.source,
            flow=self, packet_no=packet_no,
            last_packet=(packet_no == self.num_packets)
        )
        # Send the packet by adding it to the link
        self.source.outgoing_link.add_packets([pkt])


    def receive_packet(self, pkt):
        '''
        Take a packet/ack that arrives from the link, update the queues
        Send an ack back if a packet is received
        '''
        # See if it is acknowledgement
        if pkt.packet_type == ACK:
            # Check if all the packets in the flow have been received
            if pkt.expecting_packet == self.num_packets + 1:
                self.finished = True
                print("flow no", self.id, "has finished sending")
            
            # Book keeping for resetting during a timeout
            self.expecting_packet = pkt.expecting_packet

            # Calculate RTT and update RTO
            # Note that time_spawn of ack is of time spawn of original pkt
            self.rtt = self.curr_time - pkt.time_spawn
            if self.rtt < self.min_rtt:
                self.min_rtt = self.rtt
            self.update_rto()

            # Update dup ack count
            if self.expecting_packet != pkt.expecting_packet:
                self.expecting_packet = pkt.expecting_packet
                self.repeated_ack_count = 0
            else:
                self.repeated_ack_count += 1

            # If 0th packet is acked, remove all packets before expecting pkt
            while (len(self.unack_packets) > 0 and
            self.unack_packets[0] < pkt.expecting_packet):
                self.unack_packets.pop(0)
                self.repeated_ack_count = 0

            print(self.tcp_phase, "ack", pkt.expecting_packet,
                  "curr_time:", self.curr_time,
                  "RTT:", self.rtt,
                  "W:", self.window,
                  "dup ack:", self.repeated_ack_count,
                  self.unack_packets[:3])
            # print("  rto_timer:", self.rto_timer, "RTO:", self.rto)

            # Update window size if we are using RENO
            if self.protocol == "RENO":
                self.update_flow_control_ack()

        # Check if the received object is a packet
        elif pkt.packet_type == PACKET:
            # update dictionary for received packets
            self.num_packets_received += 1
            self.received_packets[pkt.packet_no] = True
            self.packet_delays.append([self.curr_time, self.curr_time - pkt.time_spawn])       
            if DEBUG:
                print(" host no", self.destination.id,
                      "received packet number", pkt.packet_no,
                      "of flow", pkt.flow.id, "from host no", pkt.source.id,
                      self.curr_time)

            # Create an acknowledgement for the packet
            while self.next_missing_packet in self.received_packets:
                self.next_missing_packet += 1
            ack_packet = self.network.create_packet(
                ACK_SIZE, ACK,
                pkt.destination, pkt.source, pkt.time_spawn,
                False, pkt.destination,
                flow=self,
                expecting_packet=self.next_missing_packet
            )
            # Send the packet by adding it to the link
            self.destination.outgoing_link.add_packets([ack_packet])


    def check_for_timeouts(self):
        '''
        This function checks if the flow has timed out
        If so, resend the earliest lost packet and update window size
        '''
        if (self.curr_time - self.rto_timer) >= self.rto:
            # If this flow has timed out, update flow control
            print("timeout occured")
            self.update_flow_control_rto()
            print("next_packet_to_send", self.next_packet_to_send)
            self.window_sizes.append([self.curr_time, self.window])


    def update_rto(self):
        '''
        Update retransmission timeout time based on the most current RTT.
        Upperbound = 60 sec
        Lowerbound = 1 sec
        '''
        self.rto = min(60, max(1, self.rtt * 2))
        if DEBUG:
            print(" update_rto RTO:", self.rto)


    def update_flow_control_rto(self):
        ''' 
        Update window size and thresholds according to protocol,
        upon a retransmission timeout.
        Set ssthresh to max(W/2, 2), reset W
        '''
        self.rto *= 2
        self.rto_timer = self.curr_time
        if self.protocol == "RENO":
            self.ssthresh = max(self.window / 2, 2)
            self.window = 1
            self.next_packet_to_send = self.expecting_packet
            self.unack_packets = []
            self.tcp_phase = "SS"

        self.window_sizes.append([self.curr_time, self.window])
        if DEBUG:
            print(" Timeout", self.curr_time, " W:", self.window, "ssthresh:",
                  self.ssthresh, "repeated ack:", self.repeated_ack_count)


    def update_flow_control_fast(self):
        '''
        This function is called periodically to update the window size according
        to FAST protocol.
        '''
        if self.protocol != "FAST":
            print("Should not update window periodically when FAST is not used!")
            return
        
        self.window = min(
            2 * self.window,
            (1-self.gamma) * (self.window) + 
            (self.gamma) * (self.min_rtt / self.rtt * self.window + self.alpha)
        )


    def update_flow_control_ack(self):
        ''' 
        Update window size and thresholds according to RENO protocol,
        upon receiving an acknowledgement.
        '''	
        if self.protocol != "RENO":
            print("Should not update window upon ack when RENO is not used!")
            return

        # Reset rto timer upon successful ack or 3 dup ack (?)
        if self.repeated_ack_count == 0 or self.repeated_ack_count == 3:
            self.rto_timer = self.curr_time
            
        if self.tcp_phase == "SS":
            # in slow start SS phase
            if self.repeated_ack_count >= 3:
                # 3 duplicate ack, enter frfr
                print("duplicate acks")
                self.ssthresh = max(self.window / 2, 2)
                self.window = self.ssthresh + 3
                self.tcp_phase = "FR"
                # Resend the lost packet
                self.send_single_packet(self.expecting_packet)
                print(" sent packet", self.expecting_packet, "of flow", self.id)
            if self.window + 1 >= self.ssthresh:
                # if reach ssthresh, enter CA
                self.window = self.ssthresh
                self.tcp_phase = "CA"
            elif self.repeated_ack_count == 0:
                # still SS, increment window
                self.window += 1
            
        elif self.tcp_phase == "CA":
            # in congestion avoidance CA (linear) phase
            if self.repeated_ack_count == 0:
                self.window += 1 / self.window
            elif self.repeated_ack_count >= 3:
                print("duplicate acks")
                # 3 duplicate ack, enter frfr
                self.ssthresh = max(self.window / 2, 2)
                self.window = self.ssthresh + 3
                self.tcp_phase = "FR"
                # Resend the lost packet
                self.send_single_packet(self.expecting_packet)
                print(" sent packet", self.expecting_packet, "of flow", self.id)

        elif self.tcp_phase == "FR":
            # in fast recovery (exponential) phase
            # exit fr if window is large enough or get successful ack
            if (self.repeated_ack_count == 0 or
            self.window + 1 >= 3 * self.ssthresh - 1):
                # if we reach the end of frfr, go back to ss or ca
                # if self.window < self.ssthresh:
                #     self.tcp_phase = "SS"
                # else:
                #     self.tcp_phase = "CA"
                self.tcp_phase = "CA"
                self.window = self.ssthresh
            else:
                # still in frfr, increase exponentially
                self.window += 1

        else:
            print("flow id", self.id, 
                    "is in unknown phase of RENO: '" + self.tcp_phase + "'")


    def run(self, curr_time):
        '''
        Called by the network at every interruption
        Handle congestion control. We want to check if the current
        time is the spawn time and we want to intialize the flow. Also,
        we want to adjust the window size of the flow.
        '''
        # Update internal clock
        self.curr_time = curr_time
        
        # Check if this flow should be initialized
        if self.spawned == False:
            if self.curr_time >= self.time_spawn:
                self.spawned == True
            else:
                return
        
        if not self.finished:
            # Check to send packets
            self.send_packets()
            self.check_for_timeouts()
        
        # periodically update window size
        if self.protocol == "FAST" and self.network.counter % 1000 == 0:
            self.update_flow_control_fast()

        # use this so that we dont get every point
        if self.network.counter % 500 == 0:
            self.window_sizes.append([self.curr_time, self.window])
        if self.network.counter % 5000 == 0:
            if len(self.flow_rates) != 0:
                self.flow_rates.append([curr_time - (1000 * self.network.timestep), \
                    (self.num_packets_received * PACKET_SIZE) / 1000 * self.network.timestep])
            self.flow_rates.append([curr_time, (self.num_packets_received * PACKET_SIZE) / \
                1000 * self.network.timestep])
            self.num_packets_received = 0 
        
        
            
