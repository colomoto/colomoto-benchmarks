#!/usr/bin/env python3

from __future__ import print_function

import subprocess
import sys
import os


def benchmark_tool_feature(tool, feat, models, outfolder):
    launcher = os.path.join('tools', tool, 'features', feat)
    if not os.path.exists( launcher): return
    if not os.path.exists(outfolder): os.makedirs(outfolder)
    
    print("==" * 32)
    print('# {:^60} #'.format('%s:%s' % (tool,feat)))
    print("==" * 32)
    
    for model in models:
        # TODO: skip multivalued models for Boolean tools
        if False: continue
        
        model_name = '__'.join(model.split('/'))
        with open( os.path.join(outfolder, '%s.output' % model_name), 'w' ) as outfile:
            print('*', model)
            subprocess.run( (launcher,model), stdout=outfile )
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


