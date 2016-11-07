# Benchmarks for Tools of Logical Models

With the aim to facilitate benchmarking of several methods and tools for logical model analysis,
we will assemble a collection of test models, modelling tools and their supported features, as 
well as a script to measure running time for each combination.


# Setup
1. Tools
   - every tool lives in its own folder, e.g. `tools/PyBoolNet/`
   - `tools/PyBoolNet/config.txt` contains infos about the tool, e.g. `multivalued: false`
   - `tools/PyBoolNet/source/` contains Linux source files
   - `tools/PyBoolNet/features/` contains a shell script for every benchmark the tool can handle, e.g. `tools/PyBoolNet/features/steadystates`
   
2. Models
   - all models are kept in `tools/models/`
   - whether a model is boolean or multi-valued is determined by the file extension with `bnet` for boolean models and `sbml` for multi-valued models


   
