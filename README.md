Description
====================
JobLauncher is a web application which have the purpose to build a common interface for job processing.
It is accessible from command line and from forms, and allows you to easily add your own methods.

Features
====================

    * plugins : it uses plugins to automatically add methods to the interface (uses [yapsy](http://yapsy.sourceforge.net/)).
    * forms : form are build using [toscawidget](http://www.toscawidgets.org/).
    * interface/controllers : build with [turbogears](http://turbogears.org/) is easy to change.
    * database : Several backend can be configured as joblauncher use [SQLalchemy](http://www.sqlalchemy.org/) such as mysql, sqlite, pgsql, oracle, ... 
    * processing : uses [celery](http://celeryproject.org/) which make job processing highly configurable.
    * messaging : amqp(http://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol) messaging is used between the interface and the worker with [rabbitmq](http://www.rabbitmq.com/) that make it easy to bput your applications running on differents server.
    

More documentation is comming

Enjoy ;)

 This code was written by the BBCF
 http://bbcf.epfl.ch/              
 webmaster.bbcf@epfl.ch            
