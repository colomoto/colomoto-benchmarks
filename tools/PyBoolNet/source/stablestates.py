
import sys
import PyBoolNet

if __name__ == '__main__':
    bnet = sys.argv[1]
    primes = PyBoolNet.FileExchange.bnet2primes(bnet)
    steadystates = PyBoolNet.TrapSpaces.steady_states(primes)
    steadystates = [PyBoolNet.StateTransitionGraphs.state2str(x) for x in steadystates]
    print(','.join(steadystates))
