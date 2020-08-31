#!/usr/bin/env python3

#This is a job launch script to run microbenchmark experiments.

import os
import sys
import argparse
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance

sys.path.insert(1, '/fasthome/shparekh/gem5-validation-framework/')
from benchmarks import *
import functions as fs

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
    ''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'git repo for gem5'
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86/gem5.opt -j16',
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

    parser = argparse.ArgumentParser()
    parser.add_argument('config', choices = ['UnCalib','Calib','Max','all'], type=str, help="CPU type")
    parser.add_argument('bm', choices = ['ctrl', 'exe', 'mem', 'all', 'CCe'], type=str, help="Benchmark categories")
    parser.add_argument('-w','--write', action="store_true", help="collect gem5 stats")
    args  = parser.parse_args()
    bm_cat = args.bm

    if (args.config == 'all'):
        configs = ['UnCalib', 'Calib', 'Max']
    else:
        configs = [args.config]

    if (bm_cat == 'ctrl'): bms = vrg_ctrl
    elif (bm_cat == 'exe'): bms = vrg_exe
    elif (bm_cat == 'mem'): bms = vrg_mem
    elif (bm_cat == 'all'): bms = vrg_all
    elif (bm_cat == 'CCe'): bms = individual
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
    if (args.write):
        for config in configs:
            fs.getGem5Data(config,f'gcc-gem5-{config}-results.csv')
    else:
        for config in configs:
            for bm in bms:
                run = gem5Run.createSERun('skylake_micro-benchmarks_run_{}_{}'.format(config,bm),
                    'gem5/build/X86/gem5.opt',
                    'gem5-configs/run.py',
                    'stats/microbenchmark-experiments/{}/{}'.format(config,bm),
                    gem5_binary, gem5_repo, experiments_repo,
                    config, os.path.join(path,bm,'bench.X86'))
                run.run()
