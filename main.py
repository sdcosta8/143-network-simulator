import sys
from network import Network
from utils import (
    DEBUG, MB, KB, Mb, RENO
)

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


if __name__ == '__main__':
    args = sys.argv[1:]
    network = Network()

    # The user should pass in the type of object followed 
    # by the number of them that they want to initialize. They 
    # will then be prompted to specify the various fields 
    # associated with each object. 
    i = 0
    while i < len(args):
        num_objects = int(args[i + 1])
        for j in range(num_objects):
            if args[i] == "Hosts":
                network.create_host(None, None)

            if args[i] == "Routers":
                network.create_router(None)

            if args[i] == "Links":
                network.create_link(None, None, None, None, None)

            if args[i] == "Flows":
                network.create_flow(None, None, None, None, None)
        i += 2

    # TODO: write functions to convert units to bits and seconds

    # Get the true values for the links
    links_list = list(network.links.items())
    for link_id, link in links_list:
        print("Enter parameters for link " + str(link_id) + ".")
        rate = convert_to_bits(float(input("Link Rate (Mbps): ")), Mb)
        delay = convert_to_seconds(float(input("Link Delay (ms): ")))
        buff = convert_to_bits(float((input("Link Buffer Size (KB): "))), KB)
        source = input("Connection 1. Input the type of node (H or R) and its id. (Ex: H1): ")
        sink = input("Connection 2. Input the type of node (H or R) and its id. (Ex: R2): ")

        if source[0] == "H":
            source_ref = network.hosts[int(source[1:])]
        else:
            source_ref = network.routers[int(source[1:])]

        if sink[0] == "H":
            sink_ref = network.hosts[int(sink[1:])]
        else:
            sink_ref = network.routers[int(sink_ref[1:])]

        link.capacity = rate
        link.connection1 = source_ref
        link.connection2 = sink_ref
        link.queue_capacity = buff

        # TODO: should the cost be the delay?
        link.static_cost = delay

        # We should also create a second link with the same properties between
        # the source and sink
        new_link = network.create_link(sink_ref, source_ref, buff, rate, delay)

        # Make sure the nodes also reference the links
        source_ref.incoming_link = link
        source_ref.outgoing_link = new_link
        sink_ref.incoming_link = link
        sink_ref.outgoing_link = new_link

    # Get the parameters for hosts 
    hosts_list = network.hosts.items()
    for host in hosts_list:
        host_id = host[0]
        print("Enter parameters for host " + str(host_id) + ".")
        ip = input("IP address: ")
        host[1].ip = ip 
        # TODO: max_window only for the flow???
        # wind_size = float(input("Input Max Window Size: "))
        # host[1].max_window = wind_size

    # Get the parameters for routers
    routers_list = network.routers.items()
    for router in routers_list:
        router_id = router[0]
        print("Enter parameters for router " + str(router_id) + ".")
        ip = input("IP address: ")
        router[1].ip = ip

    # Get the parameters for flows
    flows_list = network.flows.items()
    for flow in flows_list:
        flow_id = flow[0]
        print("Enter parameters for flow " + str(flow_id) + ".")
        size = convert_to_bits(float(input("Data Amount (MB): ")), MB)
        start_time = float(input("Flow Start Time (s): "))
        source = int(input("ID of Flow Source: "))
        dest = int(input("ID of Flow Destination: "))
        source_ref = network.hosts[source]
        dest_ref = network.hosts[dest]
        flow[1].size = size
        flow[1].source = source_ref
        flow[1].destination = dest_ref
        flow[1].time_spawned = start_time
        source_ref.flows.append(flow[1])


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
            # max_window only for the flow???
            # print("    Max Window Size: " + str(host[1].max_window))

        routers_list = list(network.routers.items())
        if (len(routers_list) > 0):
            print("\n")
            print("________Routers________")
        for router in routers_list:
            router_id = router[0]
            print("Printing out Fields for Router " + str(router_id) + ".")
            print("    IP Address: " + str(router[1].ip))
            print("    ID of Links to/from Router:")
            for link in router[1].links:
                print("    " + str(link.id))

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
            print("    Time Spawned " + str(flow[1].time_spawned))



            

            





