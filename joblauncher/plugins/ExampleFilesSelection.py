from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf
from joblauncher.lib.plugins import form
from yapsy.IPlugin import IPlugin
from tw import forms as twf
from tg import tmpl_context


class ExampleFilesSelection(IPlugin, OperationPlugin):

    def title(self):
        return 'Select two files'

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
        print 'process'
        print kw
        file_1 = rp(kw, 'track_1')
        file_2 = rp(kw, 'track_2')
        print '---------------------------'
        print file_1
        print file_2
        nf(self, file_1)
        nf(self, file_2)
        return 'done %s, %s' % (file_1, file_2)
