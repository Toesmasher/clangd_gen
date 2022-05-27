#!/usr/bin/env python3

import argparse
import json
import os

# Take a list of files, return a list of directories containing these files,
# without duplicate entries
def unique_dirs(files: list) -> list:
    results = []

    for f in files:
        d = os.path.dirname(f)
        if d not in results:
            results.append(d)

    return results

# Find all files with a certain suffix in a given root directory
def find_files(root: str, suffix: str) -> list:
    results = []

    suffix_pos = -len(suffix)

    for root, dirs, files in os.walk(root, topdown=True):
        for f in files:
            if f[suffix_pos:] == suffix:
                results.append(os.path.join(root, f))

    return results

if __name__ == '__main__':
    p = argparse.ArgumentParser('clangd_gen')
    p.add_argument('path', type=str, nargs='?', default=os.getcwd())

    r = p.parse_args()
    r.path = os.path.abspath(r.path)

    if not os.path.isdir(r.path):
        print(('%s is not a valid path' % (r.path)))
        exit(-1)

    # Find all relevant files and directories
    c_files = find_files(r.path, '.c')
    h_files = find_files(r.path, '.h')
    h_dirs = unique_dirs(h_files)

    # Create all the include arguments
    include_lines = []
    for h in h_dirs:
        include_lines.append('-I%s' % (h))

    # Create JSON representation of compile_commands
    cc_out = []
    for c in c_files:
        c_entry = {}
        c_entry['directory'] = r.path
        c_entry['file'] = c
        c_entry['arguments'] = include_lines

        cc_out.append(c_entry)

    # Dump it all out into a string and save
    cc_out_str = json.dumps(cc_out, indent=2)
    f = open('%s/compile_commands.json' %(r.path), 'w')
    f.write(cc_out_str)
    f.close()
