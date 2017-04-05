http://people.kth.se/~dubrova/bns.html



BNS
BNS is a software tool for computing attractors in Boolean Networks with Synchronous update. Synchronous Boolean networks [1] are used for the modeling of genetic regulatory networks.

BNS implements the algorithm presented in [2] which is based on a SAT-based bounded model checking. BNS uses much less space compared to BooleNet or other BDD-based approaches for computing attractors. It can handle several orders of magnitude larger networks.

BNS reads in a Boolean network description represented in a .cnet format similar to the Berkeley Logic Interchange Format (BLIF) format commonly used in synthesis and verification tools and prints out the set of network's attractors.

BNS binaries are available for the following platforms:

    Linux: BNS-1.0. Tested on Red Hat Enterprise kernel 2.6.18, Ubuntu 8.04 (64 bit), and Fedora Core 8.

    Windows Cygwin: BNS-1.0. Tested on cygwin1.dll version 1.5.25.

User manual for BNS.

TEST INPUT FILES
You can use the following files to test BNS:

    The Boolean network model of of the control of flower morphogenesis in Arabidopsis thaliana [3]. It has 10 attractors of length 1.

    The Boolean network model of the control of T-helper cell differentiation [4]. It has 3 attractors of length 1.

    The Boolean network model of the T-cell receptor signaling pathway [5]. It has 8 attractors of length 1 and one attractor of length 6.

    The Boolean network model of the control of the mammalian cell cycle [6]. It has one attractor of length 1 and one attractor of length 7.

    The Boolean network model of the control of the fission yeast cell cycle regulation [7]. It has 13 attractors of length 1.

    The Boolean network model of the control of the budding yeast cell cycle regulation [8]. It has 7 attractors of length 1.

    The Boolean network model of interactions between the segment polarity genes in Drosophila melanogaster [9]. It has 7 attractors of length 1.

You can also test BNS on randomly generated graphs. Statistical features of randomly generated Boolean networks on the critical line are believed to capture the dynamics of genetic regulatory networks of living organisms [1]. The following simple program will generate you an n-node random Boolean network on the critical line in the .cnet format.
REFERENCES:
[1] Boolean Dynamics with Random Couplings, M. Aldana, S. Coopersmith, L. P. Kadanoff, 2002, http://arXiv.org/abs/nlin/0204062.

[2] "A SAT-Based Algorithm for Finding Attractors in Synchronous Boolean Networks", E. Dubrova, M. Teslenko, IEEE/ACM Transactions on Computational Biology and Bioinformatics, vol. 8, no. 5, 2011, pp. 1393-1399.

[3] "From Genes to Flower Patterns and Evolution: Dynamic Models of Gene Regulatory Networks", A. Chaos, M. Aldana, C. Espinosa-Soto, B. G. P. de Leon, A. G. Arroyo, E. R. Alvarez-Buylla, Journal of Plant Growth Regulation, vol. 25, n. 4, 2006, pp. 278-289.

[4] "A Method for the Generation of Standardized Qualitative Dynamical Systems of Regulatory Networks", L. Mendoza and I. Xenarios, Journal of Theoretical Biology and Medical Modeling, 2006, vol. 3, no. 13.

[5] "A Methodology for the Structural and Functional Analysis of Signaling and Regulatory Networks", S. Klamt, J. Saez-Rodriguez, J. A. Lindquist, L. Simeoni, E. D. Gilles, JBMC Bioinformatics, 2006, vol. 7, no. 56.

[6] "Dynamical Analysis of a Generic Boolean Model for the Control of the Mammalian Cell Cycle", A. Faure, A. Naldi, C. Chaouiya, D. Thieffry, Bioinformatics, 2006, vol. 22, no. 14, pp. e124-e131.

[7] "Boolean Network Model Predicts Cell Cycle Sequence of Fission Yeast", M. I. Davidich, S. Bornholdt, PLoS ONE. 2008 Feb 27, 3(2):e1672.

[8] "The Yeast Cell-Cycle Network is Robustly Designed", Fangting Li, Tao Long, Ying Lu, Qi Ouyang, Chao Tang, PNAS April 6, 2004, vol. 101 no. 14, 4781-4786.

[9] "The Topology of the Regulatory Interactions Predicts the Expression Pattern of the Segment Polarity Genes in Drosophila Melanogaster", R. Albert and H. G. Othmer, Journal of Theoretical Biology, 2003, vol. 223, no. 1, pp. 1-18.

CONTACT PERSON:

    Elena Dubrova
    Department of Electronics, Computer and Software
    School of Information and Communication Technology
    dubrova@kth.se


