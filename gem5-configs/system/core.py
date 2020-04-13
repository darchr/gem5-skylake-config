import m5
from m5.objects import *

class IntALU(FUDesc):
    opList = [ OpDesc(opClass='IntAlu', opLat=1),
               OpDesc(opClass='MemRead', opLat=1),
               OpDesc(opClass='MemWrite', opLat=1) ]
    count = 4

class IntMult(FUDesc):
    opList = [ OpDesc(opClass='IntMult', opLat=4) ]
    count = 1

class FP_ALU(FUDesc):
    opList = [ OpDesc(opClass='FloatAdd', opLat=3),
               OpDesc(opClass='FloatCmp', opLat=3),
               OpDesc(opClass='FloatCvt', opLat=3) ]
    count = 3

class FP_Mult(FUDesc):
    opList = [ OpDesc(opClass='FloatMult', opLat=5),
               OpDesc(opClass='FloatMultAcc', opLat=5),
               OpDesc(opClass='FloatMisc', opLat=3) ]
    count = 3

class DivUnit(FUDesc):
    # DIV and IDIV instructions in x86 are implemented using a loop which
    # issues division microops.  The latency of these microops should really be
    # one (or a small number) cycle each since each of these computes one bit
    # of the quotient.
    opList = [ OpDesc(opClass='IntDiv', opLat=1, pipelined=False),
                # OpDesc(opClass='FloatDiv', opLat=15, pipelined=False),
                # OpDesc(opClass='FloatSqrt', opLat=15, pipelined=False),
                OpDesc(opClass='SimdFloatDiv', opLat=15, pipelined=False),
                OpDesc(opClass='SimdFloatSqrt', opLat=10, pipelined=False) ]
    count = 1

class SIMD_Unit(FUDesc):
    opList = [ OpDesc(opClass='SimdAdd', opLat=1),
               OpDesc(opClass='SimdAddAcc', opLat=1),
               OpDesc(opClass='SimdAlu', opLat=1),
               OpDesc(opClass='SimdCmp', opLat=1),
               OpDesc(opClass='SimdCvt', opLat=3),
               OpDesc(opClass='SimdMult', opLat=5),
               OpDesc(opClass='SimdMultAcc', opLat=5),
               OpDesc(opClass='SimdShift', opLat=2),
               OpDesc(opClass='SimdShiftAcc', opLat=2),
               OpDesc(opClass='SimdSqrt', opLat=4),
               OpDesc(opClass='SimdFloatAdd', opLat=4),
               OpDesc(opClass='SimdFloatAlu', opLat=4),
               OpDesc(opClass='SimdFloatCmp', opLat=4),
               OpDesc(opClass='SimdFloatCvt', opLat=4),
                ]
    count = 2

class SIMD_MUL(FUDesc):
    opList = [ OpDesc(opClass='SimdFloatMult', opLat=5),
               OpDesc(opClass='SimdFloatMultAcc', opLat=5) ]
    count = 2

class SIMD_Misc(FUDesc):
    opList = [ OpDesc(opClass='SimdMisc', opLat=3),
               OpDesc(opClass='SimdFloatMisc', opLat=3), ]
    count = 1

class FPMem(FUDesc):
    opList = [ OpDesc(opClass='FloatMemRead', opLat=1),
               OpDesc(opClass='FloatMemWrite', opLat=1) ]
    count = 2

# class IprPort(FUDesc):
#     opList = [ OpDesc(opClass='IprAccess', opLat = 3, pipelined = False) ]
#     count = 1

class Ideal_FUPool(FUPool):
    FUList = [ IntALU(), IntMult(), DivUnit(), SIMD_Unit(), SIMD_MUL(), SIMD_Misc(), FPMem() ]


class UnCalibCPU(DerivO3CPU):
    """ Unoptimized configuration of skylake micro-architecture
        not calibrated against the hardware """
    ######################################
    # Front End
    ######################################
    branchPred = LTAGE()

    # Pipeline widths
    fetchWidth = 4
    decodeWidth = 4

    # Pipeline delays
    fetchToDecodeDelay = 2
    decodeToRenameDelay = 3

    fetchBufferSize = 16
    fetchQueueSize = 64
    numIQEntries = 64

    ######################################
    # Back End
    ######################################

    fuPool = Ideal_FUPool()

    # Pipeline widths
    renameWidth = 4
    dispatchWidth = 4
    issueWidth = 4
    wbWidth = 4
    commitWidth = 4
    squashWidth = 4

    # Pipeline delays
    renameToIEWDelay = 4
    issueToExecuteDelay  = 1
    iewToRenameDelay = 1
    iewToCommitDelay = 4
    commitToFetchDelay = 1
    commitToIEWDelay = 1
    commitToRenameDelay = 1

    LQEntries = 72
    SQEntries = 56
    numPhysIntRegs = 180
    numPhysFloatRegs = 168 # Need to change this
    numROBEntries = 224


class CalibCPU(DerivO3CPU):
    """ Optimized configuration of skylake micro-architecture 
        calibrated against the hardware"""
    ######################################
    # Front End
    ######################################
    branchPred = LTAGE()
    # Pipeline widths
    fetchWidth = 7
    decodeWidth = 7

    # Pipeline delays
    # fetchToDecodeDelay = 1
    # decodeToRenameDelay = 1

    fetchBufferSize = 16
    fetchQueueSize = 64
    numIQEntries = 64

    ######################################
    # Back End
    ######################################

    fuPool = Ideal_FUPool()
    fuPool.FUList[0].count = 7
    fuPool.FUList[0].count = 4
    fuPool.FUList[1].opList[0].opLat = 2
    fuPool.FUList[4].opList[0].opLat = 4
    # fuPool.FUList.append(FP_ALU())
    # Pipeline widths
    renameWidth = 7
    dispatchWidth = 7
    issueWidth = 7
    wbWidth = 7
    commitWidth = 7
    squashWidth = 7

    # Pipeline delays
    # renameToIEWDelay = 1
    # issueToExecuteDelay  = 1
    # iewToRenameDelay = 1
    # iewToCommitDelay = 1
    # commitToFetchDelay = 1
    # commitToIEWDelay = 1
    # commitToRenameDelay = 1

    LQEntries = 72
    SQEntries = 56
    numPhysIntRegs = 180
    numPhysFloatRegs = 168 # Need to change this
    numROBEntries = 224

class MaxCPU(DerivO3CPU):
    """ Configuration with maximum pipeline widths and mininum delays """
    ######################################
    # Front End
    ######################################
    branchPred = LTAGE()

    # Pipeline widths
    fetchWidth = 32
    decodeWidth = 32

    # Pipeline delays
    fetchToDecodeDelay = 1
    decodeToRenameDelay = 1

    # fetchBufferSize = 16
    fetchQueueSize = 256
    numIQEntries = 128

    ######################################
    # Back End
    ######################################

    fuPool = Ideal_FUPool()
    fuPool.FUList[0].count = 32
    fuPool.FUList[1].count = 32
    fuPool.FUList[2].count = 32
    fuPool.FUList[3].count = 32
    fuPool.FUList[4].count = 32
    # fuPool.FUList[5].count = 32
    # fuPool.FUList[6].count = 32

    # Pipeline widths
    renameWidth = 32
    dispatchWidth = 32
    issueWidth = 32
    wbWidth = 32
    commitWidth = 32
    squashWidth = 32

    # Pipeline delays
    renameToIEWDelay = 1
    issueToExecuteDelay  = 1
    iewToRenameDelay = 1
    iewToCommitDelay = 1
    commitToFetchDelay = 1
    commitToIEWDelay = 1
    commitToRenameDelay = 1

    LQEntries = 128
    SQEntries = 128
    numPhysIntRegs = 256
    numPhysFloatRegs = 256 # Need to change this
    numROBEntries = 2096
    
