from utils import (
    DEBUG, RENO, PACKET_SIZE, ACK_SIZE, MESSAGE_SIZE, PACKET, ACK, MESSAGE
)

class Flow:

    def __init__(self, size, source, destination, time_spawn, max_window,
                 id, network):

        # The total size of the flow. Lets represent this in bits
        self.size = size

        # The source host where the flow spawns
        self.source = source

        # The destination host where the flow should arrive
        self.destination = destination

        # The time at which the flow is initialized
        self.time_spawn = time_spawn

        # Max window size
        self.max_window = max_window

        # The flow id for the flow represented as an integer
        self.id = id

        # Reference to the network object
        self.network = network

        # 0 if packets from the flow are still in transit. 1 if the 
        # whole round trip of the flow is done
        self.RT_success = 0

        # A list of packets that have successfully made the round trip
        self.finished_packets = []

        # The number of packets for the flow
        self.num_packets = 0

        # A list of packets for the flow
        self.packets = []
        
        self.current_window = 0
        
        # This value tells us if the flow has been spawned
        self.spawned = False
        
        # This will be the packet that the flow expects next, which will
        # help with future protocols
        self.next_expected_packet_no = 0

        # Field to keep track of current time
        self.curr_time = None


    def construct_packets(self):
        '''
        Break the flow into packets
        Return a list of packets
        '''
        assert(self.size % PACKET_SIZE == 0)

        packets = []
        self.num_packets = self.size / PACKET_SIZE

        # Index the packets starting at 1
        for i in range(1, self.num_packets + 1):
            new_packet = self.network.create_packet(
                PACKET_SIZE, PACKET,
                self.source, self.destination, 0,
                self.source, flow=self, packet_no=i)
            packets.append(new_packet)

        # Set the last packet's flag
        packets[len(packets) - 1].last_packet = 1
        return packets
    
    def initialize_flow(self):
        '''
        Construct packets, update source host on status of new outgoing packets
        and this flow
        Called when the flow spawn time equals the current time
        '''
        # Split up the flow into packets
        self.packets = self.construct_packets()
        
        # Need a for loop because don't want to append a list to another
        # list and create a list of lists
        for packet in self.packets:
            self.source.outgoing_packets.append(packet)
        
        # We want to remove the flow from the waiting flow array of the 
        # host and place it into the active flow object
        try:
            self.source.waiting_flows.remove(self)
            self.source.flows.append(self)
            if DEBUG:
                print(" removed flow id:" + self.id)
        except ValueError:
            print(" ERROR: FLOW NOT FOUND IN THE WAITING QUEUE")
            
    def calc_send_receive_rate(self):
        '''
        Calculated as the bits of the flow received over time?
        '''
        # TODO 
        pass 


    def calc_RT_delay(self):
        '''
        The delta between the flow initialized and a packet's acknowledgement
        being received by the host that initialized the flow
        '''
        # TODO
        pass

    # Window size protocol function
    def window_protocol_decrease(self):
        ''' 
        This function will be called from the host, when it experiences
        a timeout for a packet that belongs to this flow or it receives
        3 of the same acknowlegdments. Based on the protocol, the window 
        size of the flow will be updated appropriately. This will be 
        implemented, when we decide which protocols to use for each flow
        '''
        pass

    def window_size_update_when_pkt_sent(self):
        ''' 
        This is the function that will be called when a packet is sent
        so we know how the window size changes based on the protocol
        '''
        pass
        
    def update_window_size_increase(self):
        ''' 
        This function will be called from the host, when it receives and 
        acknowledgement and wants to increase the window size 
        '''	
        pass

    def all_packets_received(self):
        '''
        Check if all packets are in finished_packets (ack received)
        Return True/False
        '''
        # Get unique list of finished packets
        packets_received_ack = list(set(self.finished_packets))
        
        # Sort the list of received packets in place by their packet number
        packets_received_ack.sort(key=lambda x: x.packet_no, reverse=True)
        
        # Check if all the packets are received
        all_received = self.num_packets == len(packets_received_ack)
        if DEBUG:
            # Find the packets missing (1 indexed)
            missed_pkt_num =[]
            i = 0
            for num in range(1, self.num_packets+1):
                if (len(packets_received_ack) <= i or 
                packets_received_ack[i].packet_num != num):
                    missed_pkt_num.append(num)
                else:
                    i += 1
            # Check if the result is consistent with quick length check
            if (len(missed_pkt_num) == 0) != all_received:
                print("ALL RECEIVED DOES NOT AGREE WITH TRAVERSAL CHECK.")
            
            # Print info about missed packets
            if len(missed_pkt_num) > 0:
                print("packet no", end=" ")
                for num in missed_pkt_num:
                    print(num, end=" ")
                print("is missing of flow no", self.id)
            else:
                print("All packets for flow no", self.id, "are received")
        
        return all_received
        
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
        if (self.curr_time >= self.time_spawn) and (self.spawned == False):
            self.initialize_flow()
            self.spawned = True
        
        # TODO: Calculate window size W based on congestrion control protocol
        
        
            
