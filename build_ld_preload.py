import os
import subprocess
from collections import defaultdict, namedtuple

KERNEL_IMAGE_WITH_DBG = '/root/app-elfloader/build/app-elfloader_qemu-x86_64.dbg'
BYPASS_FUNCTIONS_CONFIG = './needed_bypass_functions'

# read config
bypass_functions = {}
with open(BYPASS_FUNCTIONS_CONFIG) as f:
    for line in f:
        bypass_functions[line.strip()] = None

# get kernel func address
for line in subprocess.run('objdump -D {}'.format(KERNEL_IMAGE_WITH_DBG), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.decode('utf-8').split('\n'):
    for func in bypass_functions.keys():
        if '<{}>:'.format(func) in line:
            bypass_functions[func] = {'kernel_addr': int(line.split()[0], 16)}

# write source code
with open('build_library/preload.c', 'w') as w:
    w.write('#include "ld_preload.h"\n\n')
    for f, addr in bypass_functions.items():
        if addr is None:
            print('Function {} not found in kernel image!'.format(f))
            continue
        w.write('ADAPT({})\n'.format(f))

# compile .so
os.system('gcc build_library/preload.c -o build_library/preload.so -fpic -shared -O3')

# get library func address
for line in subprocess.run('objdump -D build_library/preload.so', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.decode('utf-8').split('\n'):
    for func in bypass_functions.keys():
        if '<{}>:'.format(func) in line:
            bypass_functions[func]['lib_addr'] = int(line.split()[0], 16)

# rewrite .so
with open('build_library/preload.so', 'rb+') as so:
    for f, info in bypass_functions.items():
        so.seek(info['lib_addr']+6)
        so.write(info['kernel_addr'].to_bytes(8, 'little'))
