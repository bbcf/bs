from joblauncher.lib.plugins.plugin import OperationPlugin, rp
from joblauncher.lib.plugins import form
from yapsy.IPlugin import IPlugin
from tw import forms as twf
from tg import tmpl_context


class Test(IPlugin, OperationPlugin):
    
    def title(self):
        return 'Test'
    
    def path(self):
        return ['Tests', 'test form']

    def output(self):
        return form.TestForm

    def description(self):
        return '''A test plugin'''

    def parameters(self):
        return {'one' : 'a simple input',
                'two' : 'a simple single select field',
                'three' : 'a random field'}

    def files(self):
        return ['two']

    def process(self, **kw):
        print 'process test with parameters : %s' % kw
        import time
        time.sleep(5)
        print 'end test process'
        return 1
