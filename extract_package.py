#!/usr/bin/env python

from os import mkdir, chdir, path, listdir
import sys
from shutil import copy2 as cp
from subprocess import Popen, PIPE

scriptpath = '/var/lib/dpkg/info/'

if path.isdir(sys.argv[1]) or not path.exists(sys.argv[1]):
    package = sys.argv[1]
    target = package
    p = Popen(['dpkg', '--listfiles', package], stdout=PIPE, stderr=PIPE)
    lst = p.stdout.read().split()

    if not lst:
        print p.stderr.readline()
        p = Popen(['apt-cache', '--installed', 'search', package], stdout=PIPE)
        print 'apt-cache search result:'
        print p.stdout.read()
        sys.exit(0)
else:
    target = path.splitext(path.basename(sys.argv[1]))[0]
    with open(sys.argv[1], 'r') as f:
        lst = f.read().split()

if not path.exists(target):
    mkdir(target)
chdir(target)

for fn in lst:
    if path.exists(fn):
        if path.isdir(fn):
            if not path.exists(fn[1:]):
                mkdir(fn[1:])
        else:
            try:
                cp(fn, fn[1:])
            except OSError as e:
                print e
            except IOError as e:
                print e
    else:
        print 'path not found: %s' % fn

dpkgpath = 'dpkg_info'
if not path.exists(dpkgpath):
    mkdir(dpkgpath)
    
for fn in filter(lambda x: x.startswith(package), listdir(scriptpath)):
    try:
        cp(path.join(scriptpath, fn), dpkgpath)
    except OSError as e:
        print e
    except IOError as e:
        print e

p = Popen(['du', '-sh', '.'], stdout=PIPE)
print '%s copied' % p.stdout.readline().split()[0]
