
import m5
from m5.objects import *
from core import *
from caches import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('binary', type = str, help = "Path to binary to run")
args = parser.parse_args()

class MySystem(System):

  def __init__(self):
    super(MySystem, self).__init__()

    self.clk_domain = SrcClockDomain()
    self.clk_domain.clock = '3.5GHz'
    self.clk_domain.voltage_domain = VoltageDomain()

    self.mem_mode = 'timing'
    self.mem_ranges = [AddrRange('16GB')] # Need to change this

    self.cpu = BaseConfig()

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
    self.membus = SystemXBar()

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
    self.mem_ctrl =  DDR4_2400_8x8()
    self.mem_ctrl.range = self.mem_ranges[0]
    self.mem_ctrl.port = self.membus.master

  def setTestBinary(self, binary_path):
        """Set up the SE process to execute the binary at binary_path"""
        from m5 import options
        self.cpu.workload = Process(
                          cmd = [binary_path])
        self.cpu.createThreads()

