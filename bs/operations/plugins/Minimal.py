from bs.operations.base import OperationPlugin  # import the base class to build your plugin



# some information for the plugin
meta = {'version' : "1.0.0",
        'author' : "BBCF",
        'contact' : "webmaster-bbcf@epfl.ch"}

in_parameters = [
    {'id' : 'input', 'type' : 'text', 'required' : True},
    ]

out_parameters = [
    {'id' : 'output', 'type' : 'file'},
    ]


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



class Simple(OperationPlugin):

    info = plugin_information

    def __call__(self, **kw):
        text = kw.get('input', '')       # get the parameter back

        path = self.temporary_path()     # get a temporary path
        with open(path, 'w') as f:            # open a file & write the input
            f.write(text)
        self.new_file(path, 'output')     # add a file to the result

        return 1

