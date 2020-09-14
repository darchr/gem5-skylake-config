# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jason Lowe-Power
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

class MySystem(System):

  _CPUModel = BaseCPU

  def __init__(self):
    super(MySystem, self).__init__()

    self.clk_domain = SrcClockDomain()
    self.clk_domain.clock = '3.5GHz'
    self.clk_domain.voltage_domain = VoltageDomain()

    self.mem_mode = 'timing'
    mem_size = '32GB'
    self.mem_ranges = [AddrRange('100MB'), # For kernel
                      AddrRange(0xC0000000, size=0x100000), # For I/0
                      AddrRange(Addr('4GB'), size = mem_size) # All data
                        ]

    self.cpu = self._CPUModel()

    # Create a memory bus
    self.membus = SystemXBar(width = 64)
    self.membus.badaddr_responder = BadAddr()
    self.membus.default = Self.badaddr_responder.pio

    # Set up the system port for functional access from the simulator
    self.system_port = self.membus.cpu_side_ports

    # Create an L1 instruction and data cache
    self.cpu.icache = L1ICache()
    self.cpu.dcache = L1DCache()
    self.cpu.mmucache = MMUCache()

    # Connect the instruction and data caches to the CPU
    self.cpu.icache.connectCPU(self.cpu)
    self.cpu.dcache.connectCPU(self.cpu)
    self.cpu.mmucache.connectCPU(self.cpu)

    # Create a memory bus, a coherent crossbar, in this case
    self.l2bus = L2XBar(width = 96)

    # Hook the CPU ports up to the l2bus
    self.cpu.icache.connectBus(self.l2bus)
    self.cpu.dcache.connectBus(self.l2bus)
    self.cpu.mmucache.connectBus(self.l2bus)

    # Create an L2 cache and connect it to the l2bus
    self.l2cache = L2Cache()
    self.l2cache.connectCPUSideBus(self.l2bus)

    # Create a memory bus, a coherent crossbar, in this case
    self.l3bus = L2XBar(width = 64,
                        snoop_filter = SnoopFilter(max_capacity='32MB'))

    # Connect the L2 cache to the l3bus
    self.l2cache.connectMemSideBus(self.l3bus)

    # Create an L3 cache and connect it to the l3bus
    self.l3cache = L3Cache()
    self.l3cache.connectCPUSideBus(self.l3bus)

    # Connect the L3 cache to the membus
    self.l3cache.connectMemSideBus(self.membus)

    # create the interrupt controller for the CPU
    self.cpu.createInterruptController()

    self.cpu.interrupts[0].pio = self.membus.mem_side_ports
    self.cpu.interrupts[0].int_requestor = self.membus.cpu_side_ports
    self.cpu.interrupts[0].int_responder = self.membus.mem_side_ports

    self.createMemoryControllersDDR4()

    # provide cache paramters for verbatim CPU
    if (self._CPUModel is VerbatimCPU):
      # L1I-Cache
      self.cpu.icache.size = '32kB'
      self.cpu.icache.tag_latency = 4
      self.cpu.icache.data_latency = 4
      self.cpu.icache.response_latency = 2
      # L1D-Cache
      self.cpu.dcache.tag_latency = 4
      self.cpu.dcache.data_latency = 4
      self.cpu.dcache.response_latency = 2
      # L2-Cache
      self.l2cache.tag_latency = 12
      self.l2cache.data_latency = 14
      self.l2cache.response_latency = 4
      # L3-Cache
      self.l3cache.tag_latency = 41
      self.l3cache.data_latency = 44
      self.l3cache.response_latency = 12

  # Memory latency: Using the smaller number from [3]: 96ns
  def createMemoryControllersDDR4(self):
    self._createMemoryControllers(8, DDR4_2400_16x4)

  def _createMemoryControllers(self, num, cls):
    kernel_controller = self._createKernelMemoryController(cls)

    ranges = self._getInterleaveRanges(self.mem_ranges[-1], num, 6, 20)
    self.mem_cntrls = [
        MemCtrl(dram = cls(range = ranges[i]), port = self.membus.mem_side_ports)
        for i in range(num)
    ] + [kernel_controller]

  def _createKernelMemoryController(self, cls):
    return MemCtrl(dram = cls(range = self.mem_ranges[0]), port = self.membus.mem_side_ports)

  def _getInterleaveRanges(self, rng, num, intlv_low_bit, xor_low_bit):
    from math import log
    bits = int(log(num, 2))
    if 2**bits != num:
        m5.fatal("Non-power of two number of memory controllers")

    intlv_bits = bits
    ranges = [
        AddrRange(start=rng.start,
                  end=rng.end,
                  intlvHighBit = intlv_low_bit + intlv_bits - 1,
                  xorHighBit = xor_low_bit + intlv_bits - 1,
                  intlvBits = intlv_bits,
                  intlvMatch = i)
            for i in range(num)
        ]

    return ranges

  def setTestBinary(self, binary_path):
    """Set up the SE process to execute the binary at binary_path"""
    from m5 import options
    self.cpu.workload = Process(
                      cmd = [binary_path])
    self.cpu.createThreads()
