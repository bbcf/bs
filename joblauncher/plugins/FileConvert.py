from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf, BaseForm, temporary_path
from yapsy.IPlugin import IPlugin
import os, shutil, track

class FileConvert(IPlugin, OperationPlugin):

    def title(self):
        """
        Define the Operation title.
        """
        return 'Convert file'

    def path(self):
        """
        Define the Operation path. Must be unique among all others operations.
        """
        return ['Manipulation', 'Convert']

    def output(self):
        """
        Define what form will be used.
        """
        return ConvertForm

    def description(self):
        """
        Document your Operation.
        """
        return '''Convert file from a format to another.'''

    def parameters(self):
        """
        Define the parameters needed by your Operation.
        """
        return {'in' : ['to', 'infile'],
                'out' : {'conv' : 'track'}}

    def files(self):
        """
        Define which parameters will receive a list of files as pre-input.
        """
        return ['infile']

    def meta(self):
        """
        A dict with additional information. Put here everything you want.
        """
        return {'version' : "1.0.0",
                'author' : "BBCF",
                'contact' : "webmaster-bbcf@epfl.ch",
                'library' : 'http://bbcf.epfl.ch/track'}

    def process(self, **kw):
        """
        Define here the Operation itself with the parameters gathered form the form.
        """
        _to = rp(kw, 'to')
        infile = rp(kw, 'infile')
        outfile = temporary_path(fname='converted', ext=_to)
        track.convert(infile, outfile)
        nf(self, outfile, 'conv')
        return 1



import tw2.forms as twf
import tw2.core as twc

class ConvertForm(BaseForm):
    hover_help = True
    show_errors = True
    infile = twf.SingleSelectField(label='File', help_text='Select the file.', hover_help=True, validator=twf.FileValidator(required=True))
    to = twf.SingleSelectField(label='Output format', help_text='Select the output format of your file.',
        options=['wig', 'bed', 'sql', 'gff', 'sga'], validator=twc.Validator(required=True), hover_help=True)
    submit = twf.SubmitButton(id="submit", value="Convert")

