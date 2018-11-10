import sys
import json
import matplotlib.pyplot as plt
from network import Network
from host import Host
from utils import (
    DEBUG, MB, KB, Mb, RENO, TIMESTEP
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
    
    return minimum_time / 4 
    
    

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


# Pass in a  list of dictionary where timestamps are 
# mapped to rates, packet losses, etc.
# The list will be length > 1 in a case where we need
# to plot several series
def add_graph(time_dicts, last_time, y_label, series_labels):
    for i in range(len(time_dicts)):
        time_dict = time_dicts[i]
        series = series_labels[i]
        x_axis = []
        y_axis = []

        time = 0
        while time <= last_time:
            if time in time_dict:
                y_axis.append(time_dict[time])
                x_axis.append(time)
            time += TIMESTEP

        plt.plot(x_axis, y_axis, label=series)
    plt.legend()
    plt.xlabel('Time (secs)')
    plt.ylabel(y_label)
    plt.savefig(label + '.png')
    plt.close


if __name__ == '__main__':
    filename = sys.argv[1]
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
        new_flow = network.create_flow(\
            convert_to_bits(float(flow["data_amount"]), MB), src, dest, \
            float(flow["start_time"]), int(flow["window"]), \
                int(flow["id"]))
        src.flows.append(new_flow)

    # Keep track of this so we can add links going the opposite direction
    highest_link_id = max([int(link["id"]) for link in net_data["links"]])
    for link in net_data["links"]:

        if link["source"][0] == "H":
            src = network.hosts[int(link["source"][1])]
        else:
            src = network.routers[int(link["source"][1])]

        if link["sink"][0] == "H":
            sink = network.hosts[int(link["sink"][1])]
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
            print("    Max Window Size: " + str(flow[1].max_window))

    # This will find the minimum time step for each iteration 
    lst_link_prop = []
    for links in links_list:
        lst_link_rate.append(links.capacity)
        lst_link_prop.append(links.prop_time)    
        TIME_STEP = find_time_step(lst_link_rate, lst_link_prop)


'''
    # Start the network! 
    network.run_network()

    # Get the values for the calculations each link keeps track of 
    links_list = network.links.items()
    packet_loss_dicts = []
    buffer_occ_dicts = []
    link_rate_dicts = []
    link_order = []
    for element in links_list:
        link_order.append("L" + str(element[0]))
        packet_loss_dicts.append(element[1].packet_loss)
        buffer_occ_dicts.append(element[1].buffer_occupancy)
        link_rate_dicts.append(element[1].link_rates)

    # Graph the buffer occupancies over time
    add_graph(buffer_occ_dicts, network.curr_time, "Buffer Occupancy (pkts)", \
        link_order)

    # Graph the packet loss over time
    add_graph(packet_loss_dicts, network.curr_time, "Packet Loss (pkts)", \
        link_order)

    # Graph the link rates
    add_graph(link_rate_dicts, network.curr_time, "Link Rate (bps)", \
        link_order)

    # Get the values for the calculations each flow keeps track of 
    flow_list = network.flows.items()
    wind_size_dicts = []
    flow_rate_dicts = []
    packet_delay_dicts = []
    flow_order = []
    for element in flow_list:
        flow_order.append("F" + str(element[0]))
        wind_size_dicts.append(element[1].window_size)
        flow_rate_dicts.append(element[1].flow_rates)
        packet_delay_dicts.append(element[1].packet_delays)

    # Graph the window size over time
    add_graph(wind_size_dicts, network.curr_time, "Window Size (pkts)", \
        flow_order)

    # Graph the flow rate over time
    add_graph(flow_rate_dicts, network.curr_time, "Flow Rate (bps)", \
        flow_order)

    # Graph the packet delays over time
    add_graph(packet_delay_dicts, network.curr_time, "Packet Delay (sec)")
'''

