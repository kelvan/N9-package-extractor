from os import mkdir, path, chdir, listdir
from shutil import copy2 as cp
from subprocess import Popen, PIPE
import re

dpkg_info = '/var/lib/dpkg/info/'
dpkg_status = '/var/lib/dpkg/status'
script_folder = 'DEBIAN'
r = r'.*?(Package: %s.*?\n\n).*'

def _extract_control(pkgname):
    with open(dpkg_status, 'r') as f:
        rg = re.compile(r % pkgname, re.MULTILINE|re.DOTALL)
        control = rg.match(f.read()).groups()[0]
    
    cs = control.split('\n')
    return '\n'.join(cs[:1] + cs[2:])

def copy_data(pkgname, target):
    """ Copy files of package to target folder
    """
    p = Popen(['dpkg', '--listfiles', pkgname], stdout=PIPE, stderr=PIPE)
    lst = p.stdout.readlines()
    
    for fn in lst:
        fn = fn.strip()
        if path.exists(fn):
            # file/folder of package exist
            if path.isdir(fn):
                if not path.exists(path.join(target, fn[1:])):
                    # create target folder if necessary
                    mkdir(path.join(target, fn[1:]))
            else:
                try:
                    cp(fn, path.join(target, fn[1:]))
                except OSError as e:
                    print e
                except IOError as e:
                    print e
        else:
            print 'path not found: %s' % fn
    
    if not path.exists(path.join(target, script_folder)):
        mkdir(path.join(target, script_folder))
    
    for fn in filter(lambda x: x.startswith(pkgname), listdir(dpkg_info)):
        try:
            cp(path.join(dpkg_info, fn), path.join(target, script_folder, fn))
        except OSError as e:
            print e
        except IOError as e:
            print e

    # copy control information
    with open(path.join(target, script_folder, 'control'), 'w') as f:
        f.write(_extract_control(pkgname))

def generate_aegis(pkgname, target):
    """ generates aegis token for package and saves it to target folder
    """
    raise NotImplementedError()

def build_package(target):
    """ make package from target folder
    """
    p = Popen(['dpkg-deb', '-b', target], stdout=PIPE, stderr=PIPE)
    stderr = p.stderr.read()
    
    if stderr:
        raise IOError(stderr)
    else:
        return True

def check_packagename(pkgname):
    p = Popen(['dpkg', '--status', pkgname], stdout=PIPE, stderr=PIPE)
    stdout = p.stdout.readlines()
    
    return len(stdout) > 0
