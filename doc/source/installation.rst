############
Installation
############

.. note:: This is a draft. Installation steps are a bit complicated at the moment, and should reduce to just a few steps.

'''''''''''''''''
Full installation
'''''''''''''''''

To install you should download the latest source code from GitHub, either by going to the `web repository <http://github.com/bbcf/bs/>`_
and clicking on "Downloads", or by cloning the git repository with::

    git clone https://github.com/bbcf/bs.git

Once you have the source code, and on the right python environment (virtualenv) run::

    cd bs
    easy_install -i http://tg.gy/215 tg.devtools
    easy_install -U zope.interface
    python setup.py install
    python yapsy_patch.py


Then setup the application

    paster setup-app development.ini

Run the application

    paster serve --reload development.ini

Then start the worker(s)::

    celeryd --loglevel=DEBUG


'''''''''''''
Customization
'''''''''''''


Many parameters are customzable in BioScript :

    - Database backend : can be changed to any backend supported by SQLalchemy.
    - Worker backend : the same.
    - Message broker : can be upgraded with any message broker supported by Celery.




