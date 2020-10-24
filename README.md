# gem5 skylake config

This repo contains experiments to study performance of gem5 against a real hardware. The experiments are based on [gem5art](https://github.com/darchr/gem5art) framework.

## Repo structure

* gem5-configs: contains python scripts that configure for skylake micro-architecture in gem5.
  * system/`core.py`: contains the below CPU classes.
    * UnCalibCPU: configured based on the documentation available for the micro-architecture.
    * CalibCPU: considering the absence of certain features in gem5, for example, absence micro-op fusion in gem5, this configuration offsets such deficiencies by improving some other parameters.
    * MaxCPU: models a CPU with maximum pipeline widths, minimum pipeline and instruction latencies.
  * system/`caches.py`: classic cache model.
  * system/`MESI_Two_Level.py`: Ruby cache system for MESI protocol.
  * system/`se.py`: sets a system to run experiments in SE mode.
  * system/`fs.py`: sets a system to run experiments in FS mode.
  * `run-se.py`: SE mode run script.
  * `run-spec-fs.py`: FS mode run script.
* results: contains the experiment results.
* `launch_microbm_experiment.py`: script to launch the microbenchmark experiments.
* `launch_spec2006_experiment.py`: script to launch the spec2006 experiments.

## Running experiments

**Note**: The following steps describe how to setup and run experiments with microbenchmarks, refer this [tutorial](https://gem5art.readthedocs.io/en/latest/tutorials/spec2006-tutorial.html) for running experiments with spec2006.

### Step 1 - Clone this repo

```bash
git clone https://github.com/darchr/gem5-skylake-config.git
cd gem5-skylake-config
```

### Step 2 - Clone and build gem5

```bash
git clone https://gem5.googlesource.com/public/gem5
cd gem5
scons build/X86/gem5.opt -j8
```

### Step 3 - Clone and build microbenchmarks

```bash
git clone https://github.com/darchr/microbench.git
# Checkout adjust-ters branch, this branch contains benchmarks with different iteration to capture complete behavior of sim-objects in gem5.
cd microbench
git fetch --all
git checkout adjust-iters
# Build the benchmarks
make
cd ..
```

### Step 4 - Setup the environment

```bash
# Create a virtual python3 environment before using gem5art
virtualenv -p python3 venv
source venv/bin/activate

# gem5art can be installed using pip
pip install gem5art-artifact gem5art-run gem5art-tasks
```

### Step 5 - Create a database

```bash
docker run -p 27017:27017 -v <absolute path to the created directory>:/data/db --name mongo-<some tag> -d mongo
```

### Step 6 - launching the experiment

```bash
# To launch experiment for the Calib config and control flow benchmarks
python launch_experiment.py Calib ctrl
# To launch experiment for the all configs and all benchmarks
python launch_experiment.py all all
```

## References

These are primary references for skylake micro-architecture.

1. [Agner Fog, Microarchitecture of Intel and CPUs](https://www.agner.org/optimize/microarchitecture.pdf)
2. [Agner Fog, Instruction tables](https://www.agner.org/optimize/instruction_tables.pdf)
3. [Wikichip, Skylake Microarchitecture(server)](https://en.wikichip.org/wiki/intel/microarchitectures/skylake_(server))
4. [Intel, Architecture Optimization Manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-optimization-manual.pdf)

These are for configuring a micro-architecture in gem5

1. [gem5 haswell config](https://github.com/ayaz91/gem5Valid_Haswell)
2. [A Study on the Impact of Instruction Set Architectures on Processor's Performance](https://scholarworks.wmich.edu/cgi/viewcontent.cgi?article=2517&context=masters_theses)
