# sim/statistics.py

import csv
import os
from config import settings
import matplotlib.pyplot as plt
import numpy as np 

class Statistics:
    # Class attributes for storing metrics
    server_queue_sizes = {}          # {server_ip: [(time, queue_size), ...]}
    server_dropped_requests = {}     # {server_ip: [dropped_count]}
    server_dropped_requests_time = {}     # {server_ip: [dropped_count]}
    
    load_balancer_req_queue_sizes = []   # [(time, queue_size)]
    load_balancer_req_dropped_requests = 0
    load_balancer_req_dropped_requests_time = []

    load_balancer_res_queue_sizes = []   # [(time, queue_size)]
    load_balancer_res_dropped_requests = 0
    load_balancer_res_dropped_requests_time = 0

    dns_queue_sizes = []             # [(time, queue_size)]
    dns_dropped_requests = 0
    dns_dropped_requests_time = []

    
    client_latencies = []            # [(start_time, latency), ...]
    
    total_requests_processed = 0
    total_requests_processed_time = []

    client_present = 0
    client_present_time = []

    @classmethod
    def clear_stats(cls):
        cls.server_queue_sizes = {}          # {server_ip: [(time, queue_size), ...]}
        cls.server_dropped_requests = {}     # {server_ip: [dropped_count]}
        cls.server_dropped_requests_time = {}     # {server_ip: [dropped_count]}
        
        cls.load_balancer_req_queue_sizes = []   # [(time, queue_size)]
        cls.load_balancer_req_dropped_requests = 0
        cls.load_balancer_req_dropped_requests_time = []

        cls.load_balancer_res_queue_sizes = []   # [(time, queue_size)]
        cls.load_balancer_res_dropped_requests = 0
        cls.load_balancer_res_dropped_requests_time = 0

        cls.dns_queue_sizes = []             # [(time, queue_size)]
        cls.dns_dropped_requests = 0
        cls.dns_dropped_requests_time = []

        
        cls.client_latencies = []            # [(start_time, latency), ...]
        
        cls.total_requests_processed = 0
        cls.total_requests_processed_time = []

        cls.client_present = 0
        cls.client_present_time = []

    @classmethod
    def record_server_queue_size(cls, server_ip, time, queue_size):
        if server_ip not in cls.server_queue_sizes:
            cls.server_queue_sizes[server_ip] = []
        cls.server_queue_sizes[server_ip].append((time, queue_size))
    
    @classmethod
    def increment_server_dropped_requests(cls, server_ip, time):
        cls.server_dropped_requests[server_ip] = cls.server_dropped_requests.get(server_ip, 0) + 1
        if(server_ip not in cls.server_dropped_requests_time):
            cls.server_dropped_requests_time[server_ip] = list()
        cls.server_dropped_requests_time.get(server_ip).append([time, cls.server_dropped_requests[server_ip]])
    
    @classmethod
    def record_load_balancer_req_queue_size(cls, time, queue_size):
        cls.load_balancer_req_queue_sizes.append((time, queue_size))

    @classmethod
    def increment_load_balancer_req_dropped_requests(cls, time):
        cls.load_balancer_req_dropped_requests += 1
        cls.load_balancer_req_dropped_requests_time.append([time, cls.load_balancer_req_dropped_requests])

    @classmethod
    def record_load_balancer_res_queue_size(cls, time, queue_size):
        cls.load_balancer_res_queue_sizes.append((time, queue_size))
    
    @classmethod
    def increment_load_balancer_res_dropped_requests(cls, time):
        cls.load_balancer_res_dropped_requests += 1
        cls.load_balancer_res_dropped_requests_time.append([time, cls.load_balancer_res_dropped_requests])

    @classmethod
    def record_dns_queue_size(cls, time, queue_size):
        cls.dns_queue_sizes.append((time, queue_size))
    
    @classmethod
    def increment_dns_dropped_requests(cls, time):
        cls.dns_dropped_requests += 1
        cls.dns_dropped_requests_time.append([time, cls.dns_dropped_requests])
    
    @classmethod
    def record_client_latency(cls, time, latency):
        cls.client_latencies.append((time, latency))

    
    @classmethod
    def increment_total_requests_processed(cls, time):
        cls.total_requests_processed += 1
        cls.total_requests_processed_time.append([time, cls.total_requests_processed])
    
    @classmethod
    def increment_client_present(cls, time):
        cls.client_present += 1
        cls.client_present_time.append([time, cls.client_present])
    
    @classmethod
    def decrement_client_present(cls, time):
        cls.client_present -= 1
        cls.client_present_time.append([time, cls.client_present])

    @classmethod
    def save_statistics(cls):
        """Save collected statistics to CSV files."""
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(settings.OUTPUT_METRICS_FILE)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save client latencies
        client_latency_file = os.path.join(output_dir, 'client_latencies.csv')
        with open(client_latency_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Latency'])
            for latency in cls.client_latencies:
                writer.writerow([latency])
        
        # Save server queue sizes
        for server_ip, data in cls.server_queue_sizes.items():
            filename = os.path.join(output_dir, f'server_{server_ip}_queue_sizes.csv')
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Time', 'Queue Size'])
                writer.writerows(data)
        
        # Save load balancer queue sizes
        lb_queue_file = os.path.join(output_dir, 'load_balancer_queue_sizes.csv')
        with open(lb_queue_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time', 'Queue Size'])
            writer.writerows(cls.load_balancer_queue_sizes)
        
        # Save DNS queue sizes
        dns_queue_file = os.path.join(output_dir, 'dns_queue_sizes.csv')
        with open(dns_queue_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time', 'Queue Size'])
            writer.writerows(cls.dns_queue_sizes)
        
        # Save summary statistics
        summary_file = os.path.join(output_dir, 'summary_statistics.txt')
        with open(summary_file, 'w') as f:
            f.write(f"Total Requests Processed: {cls.total_requests_processed}\n")
            f.write(f"Average Client Latency: {cls.get_average_client_latency():.4f} seconds\n")
            f.write(f"Total Dropped Requests:\n")
            for server_ip, count in cls.server_dropped_requests.items():
                f.write(f"  Server {server_ip}: {count}\n")
            f.write(f"  Load Balancer: {cls.load_balancer_dropped_requests}\n")
            f.write(f"  DNS Server: {cls.dns_dropped_requests}\n")
    
    @classmethod
    def get_average_client_latency(cls):
        if cls.client_latencies:
            total_latency = sum(latency for time, latency in cls.client_latencies)
            return total_latency / len(cls.client_latencies)
        else:
            return 0.0
    
    @classmethod
    def generate_graphs(cls):
        """Generate and save graphs for the collected statistics."""
        output_dir = os.path.dirname(settings.OUTPUT_METRICS_FILE)
        # delete all graphs.
        for file in os.listdir(output_dir):
            if file.endswith('.png'):
                os.remove(os.path.join(output_dir, file))
        # Generate graphs for server queue sizes
        for server_ip, queue_data in cls.server_queue_sizes.items():
            times, queue_sizes = zip(*queue_data)
            cls._plot_graph(
                times, queue_sizes,
                title=f"Server {server_ip} Queue Size Over Time",
                xlabel="Time (s)",
                ylabel="Queue Size",
                output_path=os.path.join(output_dir, f'server_{server_ip}_queue_size.png')
            )

        # Generate graphs for dropped requests at the server
        for server_ip, drop_data in cls.server_dropped_requests_time.items():
            times, dropped_counts = zip(*drop_data)
            cls._plot_graph(
                times, dropped_counts,
                title=f"Server {server_ip} Dropped Requests Over Time",
                xlabel="Time (s)",
                ylabel="Dropped Requests",
                output_path=os.path.join(output_dir, f'server_{server_ip}_dropped_requests.png')
            )
        
        # Generate load balancer request queue size graph
        if cls.load_balancer_req_queue_sizes:
            times, queue_sizes = zip(*cls.load_balancer_req_queue_sizes)
            cls._plot_graph(
                times, queue_sizes,
                title="Load Balancer Request Queue Size Over Time",
                xlabel="Time (s)",
                ylabel="Queue Size",
                output_path=os.path.join(output_dir, 'load_balancer_request_queue_size.png')
            )
        
        # Generate load balancer dropped requests graph
        if cls.load_balancer_req_dropped_requests_time:
            times, dropped_counts = zip(*cls.load_balancer_req_dropped_requests_time)
            cls._plot_graph(
                times, dropped_counts,
                title="Load Balancer Dropped Requests Over Time",
                xlabel="Time (s)",
                ylabel="Dropped Requests",
                output_path=os.path.join(output_dir, 'load_balancer_dropped_requests.png')
            )
        
               # Generate load balancer request queue size graph
        if cls.load_balancer_res_queue_sizes:
            times, queue_sizes = zip(*cls.load_balancer_res_queue_sizes)
            cls._plot_graph(
                times, queue_sizes,
                title="Load Balancer Response Queue Size Over Time",
                xlabel="Time (s)",
                ylabel="Queue Size",
                output_path=os.path.join(output_dir, 'load_balancer_response_queue_size.png')
            )
        
        # Generate load balancer dropped requests graph
        if cls.load_balancer_res_dropped_requests_time:
            times, dropped_counts = zip(*cls.load_balancer_res_dropped_requests_time)
            cls._plot_graph(
                times, dropped_counts,
                title="Load Balancer Dropped Responses Over Time",
                xlabel="Time (s)",
                ylabel="Dropped Requests",
                output_path=os.path.join(output_dir, 'load_balancer_dropped_responses.png')
            )
        
        
        # Generate DNS server queue size graph
        if cls.dns_queue_sizes:
            times, queue_sizes = zip(*cls.dns_queue_sizes)
            cls._plot_graph(
                times, queue_sizes,
                title="DNS Server Queue Size Over Time",
                xlabel="Time (s)",
                ylabel="Queue Size",
                output_path=os.path.join(output_dir, 'dns_server_queue_size.png')
            )

        # Generate DNS dropped requests graph
        if cls.dns_dropped_requests_time:
            times, dropped_counts = zip(*cls.dns_dropped_requests_time)
            cls._plot_graph(
                times, dropped_counts,
                title="DNS Server Dropped Requests Over Time",
                xlabel="Time (s)",
                ylabel="Dropped Requests",
                output_path=os.path.join(output_dir, 'dns_dropped_requests.png')
            )

        # Generate client latency graph
        if cls.client_latencies:
            times, latencies = zip(*cls.client_latencies)
            cls._plot_graph(
                times, latencies,
                title="Client Latency Over Time",
                xlabel="Time (s)",
                ylabel="Latency (s)",
                output_path=os.path.join(output_dir, 'client_latency.png')
            )

        # Generate total requests processed graph
        if cls.total_requests_processed_time:
            times, request_counts = zip(*cls.total_requests_processed_time)
            cls._plot_graph(
                times, request_counts,
                title="Total Requests Processed Over Time",
                xlabel="Time (s)",
                ylabel="Total Requests Processed",
                output_path=os.path.join(output_dir, 'total_requests_processed.png')
            )
        
        # Generate total requests processed graph
        if cls.client_present_time:
            times, request_counts = zip(*cls.client_present_time)
            cls._plot_graph(
                times, request_counts,
                title="No. of Clients Over Time",
                xlabel="Time (s)",
                ylabel="No. of clients",
                output_path=os.path.join(output_dir, 'client_presents_time.png')
            )
        
    @classmethod
    def _plot_graph(cls, x_data, y_data, title, xlabel, ylabel, output_path, window_size=10):
        """Helper function to plot and save a smoothed graph with upper and lower bounds."""
        
        # Convert to numpy arrays for efficient computation
        x_data = np.array(x_data)
        y_data = np.array(y_data)

        # Compute the moving average (smoothing)
        smoothed_y = cls._moving_average(y_data, window_size)
        
        # Compute the upper and lower bounds (1 standard deviation around the mean)
        std_dev = cls._moving_std_dev(y_data, window_size)
        
        # Trim std_dev to match smoothed_y length
        std_dev = std_dev[:len(smoothed_y)]
        x_data_trimmed = x_data[:len(smoothed_y)]  # Ensure x_data is also trimmed to the correct length
        
        # Compute upper and lower bounds
        upper_bound = smoothed_y + std_dev
        lower_bound = smoothed_y - std_dev
        
        # Plot the original data
        plt.figure(figsize=(10, 6))
        plt.plot(x_data, y_data, color='lightgray', label='Original', alpha=0.5, linestyle='--')
        
        # Plot the smoothed data (moving average)
        plt.plot(x_data_trimmed, smoothed_y, color='blue', label='Smoothed', linewidth=2)
        
        # Plot the upper and lower bounds
        plt.fill_between(x_data_trimmed, lower_bound, upper_bound, color='blue', alpha=0.2, label='±1 Std. Dev.')
        
        # Set title, labels, and grid
        plt.title(title, fontsize=14)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='upper right', fontsize=12)

        # Save the plot
        plt.savefig(output_path)
        plt.close()

    @classmethod
    def _moving_average(cls, data, window_size):
        """Compute the simple moving average (SMA) for smoothing."""
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

    @classmethod
    def _moving_std_dev(cls, data, window_size):
        """Compute the rolling standard deviation for variability."""
        return np.array([np.std(data[max(0, i-window_size+1):i+1]) for i in range(len(data))])

    @classmethod
    def get_average_queue_size(cls, queue_sizes):
        """Compute the average queue size over time."""
        if queue_sizes:
            total_size = sum(queue_size for time, queue_size in queue_sizes)
            return total_size / len(queue_sizes)
        return 0.0

    @classmethod
    def print_summary_metrics(cls, network):
        """Prints summary statistics for the simulation."""
        print("\n===== Simulation Metrics Summary =====")
        
        # Total requests processed
        print(f"Total Requests Processed: {cls.total_requests_processed}")
        
        # Average client latency
        avg_latency = cls.get_average_client_latency()
        print(f"Average Client Latency: {avg_latency:.4f} seconds")

        all_dropped_requests = 0
        # Server metrics
        for server_ip, queue_data in cls.server_queue_sizes.items():
            avg_server_queue_size = cls.get_average_queue_size(queue_data)
            dropped_requests = cls.server_dropped_requests.get(server_ip, 0)
            print(f"\nServer {server_ip} Metrics:")
            print(f"  - Average Queue Size: {avg_server_queue_size:.2f}")
            print(f"  - Total Dropped Requests: {dropped_requests}")

            # print utilization
            entity = network.get_entity_by_ip(server_ip)
            utilization = entity.get_utilization()
            print(f"  - Utilization: {utilization:.2f}")
            all_dropped_requests += dropped_requests

        # Load balancer request queue metrics
        avg_lb_req_queue_size = cls.get_average_queue_size(cls.load_balancer_req_queue_sizes)
        print(f"\nLoad Balancer Request Queue Metrics:")
        print(f"  - Average Request Queue Size: {avg_lb_req_queue_size:.2f}")
        print(f"  - Total Dropped Requests: {cls.load_balancer_req_dropped_requests}")

        # Load balancer response queue metrics
        avg_lb_res_queue_size = cls.get_average_queue_size(cls.load_balancer_res_queue_sizes)
        print(f"\nLoad Balancer Response Queue Metrics:")
        print(f"  - Average Response Queue Size: {avg_lb_res_queue_size:.2f}")
        print(f"  - Total Dropped Requests: {cls.load_balancer_res_dropped_requests}")

        # DNS metrics
        avg_dns_queue_size = cls.get_average_queue_size(cls.dns_queue_sizes)
        print(f"\nDNS Server Metrics:")
        print(f"  - Average Queue Size: {avg_dns_queue_size:.2f}")
        print(f"  - Total Dropped Requests: {cls.dns_dropped_requests}")

        all_dropped_requests += cls.load_balancer_req_dropped_requests + cls.load_balancer_res_dropped_requests + cls.dns_dropped_requests

        print(f"\nTotal Dropped Requests: {all_dropped_requests}")
        print("======================================\n")

    @classmethod
    def get_average_server_queue_lengths(cls, network):
        total = 0
        for server_ip, queue_data in cls.server_queue_sizes.items():
            total += cls.get_average_queue_size(queue_data)
        return total / len(cls.server_queue_sizes)
    
    @classmethod
    def get_dropped_requests(cls):
        all_dropped_requests = 0
        for server_ip, queue_data in cls.server_dropped_requests.items():
            all_dropped_requests += queue_data
        return all_dropped_requests + cls.load_balancer_req_dropped_requests + cls.load_balancer_res_dropped_requests + cls.dns_dropped_requests
    
    @classmethod
    def get_avg_client_latencies(cls):
        total = 0
        for time, latency in cls.client_latencies:
            total += latency
        return total / len(cls.client_latencies)

    @classmethod
    def get_avg_server_utilization(cls, network):
        total = 0
        for server_ip, queue_data in cls.server_queue_sizes.items():
            entity = network.get_entity_by_ip(server_ip)
            total += entity.get_utilization()
        return total / len(cls.server_queue_sizes)

