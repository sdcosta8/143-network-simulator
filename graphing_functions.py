import matplotlib.pyplot as plt
from utils import (
    INDIV_SERIES, INDIV_GRAPHS, GRAPHS_TOGETHER
)

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
        counter = 5 
        for element in time_dict:
            x_axis.append(element[0])
            y_axis.append(element[1])
        all_series.append([x_axis, y_axis, series])
    return all_series


# Helper function called to plot each subplot
def add_individual_subplot(series_list, last_time, y_label, ax):
    for i in range(len(series_list)):
        x_axis = series_list[i][0]
        y_axis = series_list[i][1]
        series = series_list[i][2]
        ax.plot(x_axis, y_axis, label=series)

    chartBox = ax.get_position()
    ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.3, chartBox.height])
    ax.legend(loc='upper center', bbox_to_anchor=(1.45, 0.8), shadow=True, ncol=1)
    plt.xlabel('Time (secs)')
    plt.ylabel(y_label)


def plot_graphs(points_dict, last_time, num_subplots, plot_name):
    fig = plt.figure()
    num = 1
    for item in points_dict.items():
        # Each item is a particular graph mapped to its individual series'
        ax = fig.add_subplot(num_subplots, 1, num)
        add_individual_subplot(item[1], last_time, item[0], ax)
        num += 1
    plt.savefig(plot_name)
    plt.close()


# Each graph separate, but series are not separate
def plot_each_graph_separate(points_dict, last_time, test_case):
    for item in points_dict.items():
        graph_dict = {}
        graph_dict[item[0]] = item[1]
        plot_graphs(graph_dict, last_time, 1, test_case + item[0].split(' (')[0] + '.png')


# For each series in each graph, we should plot them separately
def plot_each_series_separate(points_dict, last_time, test_case):
    for item in points_dict.items():
        for i in range(len(item[1])):
            series_dict = {}
            series_dict[item[0]] = [item[1][i]]
            plot_graphs(series_dict, last_time, 1, test_case + \
                item[1][i][2] + item[0].split(' (')[0] + '.png')


# The function that should be called from outside this file
def create_graphs(buffer_occ_dicts, packet_loss_dicts, last_time, \
    link_rate_dicts, wind_size_dicts, flow_rate_dicts, packet_delay_dicts, \
    link_order, flow_order, test_case):
    points_dict = {}
    points_dict['Buffer Occupancy (pkts)'] = convert_to_lists(buffer_occ_dicts, 
        link_order)
    points_dict['Packet Loss (pkts)'] = convert_to_lists(packet_loss_dicts, 
        link_order)    
    points_dict['Link Rate (bps)'] = convert_to_lists(link_rate_dicts, 
        link_order)        
    points_dict['Window Size (pkts)'] = convert_to_lists(wind_size_dicts, 
        flow_order) 
    points_dict['Flow Rate (bps)'] = convert_to_lists(flow_rate_dicts, 
        flow_order)     
    points_dict['Packet Delay (sec)'] = convert_to_lists(packet_delay_dicts, 
        flow_order)  

    # All graphs on one figure
    if GRAPHS_TOGETHER:
        plot_graphs(points_dict, last_time, 6, test_case + 'AllGraphs.png')

    # Each graph in different figure
    if INDIV_GRAPHS:
        plot_each_graph_separate(points_dict, last_time, test_case)

    # Each series for each graph in a separate figure
    if INDIV_SERIES:
        plot_each_series_separate(points_dict, last_time, test_case)

