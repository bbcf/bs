# import from bs library
from bs.operations.base import OperationPlugin, BaseForm
# import toscawidget2 modules in order to build forms
import tw2.forms as twf
import tw2.core as twc




class TestForm(BaseForm):
    # the parameter 'one' : a single select field. Required
    one = twf.SingleSelectField(validator=twc.Required)

    # the parameters 'two' : a multiple select field. Not required
    two = twf.MultipleSelectField(validator=twc.Required)

    # the parameter three : an text input. Required
    three = twf.TextField(label='a label : ', help_text='Some description.', hover_help=True,
        validator=twc.Validator(required=True))

    # the submit button
    submit = twf.SubmitButton(id="submit", value="Submit test job")




# some information for the plugin
meta = {'version' : "1.0.0",
        'author' : "BBCF",
        'contact' : "webmaster-bbcf@epfl.ch"}

in_parameters = [{'id' : 'one', 'type' : 'track'}, {'id' : 'two', 'type' : 'track', 'multiple' : True}, {'id' : 'three', 'type' : 'text'}]

out_parameters = [{'id' : 'result', 'type' : 'png'}, {'id' : 'result2', 'type' : 'track'}, {'id' : 'result3', 'type' : 'pdf'}]

temporary_path = lambda x : x

class Test(OperationPlugin):

    # INFORMATION ABOUT THE PLUGIN
    info = {
        'title' : 'Test',                                 # The title of your operation
        'description' : 'A plugin for testing purposes',  # Describe the operation's goal
        'path' : ['Tests', 'Examples', 'Simple test'],    # Under which category the operation will be set
                                                          # Must be unique among all plugins
                                                          # First in the list mean higher category
        'output' : TestForm,                              # The operation 's graphical output
        'in' : in_parameters,                             # All input parameters
        'out' : out_parameters,                           # All output parameters
        'meta' : meta,                                    # Meta information (authors, version, ...)
        }


    # OPERATION PROCESS
    def __call__(self, **kw):

        # get parameters
        param_one = kw.get('one', None)
        param_two = kw.get('two', None)
        param_three = kw.get('three', None)

        # if you need file to write in, you should use 'temporary_path' method
        tmp = temporary_path(fname='track', ext='sql')


        with open(tmp, 'w') as fout:           # open the file in write mode
            with open(param_one, 'rb') as fin: # open the file in read mode
                while True :                   # write the file with nothing unchanged
                    chunk = fin.read(2048)
                    if not chunk : break
                    fout.write(chunk)

        # create some other files
        tmp2 = temporary_path(fname='other', ext='.wig')
        tmp3 = temporary_path(fname='image', ext='pdf')

        # You need to add files to the output
        self.new_file(tmp, 'result')
        self.new_file(tmp2, 'result2')
        self.new_file(tmp3, 'result3')

        # return 1 to say that it's ok
        return 1

