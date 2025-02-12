# Name: Mohammad khdour     ID 1212517
# Name: Yazan Ghunaim       ID 1220029

import random
import copy

import matplotlib.pyplot as plt
from ResourceAllocationGraph import *
from WaitForGraph import *


def readFile():
    """

    :return: processes
    """
    try:
        file = open("input.txt", "r")
    except FileNotFoundError:
        print("input file doesn't exist")
        exit(-1)

    lines = file.readlines()
    processes = []

    try:
        for line in lines:
            bursts = []
            process = {}
            print(line)
            lineContant = line.split()
            process["id"] = int(lineContant[0])
            process["arrive"] = int(lineContant[1])
            process["priority"] = int(lineContant[2])
            burst_sequence = lineContant[3:]
            # Parse bursts
            current_burst_type = None
            current_burst_content = []
            for item in burst_sequence:
                if item.startswith('CPU') or item.startswith('IO'):
                    if current_burst_type:
                        bursts.extend(parse_burst(current_burst_type, current_burst_content))
                        current_burst_content = []
                    current_burst_type = item

                    if item.startswith('CPU{') or item.startswith('IO{'):
                        contents = item.split('{')
                        current_burst_type = contents[0]
                        current_burst_content.append(contents[1].strip(",{}"))


                else:
                    current_burst_content.append(item.strip(",{}"))

            # Save the last burst
            if current_burst_type:
                bursts.extend(parse_burst(current_burst_type, current_burst_content))

            process["cpu time"] = bursts
            processes.append(process)

    except:
        print("invalid input format")
        exit(-1)

    file.close()

    return processes


def parse_burst(burst_type, content):
    """

    :param burst_type:
    :param content:
    :return: burst
    """

    bursts = []
    burst = {"type": burst_type, "time": 0, "resource": None}

    for item in content:
        if item.startswith("R["):

            resource_id = int(item[2:-1])  # Extract the resource ID
            burst['resource'] = {'type': 'R', 'rid': resource_id}
            bursts.append(burst)
            burst = {"type": burst_type, "time": 0, "resource": None}

        elif item.startswith("F["):
            resource_id = int(item[2:-1])  # Extract the resource ID
            burst['resource'] = {'type': 'F', 'rid': resource_id}
            bursts.append(burst)
            burst = {"type": burst_type, "time": 0, "resource": None}

        elif item.strip(",{}").isdigit():
            burst["time"] = int(item)
            bursts.append(burst)
            burst = {"type": burst_type, "time": 0, "resource": None}

    return bursts


def priority_schedule_with_round_robin(processes, time_quantum):
    """

    :param processes:
    :param time_quantum:
    :return: cpu_burst
    """
    # Sort processes by arrival time
    copy_processes = copy.deepcopy(processes)
    sorted_processes = sorted(copy_processes, key=lambda p: int(p['arrive']))

    # Initialize variables
    availableTime = {process['id']: process['arrive'] for process in sorted_processes}
    process_run_time = {process['id']: 0 for process in sorted_processes}
    process_waitResource_time = {process['id']: 0 for process in sorted_processes}
    terminated_process_times = {}
    cpu_burst = []  # To store CPU burst execution details
    ready_queue = []  # Processes ready for execution
    start_time = 0  # Current time
    stop_time = 0  # finish time
    waiting_queue = []
    reg = ResourceAllocationGraph()

    # Execute priority scheduling with Round Robin
    while sorted_processes or ready_queue or waiting_queue:
        wfg = convert_rag_to_wfg(reg)
        status, cycles = detect_deadlock(wfg)
        # check if there is deadlock
        if status:
            print('detect deadlock at time ', start_time)
            wfg.display()
            terminated = recover_deadlock(cycles, reg, waiting_queue, process_run_time, processes, availableTime, start_time)
            terminated_process_times.update({process: time for process, time in terminated.items()})
            process_waitResource_time.update({process: start_time - process_waitResource_time[process] for process in terminated.keys() if process_waitResource_time[process] != 0})
            draw_gantt_chart(cpu_burst)

        # Add processes to ready_queue when it arrived
        while sorted_processes and availableTime[sorted_processes[0]['id']] <= start_time:
            ready_queue.append(sorted_processes.pop(0))

        # check if waiting queue have processes
        if waiting_queue:
            for waiting in waiting_queue[:]:
                if availableTime[waiting['id']] <= start_time:
                    if not waiting['cpu time'][0]['resource']:
                        if waiting['cpu time'][0]['type'] == 'IO':  # coming from IO
                            waiting['cpu time'].pop(0)
                        ready_queue.append(waiting)
                        waiting_queue.remove(waiting)

                    elif reg.resource_used_by(waiting['cpu time'][0]['resource']['rid']) is None or reg.resource_used_by(waiting['cpu time'][0]['resource']['rid']) == waiting['id']:
                        if process_waitResource_time[waiting['id']] != 0:
                            process_waitResource_time[waiting['id']] = start_time - process_waitResource_time[waiting['id']]
                        ready_queue.append(waiting)
                        waiting_queue.remove(waiting)

                    elif not (ready_queue or sorted_processes) and len(waiting_queue) - waiting_queue.index(waiting) - 1 == 0: # if last index need resource and no process in ready queue

                        print(25 * "*", " CAN'T RELEASE THE RESOURCES", 25 * "*")
                        print("time = ",start_time)
                            #exit(-2)

            if not ready_queue:
                io_list = [availableTime[waiting['id']] for waiting in waiting_queue if
                           not waiting['cpu time'][0]['resource']]
                if len(io_list) > 0:
                    if ((not (ready_queue or sorted_processes) and min(io_list) > start_time) or
                            (sorted_processes and availableTime[sorted_processes[0]['id']] > min(
                                io_list) > start_time)):
                        start_time = min(io_list)

        if ready_queue:
            ready_queue.sort(key=lambda p: (int(p['priority']), availableTime[p['id']]))

            # get first process in the ready queue
            current_process = ready_queue.pop(0)
            reg.add_process(current_process['id'])

            for burst in current_process['cpu time'][:]:

                if burst['type'] == 'CPU':
                    if burst['resource']:
                        if burst['resource']['type'] == 'F':    # if the type of the resource is free
                            reg.release_resource(burst['resource']['rid'], current_process['id'])
                            current_process['cpu time'].remove(burst)

                            # add the process to ready queue if the released resource is requested by other process
                            for waiting in waiting_queue:
                                if waiting['cpu time'][0]['resource'] and (reg.resource_used_by(waiting['cpu time'][0]['resource']['rid']) is None or reg.resource_used_by(waiting['cpu time'][0]['resource']['rid']) == waiting['id']):
                                    if process_waitResource_time[waiting['id']] != 0:
                                        process_waitResource_time[waiting['id']] = start_time - process_waitResource_time[waiting['id']]
                                    ready_queue.append(waiting)
                                    waiting_queue.remove(waiting)
                            continue
                        else:   # if the type of the resource is Request

                            if reg.resource_used_by(burst['resource']['rid']) is not None:  # check if the resource is free
                                if reg.resource_used_by(burst['resource']['rid']) != current_process['id']:     # check if the resource is used by other process
                                    reg.add_request(burst['resource']['rid'], current_process['id'])    # add request if the resource assigned to other process
                                    waiting_queue.append(current_process)   # append the process in waiting queue
                                    process_waitResource_time[current_process['id']] += start_time
                                    if not (sorted_processes or ready_queue):
                                        print("deadlock detected")

                                    break
                                else:
                                    current_process['cpu time'].remove(burst)    # remove the request if the resource is already with the process
                                    continue
                            else:
                                reg.add_assignment(burst['resource']['rid'], current_process['id'])     # assign the resource to process if is free
                                current_process['cpu time'].remove(burst)  # remove the request if the resource is already with the process
                                continue

                    if availableTime[current_process['id']] > start_time:
                        start_time = availableTime[current_process['id']]

                    # Calculate execution time (min of time quantum or remaining burst time)
                    execution_time = min(time_quantum, burst['time'])
                    stop_time = start_time + execution_time

                    cpu_burst.append((current_process['id'], (start_time, stop_time)))

                    # Update remaining time in the burst
                    burst['time'] -= execution_time

                    process_run_time[current_process['id']] += execution_time

                    # Update the current time
                    start_time = stop_time

                    availableTime[current_process['id']] = start_time

                    if burst['time'] > 0:   # If burst is not complete, add the process to the ready queue
                        ready_queue.append(current_process)
                        break

                    else:
                        current_process['cpu time'].remove(burst)    # remove the burst
                        if current_process['cpu time']:     # check if the process has another cpu burst
                            ready_queue.append(current_process)
                            break

                elif burst['type'] == 'IO':
                    availableTime[current_process['id']] += burst['time']
                    burst['time'] = 0
                    if len(current_process['cpu time']) > 1:    # if there is cpu burst remaining append the process in waiting queue
                        waiting_queue.append(current_process)
                    break

        else:
            # If no processes are ready, advance time to the next process available
            if sorted_processes:
                start_time = availableTime[sorted_processes[0]['id']]

    # Print results
    wfg = convert_rag_to_wfg(reg)
    wfg.display()
    detect_deadlock(wfg)

    print("CPU Burst Execution Details:")
    for burst in cpu_burst:
        print(f"Process {burst[0]}: Start Time = {burst[1][0]}, Stop Time = {burst[1][1]}")

    Avg_waiting, Avg_turnaround = calculate_waiting_and_turnaround_time(processes, terminated_process_times,
                                                                        availableTime, process_waitResource_time)
    print("\naverage waiting time = ", Avg_waiting)
    print("average turnaround time = ", Avg_turnaround)
    print("execution time = ", stop_time)

    draw_gantt_chart(cpu_burst)

def calculate_waiting_and_turnaround_time(processes, terminated_process_times, process_finish_times, process_waitResource_time):
    total_waiting_time = 0
    total_turnaround_time = 0

    for process in processes:
        process_id = process['id']
        arrival_time = int(process['arrive'])
        finish_time = process_finish_times[process_id]

        io_time = sum(burst['time'] for burst in process['cpu time'] if burst['type'] == 'IO')
        cpu_time = sum(burst['time'] for burst in process['cpu time'] if burst['type'] == 'CPU')
        resource_waiting = process_waitResource_time[process_id]

        # Calculate turnaround time and waiting time
        turnaround_time = finish_time - arrival_time
        total_turnaround_time += turnaround_time

        terminated_time = terminated_process_times.get(process_id, 0)
        waiting_time = turnaround_time - cpu_time - io_time - terminated_time - resource_waiting

        total_waiting_time += waiting_time

        print(
            f"Process {process_id} - Arrival: {arrival_time}, Finish: {finish_time}, Turnaround: {turnaround_time}, CPU Time: {cpu_time}, IO Time: {io_time}, waiting resource: {resource_waiting}, execution before terminated: {terminated_time}, Waiting Time: {waiting_time}")

    # Calculate average waiting and turnaround time
    average_waiting_time = total_waiting_time / len(processes) if processes else 0
    average_turnaround_time = total_turnaround_time / len(processes) if processes else 0
    return average_waiting_time, average_turnaround_time


def get_process_with_max_requests(deadlocked_cycles, processes, reg):
    def get_required_resources_for_process(process):
        # Use a set to collect unique resource IDs
        required_resources = set()

        for burst in process.get('cpu time', []):
            if burst['resource'] is not None:
                required_resources.add(burst['resource']['rid'])

        return len(required_resources)

    process_resource_requests = {}

    for cycle in deadlocked_cycles:
        for process_id in cycle:
            process = next(p for p in processes if p['id'] == process_id)
            # Get the number of requested resources for this process
            requested_resources_count = get_required_resources_for_process(process)
            process_resource_requests[process_id] = requested_resources_count

    # Find the process with the most requests
    process_with_most_requests = max(process_resource_requests, key=process_resource_requests.get)

    # Find all processes with the maximum value
    processes_with_max_requests = [
        process_id for process_id, count in process_resource_requests.items() if count == max(process_resource_requests.values())
    ]
    if len(processes_with_max_requests) > 1:
        print("Multiple processes have the same maximum number of requests:", processes_with_max_requests)
        process_request_counts = {
            process: len(reg.request_queue.get(process, []))
            for process in processes_with_max_requests
        }
        # Select the process with the most resource requests
        process_to_terminate = max(process_request_counts, key=process_request_counts.get)
        return process_to_terminate

    return process_with_most_requests

def recover_deadlock(deadlock_cycles, rag, waiting_queue, processed_time, processes, available_Time, startTime):
    """
    Recovers from a detected deadlock by terminating processes.
    Prioritizes terminating processes with the most resource requests.
    """
    print("Starting deadlock recovery...")
    terminated_processes = set()
    terminated_process_times = {}

    # Flatten deadlock cycles into a unique set of processes
    deadlocked_processes = set(process for cycle in deadlock_cycles for process in cycle)

    while deadlocked_processes:
        # Select the process with the most resource requests
        process_to_terminate = get_process_with_max_requests(deadlock_cycles, processes, rag)

        # Terminate the selected process
        print(f"Terminating process {process_to_terminate} to resolve deadlock.")
        terminated_processes.add(process_to_terminate)
        terminated_process_times[process_to_terminate] = processed_time.get(process_to_terminate, 0)
        deadlocked_processes.remove(process_to_terminate)

        # Release all resources held by the terminated process
        for resource, assigned_process in list(rag.assignment_edges.items()):
            if assigned_process == process_to_terminate:
                print(f"Releasing resource {resource} held by process {process_to_terminate}.")
                rag.release_resource(resource, process_to_terminate)

        # Remove the terminated process from and waiting queues
        waiting_queue[:] = [process for process in waiting_queue if process['id'] != process_to_terminate]
        available_Time[process_to_terminate] = startTime

        if terminated_processes:
            print("Terminated Processes:", terminated_processes)
            # Add only the processes from processes_copy whose IDs match the terminated_processes
            processes_copy = copy.deepcopy(processes)
            terminated_process_objects = [p for p in processes_copy if p['id'] in terminated_processes]
            waiting_queue.extend(terminated_process_objects)

        # Check for remaining deadlock
        wfg = convert_rag_to_wfg(rag)
        has_deadlock, remaining_cycles = detect_deadlock(wfg)
        if not has_deadlock:
            print("Deadlock resolved successfully.")
            return terminated_process_times

        # Update the deadlock cycles and processes
        deadlock_cycles = remaining_cycles
        deadlocked_processes = set(process for cycle in deadlock_cycles for process in cycle)

    print("Deadlock recovery complete.")
    return terminated_process_times


def draw_gantt_chart(cpu_burst):
    """
    Draws a Gantt chart for CPU bursts.

    Parameters:
        cpu_burst (list): List of tuples where each tuple contains:
                          (process_id, (start_time, stop_time)).
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 4))

    # Assign a unique color to each process
    process_ids = sorted(set(burst[0] for burst in cpu_burst))
    colors = {pid: (random.random(), random.random(), random.random()) for pid in process_ids}

    # Plot each burst as a horizontal bar
    for process_id, (start_time, stop_time) in cpu_burst:
        ax.broken_barh([(start_time, stop_time - start_time)], (0.5, 1),
                       facecolors=colors[process_id], edgecolors='black', linewidth=1)
        ax.text((start_time + stop_time) / 2, 1, f"P{process_id}",
                ha='center', va='center', color='white', fontsize=10)

    # Set labels and title
    ax.set_yticks([])  # Remove Y-axis ticks as all processes are on the same line
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart for CPU Bursts")
    ax.set_xlim(0, max(burst[1][1] for burst in cpu_burst) + 5)  # Add padding to the end

    # Add legend
    legend_patches = [plt.Line2D([0], [0], color=colors[pid], lw=6, label=f"Process {pid}") for pid in process_ids]
    ax.legend(handles=legend_patches, loc='upper right', title="Processes")

    plt.show()


def convert_rag_to_wfg(rag):
    wfg = WaitForGraph()
    for process in rag.processes:
        wfg.add_process(process)

    # Process request_queue to add edges based on queued requests
    for resource, queue in rag.request_queue.items():
        assigned_process = rag.assignment_edges.get(resource)
        if assigned_process is not None:
            for process in queue:
                wfg.add_edge(process, assigned_process)  # Add an edge in WFG from 'process' to 'assigned_process'

    return wfg


def detect_deadlock(wfg):
    visited = set()
    rec_stack = set()
    deadlock_cycles = []

    def dfs(process, path):
        visited.add(process)
        rec_stack.add(process)
        path.append(process)

        for neighbor in wfg.graph.get(process, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                cycle_start_index = path.index(neighbor)
                cycle = path[cycle_start_index:]
                deadlock_cycles.append(cycle)
                return True
        rec_stack.remove(process)
        path.pop()
        return False

    for process in wfg.graph:
        if process not in visited:
            if dfs(process, []):
                break

    if deadlock_cycles:
        print("Deadlock detected involving the following processes:")
        for cycle in deadlock_cycles:
            cycle_str = " → ".join(map(str, cycle + [cycle[0]]))
            print(f"  Cycle: {cycle_str}")
        return True, deadlock_cycles
    else:
        return False, None

def main():
    processes = readFile()
    for process in processes:
        print(process)

    priority_schedule_with_round_robin(processes, 5)

main()
