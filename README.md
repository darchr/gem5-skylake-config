# gem5 skylake config

This repo contains experiments to study performance of gem5 against a real hardware. The experiments are based on [gem5art](https://github.com/darchr/gem5art) framework.

### Repo structure:
* gem5-configs: contains gem5 configs for skylake micro-architecture.
    * system/core.py: contains the below CPU classes.
        * UnCalibCPU: configured based on the documentation available for the micro-architecture.
        * CalibCPU: considering the absence of certain features in gem5, for example, gem5 doesn't support micro-op fusion and micro-op cache, this configuration offsets those difficiencies by improving some other parameters.
        * MaxCPU: models a CPU with maximum pipeline widths, minimum pipeline and instruction latencies. 
    * system/caches.py: configuration based on classic cache model.
    * system/system.py: connects core and memory together to form a system.
    * `run.py`: script to pass parameters to the system.
* results: contains the experiment's results.
* `launch_experiment.py`: script to launch the experiments.

### Running experiments:
We are using [microbenchmarks](https://github.com/darchr/microbench) for validating the performance and this [tutorial](https://gem5art.readthedocs.io/en/latest/tutorials/microbench-tutorial.html) explains how to setup experiements with these benchmarks.
We are using intel's PCM to measure the hardware counter values, this [repo](https://github.com/darchr/PCM-microbenchmark-experiments/blob/master/Validation.md) explains how to use PCM for these benchmarks.

### References:
These are primary references for skylake micro-architecture.
* [Intel® 64 and IA-32 Architectures Optimization Reference Manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-optimization-manual.pdf)
* [The microarchitecture of Intel and AMD CPUs](https://en.wikichip.org/wiki/intel/microarchitectures/skylake_(client))
* [Skylake (client) - Microarchitectures - Intel](https://www.agner.org/optimize/microarchitecture.pdf)

These are for configuring a micro-architecture in gem5
* [gem5 haswell config](https://github.com/ayaz91/gem5Valid_Haswell)
* [A Study on the Impact of Instruction Set Architectures on Processor's Performance](https://scholarworks.wmich.edu/cgi/viewcontent.cgi?article=2517&context=masters_theses)


