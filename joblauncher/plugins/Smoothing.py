from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf, tmp_path
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
Import here other libraries that you need (they must be installed on the system).
"""
from track.manipulate import window_smoothing

class Smoothing(IPlugin, OperationPlugin):

    def title(self):
        """
        Define the Operation title.
        """
        return 'Window smoothing'

    def path(self):
        """
        Define the Operation path. Must be unique among all others operations.
        """
        return ['Signal', 'smoothing']

    def output(self):
        """
        Define what form will be used.
        """
        return SmoothingForm

    def description(self):
        """
        Document your Operation.
        """
        return '''A window smoothing'''


    def parameters(self):
        """
        Define the parameters needed by your Operation.
        """
        return {'track' : 'A track to apply smoothing on.',
                'wsize' : 'The window size - Integer, floored if a float is given. Default = 11.',
                }

    def files(self):
        """
        Define which parameters will receive a list of files as pre-input.
        """
        return ['track']


    def process(self, **kw):
        """
        Define here the Operation itself with the parameters gathered form the form.
        """
        intrack = rp(kw, 'track')

        wsize = int(float(rp(kw, 'wsize', default=11)))

        vtrack = window_smoothing(intrack, wsize)
        out_path = tmp_path(prefix='%s' % (self.title()), suffix='.sql')
        vtrack.export(out_path)

        nf(self, out_path, ftype='track')

        return out_path

from tw import forms as twf
from tw.forms import validators as twv

class SmoothingForm(twf.TableForm):

    submit_text = 'Smooth'                                    # text of the submit button
    hover_help = True                                                  # show help_text with mouse onHover
    show_errors = True                                                 # show red labels when validators failed
    fields = [                                                         # define the fields you need in your form
        twf.HiddenField('_pp'),                                        # field needed to transfert information to the validation system
                                                                       # REQUIRED and don't modify it
        twf.HiddenField('key'),                                        # field needed to identify the service
                                                                       # REQUIRED and don't modify it
        twf.HiddenField('_up'),                                        # field needed to transfert user parameters if needed
                                                                       # REQUIRED you can pass some parameters needed by your application
                                                                       # in this field
        twf.SingleSelectField(id='track', label_text='File 1 : ',     # simple 'select' field with a custom validator
        help_text = 'Select the file to apply smoothing on',                          # you can customize your own
        validator=twv.NotEmpty()),
        twf.Spacer(),                                                  # a spacer between two field
        twf.InputField(label_text='Window size', id='wsize',                # a simple input field (with a simple validator)
        help_text = 'Select the window size'),
       ]
