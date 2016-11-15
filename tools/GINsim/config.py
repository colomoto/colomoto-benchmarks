import os
import urllib.request

multivalued = True
input_format =  'sbml'
url = 'http://ginsim.org/sites/default/files/ginsim-dev/GINsim-2.9.4-SNAPSHOT-jar-with-dependencies.jar'
installed_file = 'local/GINsim.jar'

is_installed = os.path.exists(installed_file)


def install():
    "Download the GINsim.jar file"
    os.makedirs('local')
    urllib.request.urlretrieve (url, installed_file)


if __name__ == '__main__':
    if not is_installed:
        install()

