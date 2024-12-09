#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py
Author: aomar47
Semester: Fall2024

The python code in this file is original work written by
"Azra Omar". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or online resource. I have not shared this python script
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Assignment2 VersionA
'''

import argparse
import os, sys

def parse_command_args() -> argparse.Namespace:
    """Set up argparse for command-line arguments."""
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action='store_true', help="Prints sizes in human readable format.")
    parser.add_argument("program", type=str, nargs='?', help="If a program is specified, show memory use of all associated processes. Show only total use if not.")
    return parser.parse_args()

def percent_to_graph(percent: float, length: int=20) -> str:
    """Convert a percentage to a bar graph string."""
   
    # To ensure percent is within the range [0, 1]
    if percent < 0:
        percent = 0
    elif percent > 1:
        percent = 1

    # Calculate the number of hashes to represent the percentage
    hashes = int(round(percent * length))  # Convert percent to number of hashes
    spaces = length - hashes  # Calculate remaining spaces to fill the bar length

    # Create the graph part of the string
    graph_part = f"{'#' * hashes}{' ' * spaces}"  # Construct the bar graph string
    return graph_part

def get_sys_mem() -> int:
    """Get the total system memory from /proc/meminfo."""
    total_mem = 0
    # Open /proc/meminfo to read memory info
    f = open('/proc/meminfo', 'r')
    for line in f:
        if line.startswith('MemTotal:'):
            # Extract total memory value from the line
            total_mem = int(line.split()[1])  # Get the value and convert to integer
            f.close()  
            return total_mem
    f.close()

    return total_mem

def get_avail_mem() -> int:
    """Get the available system memory from /proc/meminfo."""
    avail_mem = 0
   
    # Open /proc/meminfo to read memory info
    f = open('/proc/meminfo', 'r')
    for line in f:
        if line.startswith('MemAvailable:'):
            # Extract available memory value from the line
            avail_mem = int(line.split()[1])  # Get the value and convert to integer
            f.close()  
            return avail_mem
    f.close()
   
    return avail_mem

def pids_of_prog(program_name: str) -> list:
    """Get a list of PIDs for the specified program."""
    # Retrieve process IDs for the given program
    pids = os.popen(f"pidof {program_name}").read().strip()
    if pids:
        return pids.split()
    return []

def rss_mem_of_pid(pid: str) -> int:
    """Get the RSS memory usage of a process given its PID."""
    mem_total = 0
    try:
        # Open the smaps file for the given PID
        smaps_path = f"/proc/{pid}/smaps"  # Path to the memory usage information
        f = open(smaps_path, 'r')
        for line in f:
            if line.startswith('Rss'):
                # Sum the RSS memory usage from the smaps file
                mem_total += int(line.split()[1])  # Add RSS memory value to the total
        f.close()  
        return mem_total
    except FileNotFoundError:
        # Return 0 if the PID file is not found
        return 0

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "Turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']   # iB indicates 1024
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024  # Convert to the next size unit
        suf_count += 1  # Increment suffix index
    str_result = f'{result:.{decimal_places}f} '  # Format result with decimal places
    str_result += suffixes[suf_count]  # Append appropriate unit
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
   
    if args.program:
        # If a specific program is specified
        pids = pids_of_prog(args.program)
        if pids:
            # Filter for running processes only
            pids = [pid for pid in pids if os.path.exists(f"/proc/{pid}")]  # Check if PID directory exists
            total_mem = get_sys_mem()
            for pid in pids:
                mem_used = rss_mem_of_pid(pid)  
                percent_used = mem_used / total_mem if total_mem else 0  # Calculate percentage of used memory
                if args.human_readable:
                    # Display memory usage in human-readable format (MiB)
                    mem_used_human = mem_used / 1024  # Convert memory used to MiB
                    total_mem_human = total_mem / 1024  # Convert total memory to MiB
                    print(f"{pid} [{percent_to_graph(percent_used, length=args.length)} | {percent_used:.0%}] {mem_used_human}/{total_mem_human}")
                else:
                    # Display memory usage in kB
                    print(f"{pid} [{percent_to_graph(percent_used, length=args.length)} | {percent_used:.0%}] {mem_used}/{total_mem}")
            mem_total = sum(rss_mem_of_pid(pid) for pid in pids)  # Sum memory usage for all PIDs
            percent_total = mem_total / total_mem if total_mem else 0  # Calculate percentage of total memory used
            if args.human_readable:
                # Display total memory usage in human-readable format
                mem_total_human = bytes_to_human_r(mem_total)
                total_mem_human = bytes_to_human_r(total_mem)
                print(f"{args.program} [{percent_to_graph(percent_total, length=args.length)} | {percent_total:.0%}] {mem_total_human}/{total_mem_human}")
            else:
                # Display total memory usage in kB
                print(f"{args.program} [{percent_to_graph(percent_total, length=args.length)} | {percent_total:.0%}] {mem_total}/{total_mem}")
        else:
            # Print message if no processes are found for the given program
            print(f"{args.program + ' not found.'}")
    else:
        # Default behavior: show total memory usage
        total_mem = get_sys_mem()
        avail_mem = get_avail_mem()
        used_mem = total_mem - avail_mem  # Calculate used memory
        percent_used = used_mem / total_mem if total_mem else 0  # Calculate percentage of used memory
        mem_usage_graph = percent_to_graph(percent_used, length=args.length)  # Create graph representation of memory usage
        if args.human_readable:
            # Display memory usage in human-readable format (GiB)
            total_mem_gb = bytes_to_human_r(total_mem)  
            used_mem_gb = bytes_to_human_r(used_mem)  
            avail_mem_gb = bytes_to_human_r(avail_mem)
            print(f"Memory     {mem_usage_graph} {used_mem_gb}/{total_mem_gb}")
        else:
           # Display memory usage in kB
           print(f"Memory  [{mem_usage_graph} | {percent_used:.0%}] {used_mem}/{total_mem}")  # Print memory usage graph


