import sys
import json
from network import Network
from host import Host
import graphing_functions as graph
from utils import (
    DEBUG, MB, KB, Mb, RENO, MESSAGE_SIZE
)

# This will find the minimum time step for each iteration based on the 
# smallest time that it takes for a message to be propogated through a link
# or a message to be transmited
def find_time_step(lst_link_delay, lst_prop):
    current_time = 0.0
    minimum_time = 1000000000000
    for link_delay in lst_link_delay:
        current_time = (MESSAGE_SIZE / link_delay) 
        if current_time < minimum_time:
            minimum_time = current_time 
    
    for prop in lst_prop:
        current_time = prop 
        if current_time < minimum_time:
            minimum_time = current_time    
    return minimum_time

def convert_to_bits(num, units):
    if units == MB:
        return num * 8e6
    if units == KB:
        return num * 8e3
    if units == Mb:
        return num * 1e6

# Converts a number in ms to s
def convert_to_seconds(ms):
    return ms * 0.001


def run_simulation(filename):
    network = Network()

    with open(filename) as f:
        net_data = json.load(f)

    for host in net_data["hosts"]:
        # Note: we will add the links to the host when we initialize links
        network.create_host(host["ip"], int(host["id"]))

    for router in net_data["routers"]:
        # Note: we will add the links to the router when we initialize links
        network.create_router(router["ip"], int(router["id"]))

    for flow in net_data["flows"]:
        src = network.hosts[int(flow["source"])]
        dest = network.hosts[int(flow["dest"])]
        new_flow = network.create_flow(
            convert_to_bits(float(flow["data_amount"]), MB),
            src, dest,
            float(flow["start_time"]),
            float(flow["window"]),
            flow["protocol"],
            int(flow["id"]))
        src.flows.append(new_flow)

    # Keep track of this so we can add links going the opposite direction
    highest_link_id = max([int(link["id"]) for link in net_data["links"]])
    for link in net_data["links"]:

        if link["source"][0] == "H":
            src = network.hosts[int(link["source"][1])]
            if  net_data["routers"] != []:
                src.router = network.routers[int(link["sink"][1])]
        else:
            src = network.routers[int(link["source"][1])]

        if link["sink"][0] == "H":
            sink = network.hosts[int(link["sink"][1])]
            if  net_data["routers"] != []:
                sink.router = network.routers[int(link["source"][1])]
        else:
            sink = network.routers[int(link["sink"][1])]

        new_link_1 = network.create_link(src, sink, \
            convert_to_bits(float(link["buff_size"]), KB), \
            convert_to_bits(float(link["link_rate"]), Mb), \
            convert_to_seconds(float(link["prop_delay"])), int(link["id"]))
        new_link_2 = network.create_link(sink, src, \
            convert_to_bits(float(link["buff_size"]), KB), \
            convert_to_bits(float(link["link_rate"]), Mb), \
            convert_to_seconds(float(link["prop_delay"])), highest_link_id + 1)
        network.correspond_links[new_link_1] = new_link_2
        network.correspond_links[new_link_2] = new_link_1
        highest_link_id += 1

        if isinstance(src, Host):
            src.outgoing_link = new_link_1
            src.incoming_link = new_link_2
        else:
            src.outgoing_links.append(new_link_1)
            src.incoming_links.append(new_link_2) 
            src.neighbors.append(sink)
        if isinstance(sink, Host):
            sink.outgoing_link = new_link_2
            sink.incoming_link = new_link_1
        else:
            sink.outgoing_links.append(new_link_2)
            sink.incoming_links.append(new_link_1) 
            sink.neighbors.append(src)

    # In Debug mode, we want to print out all the fields we set at initialization
    if DEBUG:
        print("\n")
        print("Printing state of network at initialization time.")
        links_list = list(network.links.items())
        if (len(links_list) > 0):
            print("\n")
            print("________Links________")
        for link_id, link in links_list:
            print("Printing out fields for Link " + str(link_id) + ".")
            print("    Capacity: " + str(link.capacity))
            print("    Source IP Address: " + str(link.connection1.ip))
            print("    Destination IP Address: " + str(link.connection2.ip))
            print("    Propogation Time: " + str(link.prop_time))
            print("    Queue Capacity: " + str(link.queue_capacity))

        hosts_list = list(network.hosts.items())
        if (len(hosts_list) > 0):
            print("\n")
            print("________Hosts________")
        for host in hosts_list:
            host_id = host[0]
            print("Printing out Fields for Host " + str(host_id) + ".")
            print("    IP Address: " + str(host[1].ip))
            print("    ID of Links to/from Host:")
            print("    " + str(host[1].incoming_link.id))
            print("    " + str(host[1].outgoing_link.id))
            print("    ID of Flows from Host:")
            for flow in host[1].flows:
                print("    " + str(flow.id))
            if host[1].router:
                print("    ID of connected router: " + str(host[1].router.ip))

        routers_list = list(network.routers.items())
        if (len(routers_list) > 0):
            print("\n")
            print("________Routers________")
        for router in routers_list:
            router_id = router[0]
            print("Printing out Fields for Router " + str(router_id) + ".")
            print("    IP Address: " + str(router[1].ip))
            print("    IDs of Outgoing Links:")
            for link in router[1].outgoing_links:
                print("    " + str(link.id))
            print("    IDs of Incoming Links:")
            for link in router[1].incoming_links:
                print("    " + str(link.id))
            print("    IP Addresses of Neighbors:")
            for neighbor in router[1].neighbors:
                print("    " + str(neighbor.ip))


        flows_list = list(network.flows.items())
        if (len(flows_list) > 0):
            print("\n")
            print("________Flows________")
        for flow in flows_list:
            flow_id = flow[0]
            print("Printing out Fields for Flow " + str(flow_id) + ".")
            print("    Number of Bits: " + str(flow[1].size))
            print("    Source IP Address: " + str(flow[1].source.ip))
            print("    Destination IP Address: " + str(flow[1].destination.ip))
            print("    Time Spawned " + str(flow[1].time_spawn))
            print("    Window Size: " + str(flow[1].window))
            print("    Protocol: " + str(flow[1].protocol))

    # This will find the minimum time step for each iteration 
    lst_link_prop = []
    lst_link_rate = []
    links_list = list(network.links.items())
    for links in links_list:
        lst_link_rate.append(links[1].capacity)
        lst_link_prop.append(links[1].prop_time)    
    timestep = find_time_step(lst_link_rate, lst_link_prop)
    network.timestep = timestep

    # Start the network!
    network.run_network()

    # Get the values for the calculations each link keeps track of
    # Convert to a list so that we can index each item 
    links_list = list(network.links.items())
    size = len(links_list) / 2
    packet_loss_dicts = []
    buffer_occ_dicts = []
    link_rate_dicts = []
    link_order = []

    start_index = 0 not in network.links
    for element in links_list:
        if element[0] < size + start_index:
            name = 'L' + str(element[0]) + '_right'
        else:
            name = 'L' + str(int(element[0] % size) + start_index) + '_left'
        link_order.append(name)
        packet_loss_dicts.append(element[1].packet_loss)
        buffer_occ_dicts.append(element[1].buffer_occupancy)
        link_rate_dicts.append(element[1].link_rates)

    # Get the values for the calculations each flow keeps track of 
    flow_list = list(network.flows.items())
    wind_size_dicts = []
    flow_rate_dicts = []
    packet_delay_dicts = []
    flow_order = []
    for element in flow_list:
        flow_order.append("F" + str(element[0]))
        wind_size_dicts.append(element[1].window_sizes)
        flow_rate_dicts.append(element[1].flow_rates)
        packet_delay_dicts.append(element[1].packet_delays)

    # For tests 3 and 4, different flows have different protocols. In other cases,
    # we want to label the graphs with the protocols they follow
    protocol = ""
    if filename.split('.')[0] != 'test3' and filename.split('.')[0] != 'test4':
        protocol = flow_list[0][1].protocol

    # Send the plots to the graphing function 
    graph.create_graphs(buffer_occ_dicts, packet_loss_dicts, network.curr_time, \
        link_rate_dicts, wind_size_dicts, flow_rate_dicts, packet_delay_dicts, \
        link_order, flow_order, filename.split('.')[0], protocol, network.curr_time + 1)


if __name__ == '__main__':
    filename = sys.argv[1]
    run_simulation(filename)
