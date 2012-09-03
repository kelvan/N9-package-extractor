from os import mkdir, path, chdir, listdir
from shutil import copy2 as cp
from subprocess import Popen, PIPE

dpkg_info = '/var/lib/dpkg/info/'
script_folder = 'DEBIAN'

def copy_data(pkgname, target):
    """ Copy files of package to target folder
    """
    p = Popen(['dpkg', '--listfiles', pkgname], stdout=PIPE, stderr=PIPE)
    lst = p.stdout.readlines()
    
    for fn in lst:
        if path.exists(fn):
            # file/folder of package exist
            if path.isdir(fn):
                if not path.exists(path.join(target, fn[1:])):
                    # create target folder if necessary
                    mkdir(path.join(target,fn[1:]))
            else:
                try:
                    cp(fn, path.join(target, fn[1:]))
                except OSError as e:
                    print e
                except IOError as e:
                    print e
        else:
            print 'path not found: %s' % fn
            
    for fn in filter(lambda x: x.startswith(pkgname), listdir(dpkg_info)):
        try:
            cp(path.join(dpkg_info, fn), path.join(target, script_folder))
        except OSError as e:
            print e
        except IOError as e:
            print e

def generate_aegis(pkgname, target):
    """ generates aegis token for package and saves it to target folder
    """
    raise NotImplementedError()

def build_package(target):
    """ make package from target folder
    """
    Popen(['dpkg-deb', '-b', target], stdout=PIPE, stderr=PIPE)
    stderr = p.stderr.read()
    
    if stderr:
        raise IOError(stdterr)
    else:
        return True

def check_packagename(pkgname):
    p = Popen(['dpkg', '--status', pkgname], stdout=PIPE, stderr=PIPE)
    stdout = p.stdout.readlines()
    
    return len(stdout) > 0
