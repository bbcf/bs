##################
Plugin development
##################


If you want to contribute, please fork (or clone) the `github repository <https://github.com/bbcf/bs.operations>`_.
It contains every single plugin that is developed.

You will find examples in *Example.py* & *Example_with_form.py*.


'''''''''''''''
Develop locally
'''''''''''''''

You may want to test your plugin before proposing your own plugin.
If so please install bs locally and set the parameter *plugins.update* to 'False' in the
development.ini file.

Then put your plugin under 'bs.operations.plugins' in the webserver app; it should automatically appear after a 'restart'.




''''''''''''''''''''''''''
Develop on BBCF dev server
''''''''''''''''''''''''''

There is a development version available on a `bbcf server <https://github.com/bbcf/bs.operations>`_.
This version is available for people working with the BBCF.
Please `contact <mailto:webmaster.bbcf@epfl.ch>`_ the BBCF if you want to test your plugin there.
