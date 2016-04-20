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

# Add your library functions here.


def check_failed_services(enode):
    '''
    List failed services
    :rtype: list
    :return: The list of failed services or None
    '''
    cmd = ("systemctl list-units  -all --state=failed | grep failed | " +
        "awk '{print $2;}'")
    retval = enode(cmd, shell='bash')
    if retval is "":
        return None
    else:
        return retval.split()
__all__ = [
    'check_failed_services'
]
