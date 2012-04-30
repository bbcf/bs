"""
Small patch for yapsy library as ConfigParser module has been renamed to configparser in python 3.0 
use it like : $ python yapsy_patch.py
(must have yapsy installed in your PYTHON_PATH)
"""
import yapsy, os, fileinput
file_to_patch = os.path.join(os.path.split(yapsy.__file__)[0], 'PluginManager.py')

for line in fileinput.input(file_to_patch, inplace=1):
    if not line.startswith('import configparser') :
        print line.rstrip()
    else :
        print "try:\n    import configparser\nexcept ImportError:\n    import ConfigParser as configparser"
    
