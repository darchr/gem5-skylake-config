import m5
from m5.objects import *
import argparse
from system import MySystem
from system.core import *

valid_configs = [UnCalibCPU, CalibCPU, MaxCPU]
valid_configs = {cls.__name__[:-3]:cls for cls in valid_configs}

parser = argparse.ArgumentParser()
parser.add_argument('config', choices = valid_configs.keys())
parser.add_argument('binary', type = str, help = "Path to binary to run")
args = parser.parse_args()

class TestSystem(MySystem):
    _CPUModel = valid_configs[args.config]

system = TestSystem()
system.setTestBinary(args.binary)
root = Root(full_system = False, system = system)
m5.instantiate()

exit_event = m5.simulate()

if exit_event.getCause() != 'exiting with last active thread context':
    print("Benchmark failed with bad exit cause.")
    print(exit_event.getCause())
    exit(1)
if exit_event.getCode() != 0:
    print("Benchmark failed with bad exit code.")
    print("Exit code {}".format(exit_event.getCode()))
    exit(1)
