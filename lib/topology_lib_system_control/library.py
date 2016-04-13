# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
topology_lib_system_control communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from time import sleep

# Add your library functions here.


def check_system_services(enode):
    #
    # returns None if no failed system services
    #
    # otherwise returns the list of the failed services
    #
    cmd = ("systemctl list-units  -all --state=failed | grep failed | " +
           "awk '{print $2;}'")
    retval = enode(cmd, shell='bash')
    if retval is "":
        return None
    else:
        return retval


def get_memory_usage(enode):

    """
    This function reads /proc/meminfo file for enode and parses it to return
    MemTotal,MemFree and Cached values in a dictionary format.

    :param topology.platforms.base.BaseNode enode: Engine node to communicate
     with.
    """
    mem_info = {}
    output = enode("cat /proc/meminfo", shell="bash")
    assert 'MemTotal' in output
    buffer = output.split('\n')

    for line in buffer:
        if line.split()[0] == 'MemTotal:':
            mem_info["memTotal"] = line.split()[1]
        if line.split()[0] == 'MemFree:':
            mem_info["memFree"] = line.split()[1]
        if line.split()[0] == 'Cached:':
            mem_info["cached"] = line.split()[1]
    return mem_info


def get_cpu_usage(enode):

    """
    This function reads /proc/stat file for enode and parses it to get
    cpu usage and calculate relative usage rate relative to a small time.

    :param topology.platforms.base.BaseNode enode: Engine node to communicate
     with.
    """
    last_worktime = 0
    last_idletime = 0
    output = enode("cat /proc/stat", shell="bash")
    assert 'cpu' in output
    buffer = output.split('\n')
    line = buffer[0]
    spl = line.split(" ")
    last_worktime = int(spl[2])+int(spl[3])+int(spl[4])
    last_idletime = int(spl[5])
    sleep(0.005)
    output = enode("cat /proc/stat", shell="bash")
    assert 'cpu' in output
    buffer = output.split('\n')
    line = buffer[0]
    spl = line.split(" ")
    worktime = int(spl[2])+int(spl[3])+int(spl[4])
    idletime = int(spl[5])
    dworktime = (worktime-last_worktime)
    didletime = (idletime-last_idletime)
    rate = float(dworktime)/(didletime+dworktime)
    return rate


def cpu_load(enode):

    """
    This function reads /proc/cpuinfo to get the CPU cores count and execute
    a python script to create a load on all of the CPU cores.

    :param topology.platforms.base.BaseNode enode: Engine node to communicate
     with.
    """
    processid_list = []
    output = enode("cat /proc/cpuinfo | grep processor | wc -l", shell="bash")
    cores_count = int(output)
    print(cores_count)
    for cpu_core in range(0, cores_count):
        command = "taskset --cpu-list "+str(cpu_core)+" python pyload.py&"
        output = enode(command, shell="bash")
        assert output.find("failed") != 1, "could not start the process"
        processid_list.append(output.split(" ")[1])
    return processid_list


def cpu_unload(enode, processid_list):

    """
    This function kills the processes in the passed list to unload cpu cores

    :param topology.platforms.base.BaseNode enode: Engine node to communicate
     with.

    :processid_list contains list of process-ids to be killed
    """
    assert len(processid_list) > 0, "processes list is empty"
    for process_id in processid_list:
        command = "kill -9 "+process_id
        enode(command, shell="bash")
    command = "\n"
    enode(command, shell="bash")

__all__ = [
    'check_system_services',
    'get_memory_usage',
    'get_cpu_usage',
    'cpu_load',
    'cpu_unload'
]
