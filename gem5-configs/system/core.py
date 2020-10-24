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
import math

class IntALU(FUDesc):
    opList = [ OpDesc(opClass='IntAlu', opLat=1) ]
    count = 4

class IntMultDiv(FUDesc):
    opList = [ OpDesc(opClass='IntMult', opLat=3, pipelined=True),
               OpDesc(opClass='IntDiv', opLat=20, pipelined=True) ]

    # DIV and IDIV instructions in x86 are implemented using a loop which
    # issues division microops.  The latency of these microops should really be
    # one (or a small number) cycle each since each of these computes one bit
    # of the quotient.
    if buildEnv['TARGET_ISA'] in ('x86'):
        opList[1].opLat=1

    count=1

class FP_ALU(FUDesc):
    opList = [ OpDesc(opClass='FloatAdd', opLat=4, pipelined=True),
               OpDesc(opClass='FloatCmp', opLat=4, pipelined=True),
               OpDesc(opClass='FloatCvt', opLat=4, pipelined=True) ]
    count = 0

class FP_MultDiv(FUDesc):
    opList = [ OpDesc(opClass='FloatMult', opLat=4, pipelined=True),
               OpDesc(opClass='FloatMultAcc', opLat=5, pipelined=True),
               OpDesc(opClass='FloatMisc', opLat=3, pipelined=True),
               OpDesc(opClass='FloatDiv', opLat=12, pipelined=True),
               OpDesc(opClass='FloatSqrt', opLat=24, pipelined=True) ]
    count = 0

class SIMD_Int_Unit(FUDesc):
    opList = [ OpDesc(opClass='SimdAdd', opLat=1),
               OpDesc(opClass='SimdAddAcc', opLat=1),
               OpDesc(opClass='SimdAlu', opLat=1),
               OpDesc(opClass='SimdCmp', opLat=1),
               OpDesc(opClass='SimdShift', opLat=1),
               OpDesc(opClass='SimdShiftAcc', opLat=1),
               OpDesc(opClass='SimdReduceAdd', opLat=1),
               OpDesc(opClass='SimdReduceAlu', opLat=1),
               OpDesc(opClass='SimdReduceCmp', opLat=1),
               OpDesc(opClass='SimdCvt', opLat=3, pipelined=True),
               OpDesc(opClass='SimdMult', opLat=5, pipelined=True),
               OpDesc(opClass='SimdMultAcc', opLat=5, pipelined=True),
               OpDesc(opClass='SimdDiv',  opLat=12, pipelined=True),
               OpDesc(opClass='SimdSqrt', opLat=20, pipelined=True),
               OpDesc(opClass='SimdMisc', opLat=3, pipelined=True) ]
    count = 4

class SIMD_FP_Unit(FUDesc):
    opList = [ OpDesc(opClass='SimdFloatAdd', opLat=4, pipelined=True),
               OpDesc(opClass='SimdFloatAlu', opLat=4, pipelined=True),
               OpDesc(opClass='SimdFloatCmp', opLat=4, pipelined=True),
               OpDesc(opClass='SimdFloatReduceAdd', opLat=4, pipelined=True),
               OpDesc(opClass='SimdFloatReduceCmp', opLat=4, pipelined=True),
               OpDesc(opClass='SimdFloatCvt', opLat=5, pipelined=True),
               OpDesc(opClass='SimdFloatMult', opLat=5, pipelined=True),
               OpDesc(opClass='SimdFloatMultAcc', opLat=5, pipelined=True),
               OpDesc(opClass='SimdFloatDiv', opLat=12, pipelined=True),
               OpDesc(opClass='SimdFloatSqrt', opLat=20, pipelined=True),
               OpDesc(opClass='SimdFloatMisc', opLat=4, pipelined=True) ]
    count = 4

class PredALU(FUDesc):
    opList = [ OpDesc(opClass='SimdPredAlu') ]
    count = 1

class RdPort(FUDesc):
    opList = [ OpDesc(opClass='MemRead', opLat=1, pipelined=True),
               OpDesc(opClass='FloatMemRead', opLat=1, pipelined=True) ]
    count = 2

class WrPort(FUDesc):
    opList = [ OpDesc(opClass='MemWrite', opLat=1, pipelined=True),
               OpDesc(opClass='FloatMemWrite', opLat=1, pipelined=True) ]
    count = 1

class IprPort(FUDesc):
    opList = [ OpDesc(opClass='IprAccess', opLat = 1, pipelined = False) ]
    count = 1

class Ideal_FUPool(FUPool):
    FUList = [ IntALU(), IntMultDiv(), SIMD_Int_Unit(), SIMD_FP_Unit(), PredALU(), RdPort(), WrPort(), IprPort(), FP_ALU(), FP_MultDiv() ]

class IndirectPred(SimpleIndirectPredictor):
    indirectSets = 256 # Cache sets for indirect predictor
    indirectWays = 2 # Ways for indirect predictor
    indirectTagSize = 16 # Indirect target cache tag bits
    indirectPathLength = 3 # Previous indirect targets to use for path history
    indirectGHRBits = 13 # Indirect GHR number of bits

depth = 3
width = 4
class VerbatimCPU(DerivO3CPU):
    """ VerbatimCPU: Configured based on micro-architecture documentation, 
                     not tuned to match hardware performance. """
    branchPred = TournamentBP()
    branchPred.BTBEntries = 512
    branchPred.BTBTagSize = 19
    branchPred.RASSize = 16
    branchPred.localPredictorSize = 512
    branchPred.localCtrBits = 2
    branchPred.localHistoryTableSize = 1024
    branchPred.globalPredictorSize = 1024
    branchPred.globalCtrBits = 2
    branchPred.choicePredictorSize = 1024
    branchPred.choiceCtrBits = 2

    # Pipeline delays
    # https://gem5-users.gem5.narkive.com/LNMJQ1M5/model-deeper-pipeline-in-x86#post2
    # to model 15 stage pipeline choose depth parameter as 3
    fetchToDecodeDelay = depth
    decodeToRenameDelay = depth
    renameToIEWDelay = 2*depth
    iewToCommitDelay = depth

    # Forwarding paths
    # commitToFetchDelay = depth
    # commitToDecodeDelay = depth
    # commitToRenameDelay = depth
    # commitToIEWDelay = depth
    # decodeToFetchDelay = depth
    # iewToFetchDelay = depth
    # iewToDecodeDelay = depth
    # iewToRenameDelay = depth
    # issueToExecuteDelay = depth
    # iewToRenameDelay = depth
    # renameToFetchDelay = depth
    # renameToDecodeDelay = depth
    # renameToROBDelay = depth

    forwardComSize = 5 * depth
    backComSize = 5 * depth

    fuPool = Ideal_FUPool()

    # Pipeline widths
    fetchWidth = width
    decodeWidth = width
    renameWidth = width
    dispatchWidth = width
    issueWidth = width
    wbWidth = width
    commitWidth = width
    squashWidth = width

    fetchBufferSize = 16
    fetchQueueSize = 50
    numROBEntries = 224
    numIQEntries = 97
    LQEntries = 72
    SQEntries = 56
    numPhysIntRegs = 180
    numPhysFloatRegs = 168

depth = 3
width = 6
a_width = width + 2
class TunedCPU(DerivO3CPU):
    """ TunedCPU: Configured based on micro-architecture documentation, 
                  tuned to match hardware performance. """
    branchPred = TournamentBP()
    branchPred.BTBEntries = 512
    branchPred.BTBTagSize = 19
    branchPred.RASSize = 16
    branchPred.localPredictorSize = 512
    branchPred.localCtrBits = 2
    branchPred.localHistoryTableSize = 1024
    branchPred.globalPredictorSize = 1024
    branchPred.globalCtrBits = 2
    branchPred.choicePredictorSize = 1024
    branchPred.choiceCtrBits = 2

    branchPred.indirectBranchPred = IndirectPred() # use NULL to disable

    # Pipeline delays
    # https://gem5-users.gem5.narkive.com/LNMJQ1M5/model-deeper-pipeline-in-x86#post2
    # to model 15 stage pipeline choose depth parameter as 3
    fetchToDecodeDelay = depth
    decodeToRenameDelay = depth
    renameToIEWDelay = 2*depth
    iewToCommitDelay = depth

    forwardComSize = 5* depth
    backComSize = 5* depth

    # Pipeline widths
    fetchWidth = width
    decodeWidth = width
    renameWidth = 12
    issueWidth = a_width
    dispatchWidth = a_width
    wbWidth = a_width
    commitWidth = width
    squashWidth = a_width

    fuPool = Ideal_FUPool()
    fuPool.FUList[1].opList[0].opLat = 2
    fuPool.FUList[1].opList[1].opLat = 2

    fuPool.FUList[3].opList[5].opLat = 4
    fuPool.FUList[3].opList[6].opLat = 4
    fuPool.FUList[3].opList[5].opLat = 4

    fuPool.FUList[5].count = 3
    fuPool.FUList[6].count = 2

    fetchBufferSize = 16
    fetchQueueSize = 50
    numROBEntries = 224 * (a_width/4)
    numIQEntries = 97 * (a_width/4)
    LQEntries = 72
    SQEntries = 56
    numPhysIntRegs = 180
    numPhysFloatRegs = 168

depth = 3
width = 32
class UnConstrainedCPU(DerivO3CPU):
    """ UnConstrainedCPU: Configured for max performance
                          32 wide pipeline
                          3X to 4X more back-end resources than TunedCPU
                          Minimum instruction latency. """
    branchPred = TournamentBP()
    # use NULL to enable BTB
    # branchPred.indirectBranchPred = NULL

    # Pipeline delays
    # https://gem5-users.gem5.narkive.com/LNMJQ1M5/model-deeper-pipeline-in-x86#post2
    # to model 15 stage pipeline choose depth parameter as 3
    fetchToDecodeDelay = depth
    decodeToRenameDelay = depth
    renameToIEWDelay = 2*depth
    iewToCommitDelay = depth

    forwardComSize = 5* depth
    backComSize = 5* depth

    fuPool = Ideal_FUPool()

    # Pipeline widths
    fetchWidth = width
    decodeWidth = width
    renameWidth = width
    dispatchWidth = width
    issueWidth = width
    wbWidth = width
    commitWidth = width
    squashWidth = width

    fuPool = Ideal_FUPool()
    fuPool.FUList[0].count = 16

    fuPool.FUList[1].count = 8
    fuPool.FUList[1].opList[0].opLat = 2
    fuPool.FUList[1].opList[1].opLat = 2

    fuPool.FUList[2].count = 16

    fuPool.FUList[3].count = 16
    fuPool.FUList[3].opList[5].opLat = 4
    fuPool.FUList[3].opList[6].opLat = 4
    fuPool.FUList[3].opList[5].opLat = 4

    fuPool.FUList[4].count = 8

    fuPool.FUList[5].count = 8

    fuPool.FUList[6].count = 8

    fetchBufferSize = 64
    fetchQueueSize = 128
    numROBEntries = 1024
    numIQEntries = 512
    LQEntries = 256
    SQEntries = 224
    numPhysIntRegs = 256
    numPhysFloatRegs = 256 # Need to change this
