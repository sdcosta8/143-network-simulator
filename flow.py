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
		self.packets = self.construct_packets()


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

	def run(self):
		'''
		Called by the network at every interruption
		Handle congestion control
		'''
		pass