from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf
"""
Some util functions
"""
from joblauncher.lib.plugins import form
"""
An example form, that you can also define in this file
"""
from yapsy.IPlugin import IPlugin
"""
The plugin system
"""
import os, shutil
"""
Import here other libraries that you need
"""


class ExampleFilesSelection(IPlugin, OperationPlugin):

    def title(self):
        """
        Define the Operation title.
        """
        return 'Merge'

    def path(self):
        """
        Define the Operation path. Must be unique among all others operations.
        """
        return ['Manipulation', 'Merge']

    def output(self):
        """
        Define what form will be used.
        """
        return form.FilesForm

    def description(self):
        """
        Document your Operation.
        """
        return '''It is just an example.'''
    def parameters(self):
        """
        Define the parameters needed by your Operation.
        """
        return {'track_1' : 'The first file. Required', 'track_2' : 'The second file. Required', 'thr' : 'a threshold.'}

    def files(self):
        """
        Define which parameters will receive a list of files as pre-input.
        """
        return ['track_1', 'track_2']


    def process(self, **kw):
        """
        Define here the Operation itself with the parameters gathered form the form.
        """
        file_1 = rp(kw, 'track_1')                    # retrieve parameter `track_1`
        file_2 = rp(kw, 'track_2')                    # rp `track_2`
        threshold = int(rp(kw, 'thr'))                # rp `thr` and convert it to an int

        root, fname = os.path.split(file_1)           # simulated process
        nfile = os.path.join(root, 'new_file.bed')    # take the first file and
        shutil.move(file_1, nfile)                    # rename it to 'new_file.bed'

        nf(self, nfile)                               # add a new file in the job result
                                                      # nf(plugin, file) will add the file
                                                      # to the output of the job.
                                                      # the file can be retrieved by your service after.

        return 'example terminated'                   # the Operation return value
