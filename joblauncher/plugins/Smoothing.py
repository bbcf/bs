from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf, temporary_path, BaseForm
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
        return {'in' : ['track', 'wsize'],
                'out' : {'fresult' : 'track'},
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

        out_path = temporary_path(self.title(), ext='.sql')
        vtrack.export(out_path)
        nf(self, out_path, 'fresult')

        return out_path

import tw2.forms as twf

class SmoothingForm(BaseForm):

        track = twf.SingleSelectField(label_text='Select the file ',
            help_text = 'Select the file to apply smoothing on')
        wsize = twf.TextField(label_text='Window size',
        help_text = 'Select the window size')

        submit = twf.SubmitButton(id="submit", value="Smooth")

