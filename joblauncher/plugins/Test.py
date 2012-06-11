from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf, BaseForm, temporary_path
from joblauncher.lib.plugins import form
from yapsy.IPlugin import IPlugin
import tw2.forms
from tw.forms import validators as twv
import os

class Test(IPlugin, OperationPlugin):
    
    def title(self):
        """
        A name for the Operation.
        """
        return 'Test'

    def description(self):
        """
        A quick description about your operation.
        """
        return '''A test plugin'''


    def path(self):
        """
        An unique path among all plugins.
        """
        return ['Tests', 'test form']

    def output(self):
        """
        An output form (Toscawidget, Sprox).
        """
        return TestForm

    def parameters(self):
        """
        Operation parameters. A dict with the input(s) and output(s).
        """
        return {'in' : ['one', 'two', 'three'],
                'out' : {'result' : 'random'}
        }

    def files(self):
        """
        The list of "in" parameters that are files.
        """
        return ['two']

    def meta(self):
        """
        A dict with additional information. Put here everything you want.
        """
        return {'version' : "1.0.0",
                'author' : "BBCF",
                'contact' : "webmaster-bbcf@epfl.ch"}

    def process(self, **kw):
        print 'process test with parameters : %s' % kw
        import time
        time.sleep(5)
        tmp = temporary_path(fname='my output', ext='fasta')
        # process the file. Here I just touch one file "fasta"
        with file(tmp, 'a'):
            os.utime(tmp, None)
        # add the file to the output (param must match)
        nf(self, tmp, 'two')

        print 'end test process'
        return 1

import tw2.core

class TestForm(BaseForm):
    hover_help = True
    show_errors = True
    one = tw2.forms.TextField(label='the parameter one : ', help_text='Some description.', hover_help=True, validator=twv.NotEmpty)
    two = tw2.forms.SingleSelectField()
    three = tw2.forms.CheckBox()
    submit = tw2.forms.SubmitButton(id="submit", value="Submit test job")
