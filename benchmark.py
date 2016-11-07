#!/usr/bin/env python3

from __future__ import print_function

import subprocess
import resource
import sys
import os

TIMEOUT=2000

def subprocess_run(commands, outfile, timeout):
    # hannes doesn't have python 3.5 hence can't use subprocess.run :)
    
    process = subprocess.Popen(commands, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #process.stdin.close()
    output, error = process.communicate(timeout=timeout)
    output = output.decode()
    outfile.write(output)


def accepts_multivalues(tool):
    with open(os.path.join('tools', tool, 'config.txt')) as f:
        for line in f.readlines():
            key, value = line.split(':')
            value = value.strip()
            key = key.strip()
            if key=='multivalued':
                assert(value in ['true','false'])
                return value=='true'

    print('config.txt of %s doesnt contain "multivalued"')
    raise Exception


def is_multivalued(model):
    return '.sbml' in model
    

def benchmark_tool_feature(tool, feat, models, outfolder):
    launcher = os.path.join('tools', tool, 'features', feat)
    if not os.path.exists( launcher): return
    if not os.path.exists(outfolder): os.makedirs(outfolder)
    
    print("==" * 32)
    print('# {:^60} #'.format('%s:%s' % (tool,feat)))
    print("==" * 32)

    tool_accepts_multi = accepts_multivalues(tool)
    
    with open( os.path.join(outfolder, 'timings.txt'), 'w' ) as timingfile:
        for model in models:
            
            if is_multivalued(model) and not tool_accepts_multi: continue
            
            model_name = '__'.join(model.split('/'))
            with open( os.path.join(outfolder, '%s.output' % model_name), 'w' ) as outfile:
                print('*', model)
                usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
                subprocess_run(commands=(launcher,model), outfile=outfile, timeout=TIMEOUT)
                usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
                cpu_time = usage_end.ru_utime - usage_start.ru_utime
                timingfile.write('%s\t%s\n' % (model_name,cpu_time))
                
                # TODO: should we detect timeout triggers and error codes?
                # TODO: check results for relevant features
    
    print()


def load_models(folder='models'):
    models = []
    for model in os.listdir(folder):
        models.append( os.path.join( folder, model) )
    return models


def run_benchmarks(selected, models, runfolder):
    #TODO: obtain a new run output folder
    this_runfolder = os.path.join(runfolder, 'test')
    if not os.path.exists(this_runfolder): os.makedirs(this_runfolder)
    
    done = set()
    for target in selected:
        if target in done:
            print('skip %s:%s' % target)
            continue
        
        tool,feat = target
        outfolder = os.path.join(this_runfolder, '_'.join(target))
        benchmark_tool_feature(tool,feat,models, outfolder)
        done.add(target)


def add_tool_feature(selected, tool, feat):
    launcher = os.path.join('tools', tool, 'features', feat)
    if not os.path.exists( launcher): return
    selected.append((tool,feat))

def add_tool(selected, tool):
    feature_folder = os.path.join('tools', tool, 'features')
    if not os.path.exists( feature_folder): return

    for feat in os.listdir( os.path.join('tools', tool, 'features')):
        if '~' in feat: continue
        add_tool_feature(selected, tool, feat)


def add_feature(selected, feat):
    for tool in os.listdir("tools"):
        add_tool_feature(selected, tool, feat)


def add_all(selected):
    for tool in os.listdir("tools"):
        add_tool(selected, tool)



if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        print('Usage: %s [list of targets]')
        print('  ALL            benchmark everything')
        print('  tool           all features of a specific tool')
        print('  tool:feature   a specific features of a tool')
        print('  :feature       all instances of a specific feature')
    
    selected_features = []
    for arg in args:
        if arg == 'ALL':
            add_all(selected_features)
            continue
        
        target = arg.split(':', 1)
        if len(target) == 1:
            tool = arg
            feat = None
        else:
            tool,feat = target
        
        if tool:
            if feat:
                add_tool_feature(selected_features, tool, feat)
            else:
                add_tool(selected_features, tool)
        elif feat:
            add_feature(selected_features, feat)

    models = load_models()
    runfolder = 'runs'
    
    run_benchmarks(selected_features, models, runfolder)

    


