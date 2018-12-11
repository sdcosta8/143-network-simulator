import matplotlib.pyplot as plt
from utils import (
    INDIV_SERIES, INDIV_GRAPHS, GRAPHS_TOGETHER, PLOT_PARALLEL, TEST_2_DIRECTION, 
    ISOLATE_LINKS
)
import os

# Helper function for converting the dictionaries to a list 
# representation. We use this so that we only have to convert one time 
# and can store results
def convert_to_lists(time_dicts, series_labels):
    all_series = []
    for i in range(len(time_dicts)):
        time_dict = time_dicts[i]
        series = series_labels[i]
        x_axis = []
        y_axis = []
        for element in time_dict:
            x_axis.append(element[0])
            y_axis.append(element[1])
        all_series.append([x_axis, y_axis, series])
    return all_series

# Helper function called to plot each subplot
def add_individual_subplot(series_list, last_time, y_label, ax, width_scale, anchor_x, 
    anchor_y):
    for i in range(len(series_list)):
        x_axis = series_list[i][0]
        y_axis = series_list[i][1]
        series = series_list[i][2]
        ax.plot(x_axis, y_axis, label=series)
    chartBox = ax.get_position()
    ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*width_scale, \
        chartBox.height])
    ax.legend(loc='upper center', bbox_to_anchor=(anchor_x, anchor_y), \
        shadow=True, ncol=1)
    plt.xlabel('Time (secs)')
    plt.ylabel(y_label)

def plot_graphs(points_dict, last_time, num_subplots, plot_name, width_scale, \
    anchor_x, anchor_y, max_time):
    fig = plt.figure()
    fig.set_size_inches(20, 10)
    num = 1
    for item in points_dict.items():
        # Each item is a particular graph mapped to its individual series'
        ax = fig.add_subplot(num_subplots, 1, num)
        ax.set_xlim([0, max_time])
        add_individual_subplot(item[1], last_time, item[0], ax, width_scale, \
            anchor_x, anchor_y)
        num += 1
    plt.savefig(plot_name)
    plt.close()

# Each graph separate, but series are not separate
def plot_each_graph_separate(points_dict, last_time, test_case, protocol, max_time):
    for item in points_dict.items():
        graph_dict = {}
        graph_dict[item[0]] = item[1]
        plot_graphs(graph_dict, last_time, 1, test_case + '/' + protocol + 
            item[0].split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)

# For each series in each graph, we should plot them separately
def plot_each_series_separate(points_dict, last_time, test_case, protocol, max_time):
    for item in points_dict.items():
        for i in range(len(item[1])):
            series_dict = {}
            series_dict[item[0]] = [item[1][i]]
            plot_graphs(series_dict, last_time, 1, test_case + '/' + protocol +
                item[1][i][2] + item[0].split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)

def plot_2_direction(data, last_time, y_label, protocol, max_time):
    L1_right = None
    L1_left = None
    L2_right = None
    L2_left = None
    L3_right = None
    L3_left = None
    for element in data:
        if element[2] == 'L1_right':
            L1_right = element
        elif element[2] == 'L1_left':
            L1_left = element
        elif element[2] == 'L2_right':
            L2_right = element
        elif element[2] == 'L2_left':
            L2_left = element
        elif element[2] == 'L3_right':
            L3_right = element
        elif element[2] == 'L3_left':
            L3_left = element
    plot_graphs({y_label: [L1_right, L2_right, L3_right]}, last_time, 1, 'test2/' + \
    'test2RightDirection' + protocol + y_label.split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)
    plot_graphs({y_label: [L1_left, L2_left, L3_left]}, last_time, 1, 'test2/' + \
    'test2LeftDirection' + protocol + y_label.split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)

# Below are the series' we need to plot together:
# L1_right and L2_right
# L3_right and L4_right
# L1_left and L2_left
# L3_left and L4_left
def plot_parallel_links(data, last_time, y_label, protocol, max_time):
    L1_right = None
    L1_left = None
    L2_right = None
    L2_left = None
    L3_right = None
    L3_left = None
    L4_right = None
    L4_left = None
    for element in data:
        if element[2] == 'L1_right':
            L1_right = element
        elif element[2] == 'L1_left':
            L1_left = element
        elif element[2] == 'L2_right':
            L2_right = element
        elif element[2] == 'L2_left':
            L2_left = element
        elif element[2] == 'L3_right':
            L3_right = element
        elif element[2] == 'L3_left':
            L3_left = element
        elif element[2] == 'L4_right':
            L4_right = element
        elif element[2] == 'L4_left':
            L4_left = element
    plot_graphs({y_label: [L1_right, L2_right]}, last_time, 1, 'test1/' +  
        protocol + 'Parallel' + "L1L2_right" + y_label.split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)
    plot_graphs({y_label: [L3_right, L4_right]}, last_time, 1, 'test1/' + 
        protocol + 'Parallel' + "L3L4_right" + y_label.split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)
    plot_graphs({y_label: [L1_left, L2_left]}, last_time, 1, 'test1/' + 
        protocol + 'Parallel' + "L1L2_left" + y_label.split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)
    plot_graphs({y_label: [L3_left, L4_left]}, last_time, 1, 'test1/' + 
        protocol + 'Parallel' + "L3L4_left" + y_label.split(' (')[0] + '.png', 1, 0.5, 1.15, max_time)

def isolate_links(data):
    L1_right = None
    L1_left = None
    L2_right = None
    L2_left = None
    L3_right = None
    L3_left = None
    for element in data:
        if element[2] == 'L1_right':
            L1_right = element
        elif element[2] == 'L1_left':
            L1_left = element
        elif element[2] == 'L2_right':
            L2_right = element
        elif element[2] == 'L2_left':
            L2_left = element
        elif element[2] == 'L3_right':
            L3_right = element
        elif element[2] == 'L3_left':
            L3_left = element
    return [L1_right, L2_right, L3_right, L1_left, L2_left, L3_left]

# The function that should be called from outside this file
def create_graphs(buffer_occ_dicts, packet_loss_dicts, last_time, \
    link_rate_dicts, wind_size_dicts, flow_rate_dicts, packet_delay_dicts, \
    link_order, flow_order, test_case, protocol, max_time):
    points_dict = {}
    points_dict['Buffer Occupancy (pkts)'] = convert_to_lists(buffer_occ_dicts, 
        link_order)
    points_dict['Packet Loss (pkts)'] = convert_to_lists(packet_loss_dicts, 
        link_order)    
    points_dict['Link Rate (Mbps)'] = convert_to_lists(link_rate_dicts, 
        link_order)        
    points_dict['Window Size (pkts)'] = convert_to_lists(wind_size_dicts, 
        flow_order) 
    points_dict['Flow Rate (Mbps)'] = convert_to_lists(flow_rate_dicts, 
        flow_order)     
    points_dict['Packet Delay (sec)'] = convert_to_lists(packet_delay_dicts, 
        flow_order)  

    # create a directory for the test case if it doesn't exist
    directory = test_case
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

    # All graphs on one figure
    if GRAPHS_TOGETHER:
        plot_graphs(points_dict, last_time, 6, test_case + '/' + protocol + 
            'AllGraphs.png', 0.8, 1.2, 0.8, max_time)

    # Each graph in different figure
    if INDIV_GRAPHS:
        plot_each_graph_separate(points_dict, last_time, test_case, protocol, max_time)

    # Each series for each graph in a separate figure
    if INDIV_SERIES:
        plot_each_series_separate(points_dict, last_time, test_case, protocol, max_time)

    # Graph the links in parallel together. We need to hard code this for 
    # test case 1. do for link rates and buffer occupancy
    if PLOT_PARALLEL and test_case == 'test1':
        plot_parallel_links(points_dict['Buffer Occupancy (pkts)'], \
            last_time, 'Buffer Occupancy (pkts)', protocol, max_time)
        plot_parallel_links(points_dict['Link Rate (Mbps)'], \
            last_time, 'Link Rate (Mbps)', protocol, max_time)

    if TEST_2_DIRECTION and test_case == 'test2':
        plot_2_direction(points_dict['Buffer Occupancy (pkts)'], \
            last_time, 'Buffer Occupancy (pkts)', protocol, max_time)
        plot_2_direction(points_dict['Link Rate (Mbps)'], \
            last_time, 'Link Rate (Mbps)', protocol, max_time)

    if ISOLATE_LINKS and (test_case == 'extra_test' or test_case == 'extra_test_no_switching'):
        points_dict['Buffer Occupancy (pkts)'] = isolate_links(points_dict['Buffer Occupancy (pkts)'])
        points_dict['Link Rate (Mbps)'] = isolate_links(points_dict['Link Rate (Mbps)'])
        points_dict['Packet Loss (pkts)'] = isolate_links(points_dict['Packet Loss (pkts)'])
        plot_graphs(points_dict, last_time, 6, test_case + '/' + protocol + 
            'AllGraphsIsolatedLinks.png', 0.8, 1.2, 0.8, max_time)
        plot_each_graph_separate(points_dict, last_time, test_case, 'IsolatedLinks' + protocol, max_time)

