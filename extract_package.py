#!/usr/bin/env python

from os import mkdir, chdir, path, listdir
import sys
from shutil import copy2 as cp
from subprocess import Popen, PIPE
from utils import *

if len(sys.argv) < 3:
    print 'Usage: %s pkgname target' % sys.argv[0]
    sys.exit(1)

if path.isdir(sys.argv[2]) or not path.exists(sys.argv[2]):
    pkgname = sys.argv[1]
    target = sys.argv[2]

    if not check_packagename(pkgname):
        p = Popen(['apt-cache', '--installed', 'search', pkgname], stdout=PIPE)
        print '** Package not found **'
        print
        print 'apt-cache search result:'
        print p.stdout.read()
        sys.exit(2)
else:
    print 'invalid target'
    sys.exit(3)

if not path.exists(target):
    mkdir(target)

print 'Copying data'
copy_data(pkgname, target)

print 'Generating aegis token'
generate_aegis(pkgname, target)

print 'Building package'
build_package(target)

p = Popen(['du', '-sh', '.'], stdout=PIPE)
print '%s copied' % p.stdout.readline().split()[0]
