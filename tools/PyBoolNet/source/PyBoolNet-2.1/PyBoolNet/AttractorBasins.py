

import os
import sys
import itertools
import math
import random
import operator
import functools
import networkx

BASE = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(BASE)

import PyBoolNet.FileExchange
import PyBoolNet.ModelChecking
import PyBoolNet.QueryPatterns
import PyBoolNet.TrapSpaces
import PyBoolNet.AttractorDetection
import PyBoolNet.StateTransitionGraphs
import PyBoolNet.InteractionGraphs
import PyBoolNet.PrimeImplicants
import PyBoolNet.Utility

config = PyBoolNet.Utility.Misc.myconfigparser.SafeConfigParser()
config.read(os.path.join(BASE, "Dependencies", "settings.cfg"))
CMD_DOT = os.path.join(BASE, "Dependencies", config.get("Executables", "dot"))



def basins_diagram(Primes, Update, Attractors=None, ComputeBorders=False, Silent=True, ReturnCounter=False):
    """
    Creates the basin diagram, a networkx.DiGraph, of the STG defined by *Primes* and *Update*.
    The nodes of the diagram represent states that can reach the exact same subset of *Attractors*.
    Nodes are labeled by the index of the attractor in the order given in *Attractors* and the number of states
    that are represented. Edges indicate the existence of a transition between two states in the respective sets.
    Edges are labeled by the number of states of the source basin that can reach the target basin and,
    if *ComputeBorders* is true, additionally by the size of the border.

    The algorithm requires model checking with accepting states, i.e., NuSMV-a.
    Basic steps towards increased efficiency are implemented:
    out-DAGs (a.k.a. output cascades) are discarded during model checking, and
    disconnected components are considered separately (and recombined using a cartesian product of diagrams).

    **arguments**:
        * *Primes*: prime implicants
        * *Update* (str): the update strategy, one of *"asynchronous"*, *"synchronous"*, *"mixed"*
        * *Attractors* (list): list of states or subspaces representing the attractors. *None* results in the computation of the minimal trap spaces.
        * *ComputeBorders* (bool): whether the computation of the so-called border states should be included in the diagram
        * *Silent* (bool): whether information regarding the execution of the algorithm should be printed
        * *ReturnCounter* (bool): whether the number of performed model checks should be returned

    **returns**::
        * *BasinsDiagram* (netowrkx.DiGraph): the basins diagram
        * *Counter* (int): number of model checks performed, if *ReturnCounter=True*

    **example**::

        >>> primes = REPO.get_primes("xiao_wnt5a")
        >>> diagram = basins_diagram(primes, "asynchronous")
        >>> diagram.order()
        6
        >>> diagram.node[4]["formula"]
        '(x4 & (x7))'
        >>> diagram.node[4]["size"]
        32
    """
    
    assert(Update in ["synchronous", "mixed", "asynchronous"])

    if not Attractors:
        Attractors = PyBoolNet.TrapSpaces.trap_spaces(Primes, "min")
    
    if not Primes:
        print(" error: what are the basins of an empty Boolean network?")
        raise Exception

    igraph = PyBoolNet.InteractionGraphs.primes2igraph(Primes)
    outdags = PyBoolNet.InteractionGraphs.find_outdag(igraph)
    igraph.remove_nodes_from(outdags)
    if not Silent:
        print("basin_diagram(..)")
        print(" excluding the out-dag %s"%outdags)

    components = networkx.connected_components(igraph.to_undirected())
    components = [list(x) for x in components]
    if not Silent:
        print(" working on %i connected component(s)"%len(components))
        
    counter_mc = 0
    diagrams = []
    for component in components:
        subprimes = PyBoolNet.PrimeImplicants.copy(Primes)
        PyBoolNet.PrimeImplicants.remove_all_variables_except(subprimes, component)
        
        attrs_projected = project_attractors(Attractors, component)

        diagram, count = basins_diagram_component(subprimes, Update, attrs_projected, ComputeBorders, Silent)
        counter_mc+=count
        
        diagrams.append(diagram)
        

    factor = 2**len(outdags)
    diagram = cartesian_product(diagrams, factor, ComputeBorders)


    for x in diagram.nodes():
        projection = diagram.node[x]["attractors"]
        diagram.node[x]["attractors"] = lift_attractors(Attractors, projection)
        

    if not Silent:
        print(" total executions of NuSMV: %i"%counter_mc)

    if ReturnCounter:
        return diagram, counter_mc
    else:
        return diagram


def basins_diagram_component(Primes, Update, Attractors, ComputeBorders, Silent):
    """
    Also computes the basin diagram but without removing out-DAGs or considering connected components separately.
    Not meant for general use. Use basins_diagram(..) instead.
    """
    
    assert(Update in ["synchronous", "mixed", "asynchronous"])
    
    if not Primes:
        print("what are the basins of an empty Boolean network?")
        raise Exception

    # create nodes
    counter_mc = 0
    node_id = 0
    worst_case_nodes = 0
    inputs = PyBoolNet.PrimeImplicants.find_inputs(Primes)
    states_per_case = 2**(len(Primes)-len(inputs))
    diagram = networkx.DiGraph()

    if not Silent:
        print(" basins_diagram_component(..)")
        print("  inputs: %i"%len(inputs))
        print("  combinations:  %i"%2**len(inputs))

    for i, combination in enumerate(PyBoolNet.PrimeImplicants.input_combinations(Primes)):
        attr = [x for x in Attractors if PyBoolNet.Utility.Misc.dicts_are_consistent(x,combination)]
        worst_case_nodes+= 2**len(attr)-1
        states_covered = 0
        specs = [PyBoolNet.QueryPatterns.subspace2proposition(Primes,x) for x in attr]
        vectors = len(attr)*[[0,1]]
        vectors = list(itertools.product(*vectors))
        random.shuffle(vectors)

        if not Silent:
            print("  input combination %i, worst case #nodes: %i"%(i,2**len(attr)-1))
        
        for vector in vectors:
            if sum(vector)==0: continue
            if states_covered==states_per_case:
                if not Silent:
                    print("  avoided executions of NuSMV due to state counting")
                break

            combination_formula = PyBoolNet.QueryPatterns.subspace2proposition(Primes,combination)
            if len(vector)==1:
                data = {"attractors":   attr,
                        "size":         2**(len(Primes)-len(inputs)),
                        "formula":      combination_formula}
                
            else:
                init = "INIT %s"%combination_formula
                spec = " & ".join("EF(%s)"%x if flag else "!EF(%s)"%x for flag, x in zip(vector, specs))
                spec = "CTLSPEC %s"%spec

                answer, accepting = PyBoolNet.ModelChecking.check_primes_with_acceptingstates(Primes, Update, init, spec)
                counter_mc+=1
                
                data = {"attractors":   [x for flag,x in zip(vector,attr) if flag],
                        "size":         accepting["INITACCEPTING_SIZE"],
                        "formula":      accepting["INITACCEPTING"]}

            if data["size"]>0:
                diagram.add_node(node_id, data)
                node_id+=1
                states_covered+= data["size"]

    if not Silent:
        perc = "= %.2f%%"%(100.*diagram.order()/worst_case_nodes) if worst_case_nodes else ""
        print("  worst case #nodes: %i"%worst_case_nodes)
        print("  actual nodes: %i %s"%(diagram.order(),perc))

    # list potential targets
    potential_targets = {}
    for source, source_data in diagram.nodes(data=True):
        succs = []
        for target, target_data in diagram.nodes(data=True):
            if source==target: continue
            if all(x in source_data["attractors"] for x in target_data["attractors"]):
                succs.append((target,target_data))
                
        potential_targets[source] = succs

    if not Silent:
        worst_case_edges = sum(len(x) for x in potential_targets.values())
        print("  worst case #edges: %i"%worst_case_edges)
        
    # create edges
    for source, source_data in diagram.nodes(data=True):
        for target, target_data in potential_targets[source]:

            # computation of edges with borders ...
            if ComputeBorders:
                init = "INIT %s"%source_data["formula"]
                spec = "CTLSPEC EX(%s)"%target_data["formula"]
                answer, accepting = PyBoolNet.ModelChecking.check_primes_with_acceptingstates(Primes, Update, init, spec)
                counter_mc+=1
                
                data = {}
                data["border_size"] = accepting["INITACCEPTING_SIZE"]
                data["border_formula"] = accepting["INITACCEPTING"]
                
                if data["border_size"]>0:

                    if len(potential_targets[source])==1:
                        data["finally_size"] = source_data["size"]
                        data["finally_formula"] = source_data["formula"]

                    else:
                        spec = "CTLSPEC EF(%s)"%data["border_formula"]
                        answer, accepting = PyBoolNet.ModelChecking.check_primes_with_acceptingstates(Primes, Update, init, spec)
                        counter_mc+=1
                        
                        data["finally_size"] = accepting["INITACCEPTING_SIZE"]
                        data["finally_formula"] = accepting["INITACCEPTING"]
                    
                    diagram.add_edge(source, target, data)

            # .. is very different from the computation without
            else:
                phi1 = source_data["formula"]
                phi2 = target_data["formula"]
                init = "INIT %s"%phi1
                spec = "CTLSPEC E[%s U %s]"%(phi1,phi2)
                answer, accepting = PyBoolNet.ModelChecking.check_primes_with_acceptingstates(Primes, Update, init, spec)
                counter_mc+=1

                data = {}
                data["finally_size"] = accepting["INITACCEPTING_SIZE"]
                data["finally_formula"] = accepting["INITACCEPTING"]

                if data["finally_size"]>0:
                    diagram.add_edge(source, target, data)
                    
    if not Silent:
        perc = "= %.2f%%"%(100.*diagram.size()/worst_case_edges) if worst_case_edges else ""
        print("  actual edges: %i %s"%(diagram.size(),perc))
        print("  total executions of NuSMV: %i"%counter_mc)

    return diagram, counter_mc


def diagram2image(Primes, Diagram, FnameIMAGE, FnameATTRACTORS=None, StyleInputs=True, StyleFillColor=False,
                  StyleSplines="curved", StyleEdges=False, StyleRefinement=False, StyleRanks=True, FirstIndex=0):
    """
    Creates the image file *FnameIMAGE* for the basin diagram given by *Diagram*.
    Use *FnameATTRACTORS* to create a separate image in which the indices of the diagram are mapped to the given attractors.
    The flag *StyleInputs* can be used to highlight which basins belong to which input combination.
    *StyleEdges* adds edge labels that indicate the size of the "border" (if *ComputeBorder* was enabled in :ref:`basins_diagram`)
    and the size of the states of the source basin that can reach the target basin.
    *StyleRefinement* draws dashed edges and nodes to indicate that not all source basin states can reach a target basin.

    **arguments**:
        * *Primes*: prime implicants, needed for pretty printing of the attractors.
        * *Diagram* (networkx.DiGraph): a basin diagram
        * *FnameIMAGE* (str): name of the diagram image
        * *FnameATTRACTORS* (str): name of the attractor key file, if wanted
        * *StyleInputs* (bool): whether basins should be grouped by input combinations
        * *StyleFillColor* (bool): whether nodes should be given a shade of gray that represents the percentage of state spaces contained in the respective basin
        * *StyleSplines* (str): dot style for edges, e.g. "curved", "line" or "ortho" for orthogonal edges
        * *StyleEdges* (bool): whether edges should be size of border / reachable states
        * *StyleRefinement* (bool): experimental style that modifies edges and nodes according to "homogeneity"
        * *StyleRanks* (bool): style that places nodes with the same number of reachable attractors on the same rank (level)
        * *FirstIndex* (int): first index of attractor names
        
    **returns**::
        * *None*

    **example**::

        >>> diagram2image(primes, diagram, "basins.pdf")
        >>> diagram2image(primes, diagram, "basins.pdf", "attractors.pdf")
    """
    

    size_total = float(2**len(Primes))
    
    result = networkx.DiGraph()
    result.graph["node"]  = {"shape":"rect","style":"filled"}
    result.graph["edge"]  = {}
    
    if StyleFillColor:
        result.graph["node"]["color"] = "none"
    else:
        result.graph["node"]["color"] = "black"

    attractors = [x["attractors"] for _,x in Diagram.nodes(data=True)]
    attractors = [x for x in attractors if len(x)==1]
    attractors = set(PyBoolNet.StateTransitionGraphs.subspace2str(Primes,x[0]) for x in attractors)
    attractors = sorted(attractors)

    label = ["attractors:"]+["A%i = %s"%(i+FirstIndex,A) for i,A in enumerate(attractors)]
    label = "<%s>"%"<br/>".join(label)

    if FnameATTRACTORS:
        key = networkx.DiGraph()
        key.add_node("Attractors",label=label,style="filled",fillcolor="cornflowerblue", shape="rect")
        PyBoolNet.Utility.DiGraphs.digraph2image(key, FnameATTRACTORS, "dot")
        
    else:
        result.add_node("Attractors",label=label,style="filled",fillcolor="cornflowerblue")

    for node, data in Diagram.nodes(data=True):
        attr = sorted("A%i"%(attractors.index(PyBoolNet.StateTransitionGraphs.subspace2str(Primes,x))+FirstIndex) for x in data["attractors"])
        attr = PyBoolNet.Utility.Misc.divide_list_into_similar_length_lists(attr)
        attr = [",".join(x) for x in attr]
        label = attr+["states: %s"%data["size"]]
        label = "<br/>".join(label)
        label = "<%s>"%label

        result.add_node(node, label=label)


        if StyleFillColor:
            if len(data["attractors"])==1:
                result.node[node]["color"] = "cornflowerblue"
                result.node[node]["penwidth"] = "4"

            size_percent = data["size"] / size_total        
            result.node[node]["fillcolor"] = "0.0 0.0 %.2f"%(1-size_percent)
            if size_percent>0.5: result.node[node]["fontcolor"] = "0.0 0.0 0.8"
        else:
            if len(data["attractors"])==1:
                result.node[node]["fillcolor"] = "cornflowerblue"
            else:
                result.node[node]["fillcolor"] = "white"

        if StyleRefinement:
            if all(d["finally_size"]==data["size"] for _,_,d in Diagram.out_edges(node,data=True)):
                result.node[node]["fontcolor"] = "cornflowerblue"
        

    for source, target, data in Diagram.edges(data=True):
        result.add_edge(source, target)

        if StyleEdges:
            if "border_size" in data:
                label = "%i/%i"%(data["border_size"],data["finally_size"])
            else:
                label = data["finally_size"]
            
            result.edge[source][target]["label"] = label
            
        if StyleRefinement:
            if data["finally_size"] < Diagram.node[source]["size"]:
                result.edge[source][target]["style"]="dashed"
        

    subgraphs = []
    if StyleInputs:
        for inputs in PyBoolNet.PrimeImplicants.input_combinations(Primes):
            if not inputs: continue
            nodes = [x for x in Diagram.nodes() if PyBoolNet.Utility.Misc.dicts_are_consistent(inputs,Diagram.node[x]["attractors"][0])]
            label = PyBoolNet.StateTransitionGraphs.subspace2str(Primes,inputs)
            subgraphs.append((nodes,{"label":"inputs: %s"%label, "color":"none", "fillcolor":"lightgray"}))
            
        if subgraphs:
            result.graph["subgraphs"] = []

        PyBoolNet.Utility.DiGraphs.add_style_subgraphs(result, subgraphs)

    if StyleRanks:
        if subgraphs:
            to_rank = result.graph["subgraphs"]
        else:
            to_rank = [result]

        for graph in to_rank:
            ranks = {}
            for node, data in Diagram.nodes(data=True):
                if not node in graph:continue
                
                size = len(data["attractors"])
                if not size in ranks:
                    ranks[size]=[]
                ranks[size].append(node)
            ranks=list(ranks.items())
            ranks.sort(key=lambda x: x[0])

            for _,names in ranks:
                names = ['"%s"'%x for x in names]
                names = "; ".join(names)
                graph.graph["{rank = same; %s;}"%names]=""

    mapping = {x:str(x) for x in result.nodes()}
    networkx.relabel_nodes(result,mapping,copy=False)
    
    PyBoolNet.Utility.DiGraphs.digraph2image(result, FnameIMAGE, "dot")
    

def diagram2aggregate_image(Primes, Diagram, FnameIMAGE):
    """
    Creates the image file *FnameIMAGE* for the aggregated basin diagram given by *Diagram*.
    The aggregated basin diagram takes the union of all basins from which the same number of attractors
    can be reached even if they are not the exact same set.
    
    **arguments**:
        * *Primes*: prime implicants, needed for pretty printing of the attractors.
        * *Diagram* (networkx.DiGrap): a basin diagram
        * *FnameIMAGE* (str): name of the aggragated diagram image
        
    **returns**::
        * *None*

    **example**::

        >>> diagram2aggregate_image(diagram, "aggregated.pdf")
    """
    
    diagram = networkx.DiGraph()
    diagram.graph["node"]  = {"shape":"rect","style":"filled","color":"none"}

    for node, data in Diagram.nodes(data=True):
        x = len(data["attractors"])
        if not x in diagram:
            diagram.add_node(x, size=data["size"])
        else:
            diagram.node[x]["size"]+= data["size"]

    size_total = float(2**len(Primes))
    for x, data in diagram.nodes(data=True):
        size_percent = data["size"] / size_total
        diagram.node[x]["label"] = "<attractors: %s<br/>states: %s>"%(x,data["size"])
        diagram.node[x]["fillcolor"] = "0.0 0.0 %.2f"%(1-size_percent)
        if size_percent>0.5: diagram.node[x]["fontcolor"] = "0.0 0.0 0.8"

    for source, target in Diagram.edges():
        x = len(Diagram.node[source]["attractors"])
        y = len(Diagram.node[target]["attractors"])
        diagram.add_edge(x,y)

        
    mapping = {x:str(x) for x in diagram.nodes()}
    networkx.relabel_nodes(diagram,mapping,copy=False)
        
    PyBoolNet.Utility.DiGraphs.digraph2image(diagram, FnameIMAGE, "dot")


#######################
## auxillary functions 

def project_attractors(Attractors, Names):
    result = set()
    for space in Attractors:
        projection = tuple((k,v) for k,v in sorted(space.items()) if k in Names)
        result.add(projection)

    result = [dict(x) for x in result]

    return result


def lift_attractors(Attractors, Projection):
    return [x for x in Attractors for y in Projection if PyBoolNet.Utility.Misc.dicts_are_consistent(x,y)]


def cartesian_product(Diagrams, Factor, ComputeBorders):
    """
    creates the cartesian product of *Diagrams*.
    """

    result = networkx.DiGraph()

    # create nodes
    nodes = [x.nodes(data=True) for x in Diagrams]
    for product in itertools.product(*nodes):
        data = {}
        data["size"] = functools.reduce(operator.mul,[x["size"] for _,x in product]) * Factor
        data["formula"] = " & ".join("(%s)"%x["formula"] for _,x in product)
            
        attrs = [x["attractors"] for _,x in product]
        attrs = list(itertools.product(*attrs))
        attrs = [PyBoolNet.Utility.Misc.merge_dicts(x) for x in attrs]
        data["attractors"] = attrs

        node = tuple(x for x,_ in product)

        result.add_node(node, data)

    # create edges
    for source in result.nodes():
        for s, diagram in zip(source, Diagrams):
            factor = result.node[source]["size"] / diagram.node[s]["size"]
            for _, t, data in diagram.out_edges(s,data=True):
                
                data = {}
                basic_formula = ["(%s)"%g.node[x]["formula"] for x,g in zip(source,Diagrams) if not g==diagram]
                data["finally_size"]    = factor * diagram.edge[s][t]["finally_size"]
                formula = basic_formula + ["(%s)"%diagram.edge[s][t]["finally_formula"]]
                data["finally_formula"]  = " & ".join(formula)

                if ComputeBorders:
                    data["border_size"]     = factor * diagram.edge[s][t]["border_size"]
                    formula = basic_formula + ["(%s)"%diagram.edge[s][t]["border_formula"]]
                    data["border_formula"]  = " & ".join(formula)                    

                target = tuple(x if not g==diagram else t for x,g in zip(source,Diagrams))
                
                result.add_edge(source, target, data)

    # relabel nodes
    result = networkx.convert_node_labels_to_integers(result)
        
    return result


def diagrams_are_equal(Diagram1, Diagram2):
    """
    removes for formulas, which are different for naive / product diagrams.
    """
    g1 = Diagram1.copy()
    g2 = Diagram2.copy()

    for g in [g1,g2]:
        for x in g.nodes():
            g.node[x].pop("formula")
        for x,y in g.edges():
            if "border_formula" in g.edge[x][y]:
                g.edge[x][y].pop("border_formula")
                g.edge[x][y].pop("finally_formula")

    em = lambda x,y:x==y
    
    return networkx.is_isomorphic(g1,g2,edge_match=em)




    
if __name__=="__main__":
    print("nothing to do")



                            



