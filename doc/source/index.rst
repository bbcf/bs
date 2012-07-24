=====================================
*'bs'* documentation
=====================================

JobLauncher is a web application which have the purpose to build a common interface for job processing for different applications.

If you want to add new operations on the interface, you should go `here <http://bbcf.epfl.ch/plugins/>`_.

========
Features
========

- *Plugins* : It uses `Yapsy <http://yapsy.sourceforge.net/>`_ plugin system to automatically add new *Operations* on the interface.

- *Forms* : Forms build with `Toscawidgets <http://toscawidgets.org/>`_ are highly configurable.

- *Interface/controllers* : Powered by `Turbogears <turbogears.org/>`_.

- *Database backend* : Several backend can be configurated to fit your will : see `SQLAlchemy <http://www.sqlalchemy.org/>`_.

- *Processing* : Use `Celery <http://celeryproject.org/>`_ which allow great configuration on how jobs are processed.

- *Messaging* : `AMQP <http://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol>`_ is used between the interface and the worker(s).


Implementation of this protocol is supplied with `RabbitMQ <http://www.rabbitmq.com/>`_.



=================
Table of contents
=================
.. toctree::
    :maxdepth: 3

    Installation <installation>
    How To <use_it>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
