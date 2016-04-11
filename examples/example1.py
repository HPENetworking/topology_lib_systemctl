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
topology_lib_system_control example 1.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

import topology_lib_system_control  # noqa

TOPOLOGY = """
# |        |
# |        |
# |  ops1  |
# |        |
# |        |

# Nodes
[type=openswitch name="OpenSwitch 1"] ops1

# Links
"""

# Add your library functions here.


def test_systemfail(topology):
    ops1 = topology.get('ops1')

    assert ops1 is not None

    if ops1.libs.system_control.check_system_services():
        print("Switch has failed services..")
        raise Exception("Exiting")
    else:
        print("All good!")
