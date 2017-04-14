import os
import urllib.request

multivalued = True
input_format =  'bnet'
url = 'http://colomoto.org/pub/bioLQM/bioLQM-0.4-SNAPSHOT-jar-with-dependencies.jar'
installed_file = 'local/bioLQM.jar'

is_installed = os.path.exists(installed_file)


def install():
    "Download the bioLQM jar file"
    if not os.path.exists('local'):
        os.makedirs('local')
    urllib.request.urlretrieve (url, installed_file)


if __name__ == '__main__':
    if not is_installed:
        install()

