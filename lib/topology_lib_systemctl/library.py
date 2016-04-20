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
topology_lib_systemctl communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division
import time

# Add your library functions here.


def check_failed_services(enode):
    '''
    List failed services

    :rtype: list
    :return: The list of failed services or None
    '''
    cmd = ("systemctl list-units -all --state=failed | grep failed | " +
        "awk '{print $2;}'")
    output = enode(cmd, shell='bash')
    output = output.split('\n')
    print(output)
    retval = []
    for line in output:
        if "systemctl list-units" not in line:
            retval.append(line)
    if retval is "":
        return None
    else:
        return None


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
    buffer1 = output.split('\n')

    for line in buffer1:
        if line.split()[0] == 'MemTotal:':
            mem_info["memTotal"] = line.split()[1]
        if line.split()[0] == 'MemFree:':
            mem_info["memFree"] = line.split()[1]
        if line.split()[0] == 'Cached:':
            mem_info["cached"] = line.split()[1]
    return mem_info


def memory_leak_check(enode, init_val, final_val, leakage_threshold):

    """
    This function calculates the memory usage for initial and final instances
    and compares the difference with the leakage threshold to generate a
    verdict to declare that there is a leakage or not.
    :param topology.platforms.base.BaseNode enode: Engine node to communicate
     with.
    :init_val is the memory usage dictionary value which is returned from
     the routine get_memory_usage() at some time of instance, say before the
     execution of some test.
    :final_val is the memory usage dictionary value which is returned from
     the routine get_memory_usage() at some other time of instance say after
     the test of execution.
    :leakage_threshold is the allowed memory usage difference from init to
     final and beyond which it can be considered as memory leakage for the
     result verdict.
    :returns 1 for leakage detection and 0 for no leakage
    """
    verdict = 0
    assert init_val
    assert final_val
    init_used_mem = int(init_val["memTotal"]) - (int(init_val["memFree"]) +
                                                 int(init_val["cached"]))

    final_used_mem = int(final_val["memTotal"]) - (int(final_val["memFree"]) +
                                                   int(final_val["cached"]))
    if (abs(final_used_mem - init_used_mem) <= leakage_threshold):
        verdict = 0
    else:
        verdict = 1
    return verdict


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
    buffer1 = output.split('\n')
    line = buffer1[0]
    spl = line.split(" ")
    last_worktime = int(spl[2]) + int(spl[3]) + int(spl[4])
    last_idletime = int(spl[5])
    time.sleep(0.005)
    output = enode("cat /proc/stat", shell="bash")
    assert 'cpu' in output
    buffer1 = output.split('\n')
    line = buffer1[0]
    spl = line.split(" ")
    worktime = int(spl[2]) + int(spl[3]) + int(spl[4])
    idletime = int(spl[5])
    dworktime = (worktime - last_worktime)
    didletime = (idletime - last_idletime)
    rate = float(dworktime) / (didletime + dworktime)
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
        command = "taskset --cpu-list " + str(cpu_core) + " python pyload.py&"
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
        command = "kill " + process_id
        enode(command, shell="bash")
    command = "\n"
    enode(command, shell="bash")


def list_all_units(enode):
    '''
    List all system units
    :rtype: list
    :return: The list of all system units or None
    '''
    cmd = ("systemctl list-units  -all | tail -n+2 | head -n -7")
    retval = enode(cmd, shell='bash')
    retval = retval.split('\n')

    print(retval)

    ret_list = []
    for line in retval:
        if "failed" in line or "not-found" in line:
            ret_list.append(line[2])
        else:
            ret_list.append(line[0])
    if len(ret_list) is 0:
        return None
    else:
        return ret_list


def reload_service_units(enode, services_list):
    '''
    Reloads system service units
    Parameters: List of strings

    :rtype: boolean
    :return: "True" if succesful
    '''

    assert len(services_list) > 0, "services list is empty"

    for service in services_list:
        cmd_restart = ("systemctl restart " + service)
        retval_restart = enode(cmd_restart, shell='bash')
        assert "Failed" not in retval_restart, "Services unable to restart"

    return True


def list_loaded_units(enode):
    '''
    List loaded system units

    :rtype: list
    :return: The list of all loaded units or None
    '''
    cmd = ("systemctl list-units  --state=loaded | awk '{print $1 $2;}' | " +
     "tail -n+2 | head -n -7")
    retval = enode(cmd, shell='bash')

    if retval is "":
        return None
    else:
        return retval.split()

__all__ = [
    'check_failed_services',
    'get_memory_usage',
    'memory_leak_check',
    'get_cpu_usage',
    'cpu_load',
    'cpu_unload',
    'list_all_units',
    'reload_service_units',
    'list_loaded_units'
]
