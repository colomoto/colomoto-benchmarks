import os
import sys

multivalued = False
input_format =  'bnet'
url = 'https://github.com/hklarner/PyBoolNet/releases/download/v2.1/PyBoolNet-2.1_linux64.tar.gz'

folder = os.path.abspath(os.path.split(__file__)[0])
pypath = os.path.join(folder, 'source', 'PyBoolNet-2.1')

sys.path.insert(0,pypath)
#print(pypath)

try:
    import PyBoolNet
    is_installed = True
except:
    is_installed = False

