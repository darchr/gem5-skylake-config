# -*- coding: utf-8 -*-
# Copyright (c) 2020 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Jason Lowe-Power, Trivikram Reddy

import m5
from m5.objects import *
from core import *
from caches import *
import argparse

class MySystem(System):

  _CPUModel = BaseCPU

  def __init__(self):
    super(MySystem, self).__init__()

    self.clk_domain = SrcClockDomain()
    self.clk_domain.clock = '3.5GHz'
    self.clk_domain.voltage_domain = VoltageDomain()

    self.mem_mode = 'timing'
    self.mem_ranges = [AddrRange('32768MB')] # Need to change this

    self.cpu = self._CPUModel()

    # Create an L1 instruction and data cache
    self.cpu.icache = L1ICache()
    self.cpu.dcache = L1DCache()

    # Connect the instruction and data caches to the CPU
    self.cpu.icache.connectCPU(self.cpu)
    self.cpu.dcache.connectCPU(self.cpu)

    # Create a memory bus, a coherent crossbar, in this case
    self.l2bus = L2XBar(width = 64)

    # Hook the CPU ports up to the l2bus
    self.cpu.icache.connectBus(self.l2bus)
    self.cpu.dcache.connectBus(self.l2bus)

    # Create an L2 cache and connect it to the l2bus
    self.l2cache = L2Cache()
    self.l2cache.connectCPUSideBus(self.l2bus)

    # Create a memory bus, a coherent crossbar, in this case
    self.l3bus = L3XBar()

    # Connect the L2 cache to the l3bus
    self.l2cache.connectMemSideBus(self.l3bus)

    # Create an L3 cache and connect it to the l3bus
    self.l3cache = L3Cache()
    self.l3cache.connectCPUSideBus(self.l3bus)

    # Create a memory bus
    self.membus = SystemXBar(width = 64)

    # Connect the L2 cache to the membus
    self.l3cache.connectMemSideBus(self.membus)

    # create the interrupt controller for the CPU
    self.cpu.createInterruptController()

    self.cpu.interrupts[0].pio = self.membus.master
    self.cpu.interrupts[0].int_master = self.membus.slave
    self.cpu.interrupts[0].int_slave = self.membus.master

    # Connect the system up to the membus
    self.system_port = self.membus.slave

    # Create a DDR4 memory controller
    self.mem_ctrl =  DDR4_2400_16x4()
    self.mem_ctrl.range = self.mem_ranges[0]
    self.mem_ctrl.port = self.membus.master

  def setTestBinary(self, binary_path):
        """Set up the SE process to execute the binary at binary_path"""
        from m5 import options
        self.cpu.workload = Process(
                          cmd = [binary_path])
        self.cpu.createThreads()

