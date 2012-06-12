.. _plugins:

#######
Plugins
#######

It uses `Yapsy <http://yapsy.sourceforge.net/>`_ plugin system to automatically add new *Operations* on the interface.

'''''''''''''''
Add your plugin
'''''''''''''''

Make a python class :class:`Test.py`::

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





Make the corresponding ``yapsy`` file :class:`ExampleFilesSelection.yapsy-plugin`::

    [Core]
    Name = Test
    Module = Test

    [Documentation]
    Author = Jarosz Yohan
    Version = 1.0.0
    Website = http://github.com/yjarosz
    Description = Test plugin to put a threshold on a track


This one is used to describe your plugin and to tell ``Yapsy`` which plugin to take.


Put both file in the ``plugins`` directory. The new operation should appears on your server.


'''''
Forms
'''''

Forms can be build with `Toscawidgets <http://toscawidgets.org/>`_, `FormEncode <http://www.formencode.org/>`_ or `Sprox <http://sprox.org/>`_.
Here an example with Toscawidget : :class:`ExampleFilesSelection.py`::

    from tw import forms as twf
    from tw.forms import validators as twv

    class FilesForm(twf.TableForm):

        submit_text = 'Merge the files'                                    # text of the submit button

        hover_help = True                                                  # show help_text with mouse onHover

        show_errors = True                                                 # show red labels when validators failed

        fields = [                                                         # define the fields you need in your form

            twf.HiddenField('_pp'),                                        # field needed to transfert information to the validation system
                                                                           # REQUIRED and don't modify it

            twf.HiddenField('_up'),                                        # field needed to transfert user parameters if needed
                                                                           # REQUIRED you can pass some parameters needed by your application
                                                                           # in this field

            twf.SingleSelectField(id='track_1', label_text='File 1 : ',    # simple 'select' field with a simple validator
                help_text = 'Select the first file',                       # you can customize your own
                                  validator=twv.NotEmpty()),

            twf.Spacer(),                                                  # a spacer between two field

            twf.SingleSelectField(id='track_2', label_text='File 2 : ',    # simple 'select' field with a simple validator
                help_text = 'Select the second file',
                validator=twv.NotEmpty()),

            twf.TextField(label_text='Threshold', id='thr',                # a simple input field (with a simple validator)
                help_text = 'Input the trhreshold here', validator=twv.NotEmpty()),
               ]







