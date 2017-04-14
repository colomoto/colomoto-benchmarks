

import os
import matplotlib
import matplotlib.pyplot

import benchmark

benchmark.load_tools()

def compute_ticks(Run):
    """
    computes the ticks for the x-axis of a plot.
    reads all the results files ("timings.txt") of a run, computes network size of each model.
    
    returns:
        tick_names   (list) models sorted from easy to hard)
        
    assumed folder structure:
    
    runs/:stablestates/                             (":stablestates" is a Run)
    runs/:stablestates/PyBoolNet_stablestates/      ("PyBoolNet_stablestates" is a job)
    runs/:stablestates/PyBoolNet_stablestates/      (contains results for each model tested)
        models__arellano_rootstem.bnet.output        (middle part is model name)
        models__dahlhaus_neuroplastoma-bnet.output   
        ...
    """

    try:
        import PyBoolNet

        sizes = set([])
        for job in os.listdir(Run):
            for name in os.listdir(os.path.join(Run,job)):
                if "~" in name: continue
                if name=="timings.txt": continue

                name = name[8:-7]
                assert(name.count(".")==1)
                name = name.split(".")[0]
                name_bnet = name+".bnet"
                
                try:
                    n = len(PyBoolNet.FileExchange.bnet2primes(os.path.join("models",name_bnet)))
                    sizes.add((name,n))
                    
                except Exception:
                    print('add code here to open "%s"'%name)
           
    except ImportError:
        print("add code here to determine network size without PyBoolNet")

    tick_names = [x[0] for x in sorted(sizes, key=lambda y:y[1])]

    return tick_names


    
def read_data(PathToJob, Ordering):
    """
    reads the results file ("timings.txt") of a particular job
    """

    path_to_timings = os.path.join(PathToJob,"timings.txt")

    if not os.path.exists(path_to_timings):
        return None
    
    with open(path_to_timings, "r") as f:
        data = f.readlines()

    data = [x.split() for x in data]
    data = [(x[0][8:],float(x[1])) for x in data]
    data = [(x.split(".")[0], y) for x,y in data]
    data = dict(data)

    return [data[x] if x in data else None for x in Ordering]




if __name__=="__main__":
    """
    - creates a plot for each run in the folder ./runs/
    - saves the result in ./plots/
    """

    
    
    for run in os.listdir("runs"):
        print('found run "%s"'%run)

        tick_names = compute_ticks("runs/%s"%run)
        tick_numbers = range(len(tick_names))

        figure = matplotlib.pyplot.figure()
        matplotlib.pyplot.title('Benchmark "%s"'%run)
        matplotlib.pyplot.ylabel('time (sec)')
        matplotlib.pyplot.xlabel('models')
        
        matplotlib.pyplot.grid(True,color="k")

        matplotlib.pyplot.xticks(tick_numbers, tick_names, rotation=90)
        
        for job in os.listdir(os.path.join("runs",run)):
            tool, feature = job.split("_")

            data = read_data(os.path.join("runs",run,job), tick_names)

            if data:
                matplotlib.pyplot.plot(tick_numbers, data, label=(tool,feature), marker='o', linewidth=3)
            else:
                print('  missing "timings.txt" for %s %s'%(tool,feature))

            print('  found tool "%s"'%tool)

        matplotlib.pyplot.legend(loc=9, bbox_to_anchor=(0.5, -0.6), ncol=2)
        matplotlib.pyplot.tight_layout()

        fname = os.path.join("plots",run+".pdf")
        figure.savefig(fname)
        print('  created plot "%s"'%fname)


