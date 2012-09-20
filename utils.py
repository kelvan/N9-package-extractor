from os import mkdir, path, chdir, listdir, stat
from shutil import copy2 as cp
from subprocess import Popen, PIPE
import re

dpkg_info = '/var/lib/dpkg/info/'
dpkg_status = '/var/lib/dpkg/status'
aegis_isjawurscht = '/var/lib/aegis/restok/restok.conf'
script_folder = 'DEBIAN'
aegis_tokenr = r'(\w+:\n?(\s[\w.:/-]+\n)+)'
r = r'.*?(Package: %s.*?\n\n).*'

def _extract_control(pkgname):
    with open(dpkg_status, 'r') as f:
        rg = re.compile(r % pkgname, re.MULTILINE|re.DOTALL)
        control = rg.match(f.read()).groups()[0]
    
    cs = control.split('\n')
    allowed_fields = ['Package', 'Source', 'Version', 'Section',
                      'Priority', 'Architecture', 'Essential',
                      'Depends', 'Recommends', 'Suggests', 'Enhances',
                      'Pre-Depends', 'Installed-Size', 'Maintainer',
                      'Description', 'Homepage']
    c = ''
    
    for l in cs:
        if l.split(':')[0] in allowed_fields:
            c += l + '\n'
    
    return c + '\n'

def copy_data(pkgname, target):
    """ Copy files of package to target folder
    """
      
    with open(path.join('/var/lib/dpkg/info/', pkgname + '.list')) as f:
        lst = f.readlines()
    
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
            if not fn.endswith('.list'):
                cp(path.join(dpkg_info, fn), path.join(target, script_folder, fn.split('.')[1]))
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
    #Todo: provide, contstraint, domain, dbus
    with open(aegis_isjawurscht, 'r') as f:
        rg = re.compile(r % pkgname, re.MULTILINE|re.DOTALL)
        tc = rg.match(f.read()).groups()[0]
    
    tct = re.findall(aegis_tokenr, tc)
    tct = map(lambda entry: entry[0], tct)
    
    with open(path.join(target, '_aegis'), 'w') as _aegis:
        haverequest = False
        
        _aegis.write('<aegis>\n')
        for entry in tct:
            key, _, value = entry.partition(':')
            if key == 'Request':
                if haverequest:
                    _aegis.write('  </request>\n')
                haverequest = True
                _aegis.write('  <request>\n')
                for token in value.strip().split():
                    if not token.startswith('AID::'):
                        _aegis.write('    <credential name="%s" />\n' % token)
                
            elif key == 'Object':
                value = value.strip()
                if path.exists(value):
                    _aegis.write('    <for path="%s" />\n' % value)
                
        if haverequest:
            _aegis.write('  </request>\n')
        _aegis.write('</aegis>')
        
    #Popen(['ar', 'q', pkgname + '.deb', '_aegis']).wait()
    append_aegismanifest(path.join(target,pkgname + '.deb'), path.join(target, '_aegis'))
        

def build_package(basefolder, target):
    """ make package from target folder
    """
    p = Popen(['dpkg-deb', '-b', basefolder], stdout=PIPE, stderr=PIPE)
    stderr = p.stderr.read()
    
    if stderr:
        raise IOError(stderr)
    else:
        return True

def check_packagename(pkgname):
    return path.exists(path.join('/var/lib/dpkg/info/', pkgname + '.list'))
    
def append_aegismanifest(archive, aegismanifest):
    """ implementation of 'ar q $archive $file'
    """
    with open(archive, 'a') as deb:
        manifest_data = stat(aegismanifest)
        #filename 16 byte ascii rightpadded with spaces
        deb.write('_aegis'.ljust(16))
        #file creation time 12 byte ascii rightpadded with spaces
        deb.write(str(int(manifest_data.st_ctime)).ljust(12))
        #owner, group each 6 byte ascii rightpadded with spaces
        deb.write('0'.ljust(6) + '0'.ljust(6))
        #file mode 8 byte ascii rightpadded with spaces
        deb.write('100644'.ljust(8))
        #file size 10 byte ascii rightpadded with spaces
        deb.write(str(manifest_data.st_size).ljust(10))
        #file magic (0x60 0x0A)
        deb.write('`\n')
        with open(aegismanifest) as manifest:
            deb.write(manifest.read())
    
