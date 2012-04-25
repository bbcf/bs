from joblauncher.lib.plugins.plugin import OperationPlugin, rp
from joblauncher.lib.plugins import form
from yapsy.IPlugin import IPlugin
from tw import forms as twf
from tg import tmpl_context


class LongJob(IPlugin, OperationPlugin):
    
    def title(self):
        return 'Long Threshold'
    
    def path(self):
        return ['Manipulation', 'Thresholding', 'long one']

    def output(self):
        return form.ThresholdForm

    def description(self):
        return '''
        Apply a threshold on the track selected. Job is as long as the threshold is hight.
        '''
    def parameters(self):
        return {'thr' : 'the threshold to put. Required'}


    def process(self, **kw):
        import time
        time.sleep(float(rp(kw, 'thr', 5)))
        threshold = int(rp(kw, 'thr', 0))
        return 0





