#!/usr/bin/env python3

#This is a job launch script to run microbenchmark experiments.

import os
import sys
import argparse
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance

experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'gem5_skylake_config',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to test gem5 with micro-benchmarks'
)

gem5_repo = Artifact.registerArtifact(
    command = '''git clone https://gem5.googlesource.com/public/gem5;
                 cd gem5;
                 git cherry-pick 27dbffdb006c7bd12ad2489a2d346274fe646720;
                 git cherry-pick ad65be829e7c6ffeaa143d292a7c4a5ba27c5c7c;
                 wget https://github.com/darchr/gem5/commit/f0a358ee08aba1563c7b5277866095b4cbb7c36d.patch;
                 git am f0a358ee08aba1563c7b5277866095b4cbb7c36d.patch --reject;
    ''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'git repo with gem5 master branch, gem5 version - 19, cherry picks with BTB, branch direction patches and vector mem support'
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86/gem5.opt',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'default gem5 binary for x86'
)

run_scripts = Artifact.registerArtifact(
    command = '',
    typ = 'git repo',
    name = 'gem5-configs',
    path =  'gem5-configs',
    cwd = './',
    documentation = 'gem5 run scripts configured for skylake micro-architecture and micro-benchmarks benchmarks'
)

if __name__ == "__main__":

    # All in benchmarks from VRG micro-benchmark suite
    all_bms = ['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
                     'CS1','CS3','DP1d','DP1f','DPcvt','DPT','DPTd','ED1','EF','EI','EM1','EM5',
                     'MD','MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst',
                     'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']

    ctrl_bms = ['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm','CS1','CS3']
    exe_bms = ['DP1d','DP1f','DPcvt','DPT','DPTd','ED1','EF','EI','EM1','EM5']
    mem_bms = ['MD','MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst',
              'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']

    configs = ['UnCalib', 'Calib', 'Max']
    parser = argparse.ArgumentParser()
    parser.add_argument('config', choices = ['UnCalib','Calib','Max','all'], type=str, help="Available configs")
    parser.add_argument('bench', choices = ['ctrl','exe','mem','all'], type=str, help="Benchmark categories")
    args  = parser.parse_args()

    if (args.config == 'all'):
        configs = ['UnCalib', 'Calib', 'Max']
    else:
        configs = [args.config]

    if (args.bench == 'ctrl'): bms = ctrl_bms
    elif (args.bench == 'exe'): bms = exe_bms
    elif (args.bench == 'mem'): bms = mem_bms
    elif (args.bench == 'all'): bms = all_bms
    else: bms = []

    path = 'microbench'

    # Register the each benchmark used for test as an artifact
    for bm in bms:
        bm = Artifact.registerArtifact(
        command = '''
        cd microbench/{};
        make X86;
        '''.format(bm),
        typ = 'binary',
        name = bm,
        cwd = 'microbench/{}'.format(bm),
        path =  'microbench/{}/bench.X86'.format(bm),
        inputs = [experiments_repo,],
        documentation = 'microbenchmark ({}) binary for X86  ISA'.format(bm)
        )

    for config in configs:
        for bm in bms:
            run = gem5Run.createSERun(f'gem5_validation_skylake_{config}_{bm}',
                'gem5/build/X86/gem5.opt',
                'gem5-configs/run.py',
                f'results/microbenchmark-experiments/{config}/{bm}',
                gem5_binary, gem5_repo, experiments_repo,
                config, os.path.join(path,bm,'bench.X86'))
            run.run()


