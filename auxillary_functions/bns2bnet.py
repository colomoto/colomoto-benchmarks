#!/usr/bin/env python3

import PyBoolNet
import os



if __name__=="__main__":
    print("""
    this script scans the models folder "../models" and creates a "bns" file
    for every "bnet" file it finds. E.g., creates

    ../models/klamt_tcr.bns

    from

    ../models/klamt_tcr.bnet    
    """)

    counter = 0
    for fname in os.listdir("../models"):
        assert(fname.count(".")==1)
        name, ext = fname.split(".")
        if not ext=="bnet": continue
        
        source = os.path.join("../models", fname)
        target = os.path.join("../models", name+".bns")
        if os.path.isfile(target): continue

        primes = PyBoolNet.FileExchange.bnet2primes(source)
        PyBoolNet.FileExchange.primes2bns(primes, target)
        counter+=1

    if counter==0:
        print("nothing to convert.")
    

