Description

====================

TurboTequila is a Turbogears application with Tequila enabled.



First use

=====================

Download the project :



    $ git clone git://github.com/bbcf/joblauncher.git



(It will create a directory named `joblauncher`)



So you want to use another name for your project, like `myCoolProject`.



    $ cd joblauncher

    $ python init_project.py myCoolProject

    $ cd ..

    $ cd mycoolproject



Now as you will work on a python environment I suggest you to use [virtualenv](http://example.net) and the [wrapper](http://www.doughellmann.com/projects/virtualenvwrapper).

It will create an isolated environment for your project. (You may want to skip this step).



Once your are in the right environment:



    $ easy_install -i http://tg.gy/215 tg.devtools

    $ python setup.py develop

    $ paster setup-app development.ini

    $ mv who.ini.sample who.ini

    $ paster serve --reload development.ini



These lines will:

    

    * install the turbogears development tools

    * install the libraries needed by joblauncher

    * setup the database

    * move the authentication sample file to the right name (You MUST edit this file)

    * serve the application on localhost:8080 by default





Enjoy ;)





 This code was written by the BBCF

 http://bbcf.epfl.ch/              

 webmaster.bbcf@epfl.ch            



