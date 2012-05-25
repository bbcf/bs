.. _plugins:

#######
Plugins
#######

It uses `Yapsy <http://yapsy.sourceforge.net/>`_ plugin system to automatically add new *Operations* on the interface.

'''''''''''''''
Add your plugin
'''''''''''''''

Make a python class :class:`ExampleFilesSelection.py`::

       from joblauncher.lib.plugins.plugin import OperationPlugin, rp, nf
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
       Import here other libraries that you need
       """


       class ExampleFilesSelection(IPlugin, OperationPlugin):

           def title(self):
               """
               Define the Operation title.
               """
               return 'Merge'

           def path(self):
               """
               Define the Operation path. Must be unique among all others operations.
               """
               return ['Manipulation', 'Merge']

           def output(self):
               """
               Define what form will be used.
               """
               return form.FilesForm

           def description(self):
               """
               Document your Operation.
               """
               return '''It is just an example.'''
           def parameters(self):
               """
               Define the parameters needed by your Operation.
               """
               return {'track_1' : 'The first file. Required', 'track_2' : 'The second file. Required', 'thr' : 'a threshold.'}

           def files(self):
               '''
               Here give the parameters that need to be filled with a list of files
               '''
               return ['track_1', 'track_2']

           def process(self, **kw):
               """
               Define here the Operation itself with the parameters gathered form the form.
               """
               file_1 = rp(kw, 'track_1')                    # retrieve parameter `track_1`
               file_2 = rp(kw, 'track_2')                    # rp `track_2`
               threshold = int(rp(kw, 'thr'))                # rp `thr` and convert it to an int

               root, fname = os.path.split(file_1)           # simulated process
               nfile = os.path.join(root, 'new_file.bed')    # take the first file and
               shutil.move(file_1, nfile)                    # rename it to 'new_file.bed'

               nf(self, nfile)                               # add a new file in the job result
                                                             # nf(plugin, file) will add the file
                                                             # to the output of the job.
                                                             # the file can be retrieved by your service after.

               return 'example terminated'                   # the Operation return value






Make the corresponding ``yapsy`` file :class:`ExampleFilesSelection.yapsy-plugin`::

    [Core]
    Name = ExampleFilesSelection
    Module = ExampleFilesSelection

    [Documentation]
    Author = Jarosz Yohan
    Version = 0.1
    Website = http://github.com/yjarosz
    Description = Test plugin to select files on a form and fetch them in your service.

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







