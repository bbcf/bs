from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf, BaseForm, temporary_path
from yapsy.IPlugin import IPlugin
import tw2.forms as twf
import tw2.core as twc
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
        """
        Define here the process of your operation, with the parameters gathered from the form.
        """
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



class TestForm(BaseForm):
    hover_help = True
    show_errors = True
    one = twf.TextField(label='the parameter one : ', help_text='Some description.', hover_help=True,
        validator=twc.validator(required=True))
    two = twf.SingleSelectField(twf.FileValidator(required=True))
    three = twf.CheckBox()
    submit = twf.SubmitButton(id="submit", value="Submit test job")
