from utils import (
    DEBUG, RENO, PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)
from math import ceil
import random

class Flow:

    def __init__(self, size, source, destination, time_spawn, window, protocol,
                 id, network):

        # The total size of the flow. Lets represent this in bits
        self.size = size

        # The source host where the flow spawns
        self.source = source

        # The destination host where the flow should arrive
        self.destination = destination

        # The time at which the flow is initialized
        self.time_spawn = time_spawn

        # The flow id for the flow represented as an integer
        self.id = id

        # Reference to the network object
        self.network = network

        # Ack received, list of repeated expected next packets
        # When the length is 3, timeout and reset
        self.expecting_packet = 1
        self.repeated_ack_count = 0

        # As the destination, what the host is expecting
        self.dest_expecting_packet = 1

        # Reset to expecting_packet when we receive 3 repeated ack
        self.next_packet_to_send = 1
        # All packets that are sent but have not received acknowledgements
        self.sent_times = {}
        
        # The number of packets for the flow
        # pkt.last_packet is True if its num is this num_packets
        self.num_packets = ceil(self.size / PACKET_SIZE)
        
        # The current window size
        self.window = window

        # Retransmission timeout time
        # Compared to (curr_time - rto_timer) to determine timeout
        self.rto = 3
        # Timeout timer, reset to curr_time at successful acks and timeouts
        self.rto_timer = 0
        
        # This value tells us if the flow has been spawned
        self.spawned = False

        # If all packets are acknowledged by receiver
        self.finished = False

        # Field to keep track of current time
        self.curr_time = 0

        # Keep track of the window sizes over time 
        self.window_size = []

        # keep track of the packet delays (time between spawning and arriving)
        # at destination host
        self.packet_delays = []

        # Number of packets received over a particular time period
        self.num_packets_received = 0

        # Flow rate of the bits recived per time step
        self.flow_rates = []

        # Protocol, "", "RENO" or "FAST"
        self.protocol = protocol
        # Current phase for RENO: "SS", "CA", "FR"
        self.tcp_phase = "SS"
        # ssthresh for RENO
        self.ssthresh = float("inf")
        # alpha for FAST
        self.alpha = 10
        # gamma for FAST
        self.gamma = 0.5

        # Most current round trip time
        self.rtt = float("inf")
        self.min_rtt = float("inf")


    def initialize_flow(self):
        '''
        Called when the it's time to spawn
        '''
        self.spawned = True
    

    def send_packets(self):
        '''
        This function will be called at every iteration of the global timer to
        see if there are any packets that can be sent by the flow.
        '''
        # See if any packets can be sent. The cutoff is exclusive
        packet_cutoff = self.expecting_packet + self.window
        while (self.next_packet_to_send < packet_cutoff and
               self.next_packet_to_send <= self.num_packets):
            # We can send more packets
            pkt = self.network.create_packet(
                PACKET_SIZE, PACKET,
                self.source, self.destination, self.curr_time,
                False, self.source,
                flow=self, packet_no=self.next_packet_to_send,
                last_packet=(self.next_packet_to_send == self.num_packets)
            )
            
            # Send the packet by putting it in the link
            self.source.outgoing_link.add_packets([pkt])
            # Record sent time for this packet
            self.sent_times[pkt.packet_no] = self.curr_time
            # Update the flow's info about next packet to send
            self.next_packet_to_send += 1

            if DEBUG:
                print("sent packet", pkt.packet_no, "of flow id", self.id)


    def receive_packet(self, pkt):
        '''
        Take a packet/ack that arrives from the link, update the queues
        Send an ack back if a packet is received
        '''
        
        # See if it is acknowledgement
        if pkt.packet_type == ACK:

            # Calculate RTT and update RTO
            # Note that time_spawn of ack is of time spawn of original pkt
            self.rtt = self.curr_time - pkt.time_spawn
            if self.rtt < self.min_rtt:
                self.min_rtt = self.rtt
            self.update_rto()

            # Update the flow's duplicate ack info
            if self.expecting_packet == pkt.expecting_packet:
                self.repeated_ack_count += 1
            else:
                self.expecting_packet = pkt.expecting_packet
                self.repeated_ack_count = 0
                if (self.expecting_packet - 1) in self.sent_times:
                    del self.sent_times[self.expecting_packet - 1]
            if DEBUG:
                print(" acknowlegement for pkt no", pkt.expecting_packet - 1,
                      "flow", self.id,  "received. RTT:", self.rtt)

            # Update window size if we are using RENO
            if self.protocol == "RENO":
                self.update_flow_control_ack()
            if DEBUG:
                print("", self.tcp_phase, self.curr_time,
                " ack", pkt.expecting_packet - 1, "W:", self.window,
                "repeated ack:", self.repeated_ack_count)

            # Check if all the packets in the flow have been received
            if self.expecting_packet == self.num_packets + 1:
                self.finished = True
                if DEBUG:
                    print(" flow no", self.id, "has finished sending")

        # Check if the received object is a packet
        elif pkt.packet_type == PACKET:
            if pkt.packet_no == self.dest_expecting_packet:
                self.dest_expecting_packet += 1
                self.num_packets_received += 1
            self.packet_delays.append([self.curr_time, self.curr_time - pkt.time_spawn])       
            if DEBUG:
                print(" host no", self.destination.id,
                      "received packet number", pkt.packet_no,
                      "of flow", pkt.flow.id, "from host no", pkt.source.id,
                      self.curr_time)

            # Create an acknowledgement for the packet
            ack_packet = self.network.create_packet(
                ACK_SIZE, ACK,
                pkt.destination, pkt.source, pkt.time_spawn,
                False, pkt.destination,
                flow=self, expecting_packet=self.dest_expecting_packet)

            # Send the packet by putting it in the link
            self.destination.outgoing_link.add_packets([ack_packet])

            if DEBUG:
                print(" acknowledgement packet for pkt no", pkt.packet_no,
                      "flow", self.id, "is sent")


    def check_for_timeouts(self):
        '''
        This function we want to see if a packet was dropped due to a timeout.
        This will occur if the max waiting time of the host is greater than the
        time delta of the time that the packet was sent at.
        '''
        if (self.curr_time - self.rto_timer) >= self.rto:
            # If this flow has timed out, update flow control
            self.update_flow_control_rto()
            self.window_size.append([self.curr_time, self.window])


    def calc_send_receive_rate(self):
        '''
        Calculated as the bits of the flow received over time?
        '''
        # TODO 
        pass 


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
            self.tcp_phase = "SS"

        self.window_size.append([self.curr_time, self.window])
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

        # Reset rto timer upon successful ack
        if self.repeated_ack_count == 0:
            self.rto_timer = self.curr_time
            
        if self.tcp_phase == "SS":
            # in slow start SS phase
            if self.window + 1 >= self.ssthresh:
                # if reach ssthresh, enter CA
                self.window = self.ssthresh
                self.tcp_phase = "CA"
            else:
                if self.repeated_ack_count == 0:
                    # still SS, increment window
                    self.window += 1
            
        elif self.tcp_phase == "CA":
            # in congestion avoidance CA (linear) phase
            if self.repeated_ack_count == 0:
                self.window += 1 / self.window
            elif self.repeated_ack_count >= 3:
                # 3 duplicate ack, enter frfr
                self.ssthresh = max(self.window / 2, 2)
                self.window = self.ssthresh + 3
                self.next_packet_to_send = self.expecting_packet
                self.tcp_phase = "FR"
                self.repeated_ack_count = 0

        elif self.tcp_phase == "FR":
            # in fast recovery (exponential) phase
            if self.window + 1 >= 3 * self.ssthresh - 1:
                # if we reach the end of frfr, go back to linear
                self.window = self.ssthresh
                self.tcp_phase = "CA"
            else:
                if self.repeated_ack_count == 0:
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
                self.initialize_flow()
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
        if self.network.counter % 1000 == 0:
            self.window_size.append([self.curr_time, self.window]) 
            if len(self.flow_rates) != 0:
                self.flow_rates.append([curr_time - (1000 * self.network.timestep), \
                    (self.num_packets_received * PACKET_SIZE) / 1000 * self.network.timestep])
            self.flow_rates.append([curr_time, (self.num_packets_received * PACKET_SIZE) / \
                1000 * self.network.timestep])
            self.num_packets_received = 0 
        
        
            
