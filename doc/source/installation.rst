############
Installation
############

.. note:: This is a draft. Installation steps are a bit complicated at the moment, and should reduce to just a few steps.

'''''''''''''''''
Full installation
'''''''''''''''''

Install RabbitMQ
Edit conf scripts (celeryconfig.py, dev.ini. setup.ini, workerctl, webserverctl)

Start the rabbitMQ server::

    sudo rabbitmq-server --detached

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

    paster setup-app setup.ini

Run the application

    paster serve --reload dev.ini

Then start the worker(s)::

    celeryd --loglevel=DEBUG


''''''''''''''''''''
Plugins installation
''''''''''''''''''''

This installation is to use Operations provided by Bioscript without using the graphical interface.

To install you should download the latest source code from GitHub, either by going to the `web repository <http://github.com/bbcf/plugins/>`_
and clicking on "Downloads", or by cloning the git repository with::

    git clone https://github.com/bbcf/plugins.git

Install the library::

    easy_install plugins

Verify that's working::

    python
    >>> from bs.plugins.Test import Test
    >>> Test()()




