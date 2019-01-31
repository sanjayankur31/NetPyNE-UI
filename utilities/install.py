import setuptools
from setuptools.command.install import install
import subprocess
import json
import os, sys
from shutil import copyfile

NETPYNE = 'https://github.com/Neurosim-lab/netpyne.git'
PYGEPPETTO = 'https://github.com/openworm/pygeppetto.git'
GEPPETTO_CLIENT = 'https://github.com/openworm/geppetto-client.git'
GEPPETTO_NETPYNE = 'https://github.com/MetaCell/geppetto-netpyne.git'
ORG_GEPPETTO_FRONTEND_JUPYTER = 'https://github.com/openworm/org.geppetto.frontend.jupyter.git'

branch = None
JUPYTER_EXTENSION_PATH = './org.geppetto.frontend.jupyter'
###############################################################################
#                                 FUNCTIONS                                   #
###############################################################################
#by default clones branch (which can be passed as a parameter python install.py branch test_branch)
#if branch doesnt exist clones the default_branch
def clone(repository, folder, default_branch, cwdp='', recursive = False, destination_folder = None):
    global branch
    print("Cloning "+repository)
    if recursive:
        subprocess.call(['git', 'clone', '--recursive', repository], cwd='./'+cwdp)
    else:
        if destination_folder:
            subprocess.call(['git', 'clone', repository, destination_folder], cwd='./'+cwdp)
        else:
            subprocess.call(['git', 'clone', repository], cwd='./'+cwdp)
    checkout(folder, default_branch, cwdp)

def checkout(folder, default_branch, cwdp):
    currentPath = os.getcwd()
    print(currentPath)
    newPath = currentPath + "/" + cwdp + folder
    print(newPath)
    os.chdir(newPath)
    python_git = subprocess.Popen("git branch -a",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    outstd, errstd = python_git.communicate()
    if branch and branch in str(outstd) and branch != 'development': # don't ckeckout development for netpyne
        subprocess.call(['git', 'checkout', branch], cwd='./')
    else:
        subprocess.call(['git', 'checkout', default_branch], cwd='./')
    os.chdir(currentPath)

def main(argv):
    global branch
    if(len(argv) > 0):
        if(argv[0] == 'branch'):
            branch = argv[1]

if __name__ == "__main__":
    main(sys.argv[1:])

os.chdir(os.getcwd()+"/../")

###############################################################################
#                               CLONING REPOS                                 #
###############################################################################
clone(repository=PYGEPPETTO,
    folder='pygeppetto',
    default_branch='development'
)

clone(repository=NETPYNE,
    folder='netpyne',
    default_branch='ui'
)

clone(repository=ORG_GEPPETTO_FRONTEND_JUPYTER,
    folder='org.geppetto.frontend.jupyter',
    default_branch='development'
)

clone(repository=GEPPETTO_CLIENT,
    folder='geppetto-client',
    default_branch='development',
)

clone(repository=GEPPETTO_NETPYNE,
    folder='geppetto-netpyne',
    default_branch='development',
)
###############################################################################
#                              INSTALLING REPOS                               #
###############################################################################
# install repos
subprocess.call(['pip', 'install', '-e', '.'], cwd='./netpyne/')
subprocess.call(['pip', 'install', '-e', '.'], cwd='./pygeppetto/')
subprocess.call(['pip', 'install', '-e', '.'], cwd=JUPYTER_EXTENSION_PATH)

###############################################################################
#                                BUILD BUNDLES                                #
###############################################################################
# install and build org.geppetto.frontend.jupyter
with open('npm_frontend_jupyter_log', 'a') as stdout:
    subprocess.call(['npm', 'install'], cwd='./org.geppetto.frontend.jupyter/js', stdout=stdout)
subprocess.call(['npm', 'run', 'build-dev'], cwd='./org.geppetto.frontend.jupyter/js')

#Installing and buil geppetto application
with open('npm_frontend_log', 'a') as stdout:
    subprocess.call(['npm', 'install'], cwd='./geppetto-netpyne', stdout=stdout)
subprocess.call(['npm', 'run', 'build-dev-noTest'], cwd='./geppetto-netpyne')

###############################################################################
#                     INSTALLING JUPYTER EXTENSIONS                           #
###############################################################################
print("Installing jupyter_geppetto Jupyter Extension ...")
subprocess.call(['jupyter', 'nbextension', 'install', 
                '--py', '--symlink', '--sys-prefix', 'jupyter_geppetto'],
                cwd=JUPYTER_EXTENSION_PATH
)
subprocess.call(['jupyter', 'nbextension', 'enable', 
                '--py', '--sys-prefix', 'jupyter_geppetto'],
                cwd=JUPYTER_EXTENSION_PATH
)
subprocess.call(['jupyter', 'nbextension', 'enable', 
                '--py', '--sys-prefix', 'widgetsnbextension'],
                cwd=JUPYTER_EXTENSION_PATH
)
subprocess.call(['jupyter', 'serverextension', 'enable', 
                '--py', '--symlink', '--sys-prefix', 'jupyter_geppetto'],
                cwd=JUPYTER_EXTENSION_PATH
)
###############################################################################
#                     FINAL NETPYNE-UI INSTALLATION                           #
###############################################################################
print("Installing NetPyNE UI python package ...")
subprocess.call(['pip', 'install', '-e', '.', '--no-deps'], cwd='.')