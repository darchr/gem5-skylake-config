# Configuration Details

This documents describes configuration deatials of skylake micro-architecture in gem5.

The following configs are created in order the understand the impact of configuration details on performance.

* UnCalibCPU: configured based on the available micro-architecture documentation, no calibration is done inorder to match hardware performance.
* CalibCPU: considering the absence of certain features in gem5, for example, gem5 doesn't support micro-op fusion and micro-op cache, this configuration offsets those difficiencies by improving some other parameters.
* MaxCPU: models a CPU with maximum pipeline widths, minimum pipeline and instruction latencies.

**Note**: By default O3 CPU in gem5 is configured to a max pipeline width of 8, modify `maxwidth` parameter in `src/cpu/o3/impl.h` to simulate wider pipleine.

## Front and back end of the CPU

|     Parameters     |        UnCalib        |        Calib          |         MAX           |      Hardware       |
|--------------------|-----------------------|-----------------------|-----------------------|---------------------|
| Pipeline width     | width=4, Depth=13     | width=7, Depth=13     | width=32, Depth=7     | width=4, depth= ?   |
| IntAlu             | count=4, latency=1    | count=7, latency=1    | count=32, latency=1   | count=4, latency=1  |
| IntMult            | count=1, latency=4    | count=1, latency=2    | count=32, latency=1   | count=1, latency=4  |
| FPALU              | count=1, latency=4    | count=1, latency=2    | count=32, latency=1   |         ?           |
| SIMD_unit          | count=2, latency=same | count=2, latency=same | count=32, latency=1   |       Vector        |
| SIMD_Mult          | count=2, latency=5    | count=2, latency=4    | count=32, latency=1   |       Vector        |

## Memory sub-system

|     Parameters         |        gem5-skylake-config        |      Hardware        |
|------------------------|-----------------------------------|----------------------|
| L1-I cache size, assoc | size=32KiB, way=8                 | size=32KiB, way=8    |
| L1-I cache latency     | tag=1, data=1, response=1         | ?                    |
| L1-I cache prefetcher  | None                              | ?                    |
| L1-D cache size, assoc | size=32KiB, way=8                 | size=32KiB, way=8    |
| L1-D cache latency     | tag=1, data=1, response=1         | 4                    |
| L1-D cache prefetcher  | StridePrefetcher                  | ?                    |
| L2 cache size, assoc   | size=1MiB, way=16, mostly incl    | size=1MiB, way=16    |
| L2 cache latency       | tag=12, data=12, response=6       | 12                   |
| L2 cache MSHRS         | 32, tgts_per_mshr = 1             | ?                    |
| L2 cache write buffers | 32                                | ?                    |
| L2 cache prefetcher    | StridePrefetcher                  | ?                    |
| L3 cache size, assoc   | size=19.5MiB, way=8, mostly excl | size=19.5MiB, way=11 |
| L3 cache latency       | tag=44, data=44, response=21      | 44                   |
| L3 cache MSHRS         | 32, tgts_per_mshr = 2             | ?                    |
| L3 cache write buffers | 64                                | ?                    |
| L3 cache prefetcher    | StridePrefetcher                  | ?                    |
| DRAM                   | DDR4_2400_16x4                    | ?                    |

## Missing Features in gem5

There are few features that are not modeled in gem5. Therefore, some offsetting has to done in order match the hardware performance.

**Micro-op cache**: It holds the predecoded instructions, feeds them directly to the allocation queue (IDQ) and provides a fast access to micro-ops with 1 cycle latency. Since this feature is absent in gem5, the L1 instruction cache latency of skylake config in gem5 is configured to match micro-op cache latency, instead of 4 cycle latency which is the actual hardware latency.

**Micro-op and Macro-op fusion**: The hardware in certain cases fuses few simple micro-ops into one complex micro-op to performance, this feature is absent in gem5. In order to match the performance, the pipeline widths are scaled from 4 to 7, below figure, which is plot of IPC for execution core shows, the effect of this scaling of pipeline widths Calib CPU with respect to hardware and uncalibrated configuration.

**SIMD Vs Vector**: This [manual](https://www.agner.org/optimize/microarchitecture.pdf) provides information about vector intruction latencies, which when directly configured with the SIMD instructions in gem5, the performance doesn't match the hardware, in the figure, we can see how badly the UnCalib CPU compares to hardware for EM1 and EM5. These benchmarks test SIMD multiplier unit in CPU, EM1 has just one multiplication in a loop and EM5 has 5 dependent multiplications in same loop. By adjusted SIMD multiplication latency, we can see Calib CPU closely matches hardware IPC. Adding to this, I currently do not have correct understanding of relationship between producer-consumer micro-op flow in gem5, which might also have an impact on the result.

**Instruction categorization**: In gem5, for example, the shift operations and few other slow int operations are grouped under one enum IntAlu. But, we need to have different number of these units to order match the hardware configuration. A study is yet to made on real workloads to see the frequency of these instructions. A possible solution is to create seperate enum class for slowInt and other instruction classes in gem5.

![Execution-core microbenchmark IPC](../images/exe_IPC.png)

## References

1. [Agner Fog, Microarchitecture of Intel and CPUs](https://www.agner.org/optimize/microarchitecture.pdf)
2. [Agner Fog, Instruction tables](https://www.agner.org/optimize/instruction_tables.pdf)
3. [Wikichip, Skylake Microarchitecture(server)](https://en.wikichip.org/wiki/intel/microarchitectures/skylake_(server))
4. [Intel Architecture Reference Manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-optimization-manual.pdf)
