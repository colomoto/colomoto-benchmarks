multivalued = False
input_format =  'bns'
url = 'https://people.kth.se/~dubrova/bns.html'


try:
    import subprocess
    cmd_bns  = ["tools/bns/source/bns","tools/bns/source/test.cnet"]
    proc_bns  = subprocess.Popen(cmd_bns, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = proc_bns.communicate()
    output = output.decode()

    if not output.count("Attractor") == 9:
        raise Exception

    is_installed = True

except:
    is_installed = False
