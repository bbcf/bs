############
Installation
############



''''''''''''
Installation
''''''''''''

To install you should download the latest source code from GitHub, either by going to the `web repository <http://github.com/bbcf/bs/>`_
and clicking on "Downloads", or by cloning the git repository with::

    git clone https://github.com/bbcf/bs.git

Once you have the source code, and on the right python environment (virtualenv) run::

    easy_install -i http://tg.gy/220 tg.devtools
    cd bs
    python setup.py develop

Then setup the application (build thee database)

    paster setup-app development.ini

Run the application (serveed on localhost:8081 by default)

    paster serve --reload development.ini

Then start the worker(s)::

    celeryd --loglevel=DEBUG


'''''''''''''
Customization
'''''''''''''

Webserver onfiguration can be found in 'development.ini' file.

Worker configuration is under 'celeryconfig.py' file.

By default, bs use SQlite as pricipal backend & message broker. if you want to use other:

    - webserver & worker backends can be changed to any backend supported by SQLalchemy.
    - Message broker : can be upgraded with any message broker supported by Celery.




