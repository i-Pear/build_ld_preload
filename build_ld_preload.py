import os
import subprocess
from collections import defaultdict, namedtuple

KERNEL_IMAGE_WITH_DBG = '/root/app-elfloader/build/app-elfloader_qemu-x86_64.dbg'
BYPASS_FUNCTIONS_CONFIG = './needed_bypass_functions'

# {func_name}-{args_count} -> kernel_address
bypass_functions = {}
func_args_count = {}

ukplat_tlsp_enter_addr = None
ukplat_tlsp_exit_addr = None

# read config
with open(BYPASS_FUNCTIONS_CONFIG) as f:
    for line in f:
        func_info = line.strip().split('-')
        bypass_functions[func_info[0]] = None
        func_args_count[func_info[0]] = int(func_info[1])

# get kernel func address
for line in subprocess.run('objdump -D {}'.format(KERNEL_IMAGE_WITH_DBG), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.decode('utf-8').split('\n'):
    if '>:' not in line:
        continue
    if '<ukplat_tlsp_enter>:' in line:
        ukplat_tlsp_enter_addr = int(line.split()[0], 16)
        continue
    if '<ukplat_tlsp_exit>:' in line:
        ukplat_tlsp_exit_addr = int(line.split()[0], 16)
        continue
    for func in bypass_functions.keys():
        if '<{}>:'.format(func) in line:
            bypass_functions[func] = int(line.split()[0], 16)

assert ukplat_tlsp_enter_addr is not None
assert ukplat_tlsp_exit_addr is not None

# write source code
with open('build/preload.c', 'w') as w:
    w.write('#include "ld_preload.h"\n\n')
    w.write('unsigned long (*ukplat_tlsp_enter)(void) = {}ULL;\n'.format(hex(ukplat_tlsp_enter_addr)))
    w.write('void (*ukplat_tlsp_exit)(unsigned long orig_tlsp) = {}ULL;\n\n'.format(hex(ukplat_tlsp_exit_addr)))
    for f, addr in bypass_functions.items():
        if addr is None:
            print('Function [{}] not found in kernel image, skipping...'.format(f))
            continue
        f_args_count = func_args_count[f]
        w.write('unsigned long {}({}) {{\n'.format(f, ', '.join(['unsigned long arg{}'.format(x) for x in range(f_args_count)])))
        w.write('unsigned long orig_tlsp = ukplat_tlsp_enter();\n')
        w.write('unsigned long ret = ((unsigned long (*)({})) {}ULL)({});\n'.format(', '.join(['unsigned long arg{}'.format(x) for x in range(f_args_count)]), hex(addr), ', '.join(['arg{}'.format(x) for x in range(f_args_count)])))
        w.write('ukplat_tlsp_exit(orig_tlsp);\n')
        w.write('return ret;\n')
        w.write('}\n\n')

# compile .so
os.system('gcc build/preload.c -o build/preload.so -fpic -shared -O3')
