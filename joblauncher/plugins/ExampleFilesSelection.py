from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf
from joblauncher.lib.plugins import form
from yapsy.IPlugin import IPlugin
from tw import forms as twf
from tg import tmpl_context
import os, shutil


class ExampleFilesSelection(IPlugin, OperationPlugin):

    def title(self):
        return 'Merge'

    def path(self):
        return ['Manipulation', 'Merge']

    def output(self):
        return form.FilesForm

    def description(self):
        return '''
        Merge two files.
        '''
    def parameters(self):
        return {'track_1' : 'The first file. Required', 'track_2' : 'The second file. Required'}


    def process(self, **kw):
        file_1 = rp(kw, 'track_1')
        file_2 = rp(kw, 'track_2')
        root, fname = os.path.split(file_1)
        nfile = os.path.join(root, 'new_file')
        shutil.move(file_1, nfile)

        nf(self, nfile)
        return 'files merged'
