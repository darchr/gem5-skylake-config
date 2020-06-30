# Control Benchmarks 

The suite of control conditional benchmarks which is a part of the [University of Wisconsin micro-benchmarks suite](https://github.com/VerticalResearchGroup/microbench) can be used to try and understand the difference in performance between the Intel Skylake processor and the branch prediction unit in gem5.

Control Conditional Benchmarks:

- CCa : completely baised branches

- CCe : easy to predict -- branch pattern (i.e., 10101010...)

- CCm : heavly baised branches

- CCh_st : impossible to predict with a store operation


**Understanding the role of Branch Miss-Predictions**

To understand the role of branch predictors, we plot the conditional branch misprediction rate while using LTAGE branch predictor (which from our [analysis of control benchmarks](https://github.com/darchr/gem5art-experiments/blob/master/documents/sim-objects/branch-predictors.md) we know, is the most accurate branch predictor included in gem5)

The misprediction rate for both UnCalibrated and Calibrated CPU is almost the same as the mispredsiction rate obtained from running the benchmarks natively on Intel Skylake Processor using Intel PCM tool.

Then increasing the iteration to '500K', the misprediction rate reduces for gem5 while using LTAGE because LTAGE has a larger history table.
This large history table takes time to warm up and, thus, we see increased prediction rates as we increase the number of iterations.

<img src="../images/Branchpred_misprediction_100K.png" width="500" height="500">

<img src="../images/Branchpred_misprediction_500K.png" width="500" height="500">

## Conclusion:

<img src="../images/Branchpred_ipc_100K.png" width="500" height="500">

As shown above, the IPC for gem5 configured to model Skylake architecture with LTAGE branch predictor for '100K' iterations of the control microbenchmarks benchmarks is almost the same as the performance of the Intel processor measured using Intel PCM for 'Calib CPU'.

The various other different branch predictor parameters like history length should be studied to better understand the branch predictors in depth with respect to hardware systems.
