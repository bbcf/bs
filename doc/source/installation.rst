############
Installation
############
''''''''
Download
''''''''

To install you should download the latest source code from GitHub, either by going to the `web repository <http://github.com/bbcf/joblauncher/>`_
and clicking on "Downloads", or by cloning the git repository with::

    git clone https://github.com/bbcf/joblauncher.git

Once you have the source code, run::

    cd joblauncher
    sudo python setup.py install

'''''''''''''
Configuration
'''''''''''''

You have to edit some file to configure joblaucher on your server(s)

- **development.ini** : define the main application (you should rename this file).
- **celeryconfig.py** : define the configuration of the worker.

And additional configuration is needed for the messaging system : RabbitMQ (refers to the `rabbit MQ documentation <http://www.rabbitmq.com/documentation.html>`_)

''''''
Launch
''''''
Put your shell in the right environment::

    workon joblauncher


Start the main application via a daemon or run::

    paster serve development.ini

Start the rabbitMQ server::

    sudo rabbitmq-server --detached


Then start the worker(s)::

    celeryd --loglevel=DEBUG

