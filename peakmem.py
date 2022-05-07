#!/usr/bin/env python

import os
import time
import sys

_pid = os.getpid()

print('PID of memory monitoring process : ' + str(_pid))

def _run(pid):
    delay = 0.1 # seconds
    fname = '/proc/' +  str(pid) + '/status'
    assert(os.path.exists(fname))
    peakmem_gb = -1.0
    ct = 0
    while(True):
        time.sleep(delay)
        if os.path.exists(fname):
            #print('checking peak memory')
            cmd = 'grep -i vmpeak ' + fname
            result = os.popen(cmd).read()
            tokens = result.split()
            assert(len(tokens) == 3)
            assert(tokens[2] == 'kB')
            this_peakmem_gb = float(tokens[1])*(1.0e3)/(1.0e9)
            peakmem_gb = max(peakmem_gb, this_peakmem_gb)
            if (ct % 10) == 0:
                print(result.replace('\n', ''), ' = ', '{:.2f}'.format(peakmem_gb), ' GB, for PID = ', pid)
            ct += 1
        else:
            break

    print('THE FINAL PEAK MEMORY USAGE IN GB WAS : ' + str(peakmem_gb))

pid = int(sys.argv[1])

_run(pid)
