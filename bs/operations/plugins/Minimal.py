from bs.operations.base import OperationPlugin  # import the base class to build your plugin



# some information for the plugin
meta = {'version' : "1.0.0",
        'author' : "BBCF",
        'contact' : "webmaster-bbcf@epfl.ch"}

in_parameters = [
    {'id' : 'param_one_text', 'type' : 'text'},
    {'id' : 'param_two_numeric', 'type' : 'int'},
    {'id' : 'param_three_boolean', 'type' : 'boolean'},
    {'id' : 'param_four_file' , 'type' : 'file', 'required' : True},
    {'id' : 'param_five_file', 'type' : 'file', 'multiple' : True},
    ]

out_parameters = []


plugin_information = {
    'title' : 'Test',                             # The title of your operation
    'description' : 'A minimal example',          # Describe the operation's goal
    'path' : ['Tests', 'Examples', 'Minimal'],    # Under which category the operation will be set
                                                  # Must be unique among all plugins
                                                  # First in the list mean higher category
    'in' : in_parameters,                         # All input parameters
    'out' : out_parameters,                       # All output parameters
    'meta' : meta,                                # Meta information (authors, version, ...)
    }



temporary_path = lambda x : x



# a method
def my_method(**kw):
    print 'my method received %s ' % kw
    return 1




class Simple(OperationPlugin):

    info = plugin_information

    def __call__(self, **kw):
        return my_method(**kw)

