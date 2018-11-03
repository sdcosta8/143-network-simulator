from packet import Packet
#from network import Network

class Flow:

	def __init__(self, size, source, destination, time_spawn, id, network):

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
	    
		self.max_window = max_window_size	
		
		# This value tells us if the flow has been spawned
		self.spawned = False

	# Used to break the flow into packets
	def construct_packets(self):
		assert(self.size % Packet.PACKET_SIZE == 0)

		packets = []
		self.num_packets = self.size / Packet.PACKET_SIZE

		# Index the packets starting at 1
		for i in range(1, self.num_packets + 1):
			new_packet = self.network.create_packet(
				Packet.PACKET_SIZE, Packet.PACKET,
				self.source, self.destination, 0,
				self.source, flow=self, packet_no=i)
			packets.append(new_packet)

		# Set the last packet's flag
		packets[len(packets) - 1].last_packet = 1
		return packets
	
	def initialize_flow(self):
		'''
		When the flow spawn time equals the current time, we want to 
		intialize the flow by splitting the flow into packets and then
		placing the packets in the corresponding host's outgoing queue,
		so that they can be sent.
		'''
		# Split up the flow into packets
		packets = self.construct_packets()
		
		# Populate the flow with the packets that it is made up of
		self.packets = packets
		
		# Place packets returned by the flow into the
		# outgoing_packets queue
		
		# Need a for loop because don't want to append a list to another
		# list and create a list of lists
		for packet in packets:	
			self.source.outgoing_packets.append(packet)
		
		# Intialize a flow variable, so that it will scope out side of 
		# the for loop below
		flow = None
		
		# We want to remove the flow from the waiting flow array of the 
		# host and place it into the active flow object
		for index in range(len(self.source.waiting_flows)):
			flow = self.source.waiting_flows[index]
			# Find the flow in the hosts 
			if self.id == flow.id:
				del source.waiting_flows[index]
				if DEBUG:
					print(" removed flow id:" + flow.id)
				break
		
		if flow == None:
			print(" ERROR: NO FLOW FOUND IN THE WAITING QUEUE")
		# Add the removed flow to the queues of active flows of the host
		else:
			self.source.flows.append(flow)
			
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
	def window_protocol():
		''' 
		This function will be called from the host, when it experiences
		a timeout for a packet that belongs to this flow or it recieves
		3 of the same acknowlegdments. Based on the protocol, the window 
		size of the flow will be updated appropriately. This will be 
		implemented, when we decide which protocols to use for each flow
		'''
		pass
	def run(self, curr_time):
		'''
		Called by the network at every interruption
		Handle congestion control. We want to check if the current
		time is the spawn time and we want to intialize the flow. Also,
		we want to adjust the window size of the flow.
		'''
		
		if (curr_time >= time_spawn) and (self.spawned == False):
			self.initialize_flow()
			self.spawned = True
		
		
			