import sys









try:

    from setuptools import setup, find_packages

except ImportError:

    from ez_setup import use_setuptools

    use_setuptools()

    from setuptools import setup, find_packages



testpkgs=['WebTest >= 1.2.3',

               'nose',

               'coverage',

               'wsgiref',

               'repoze.who-testutil >= 1.0.1',

               ]

install_requires=[

    "TurboGears2 >= 2.1.5",

    "Genshi",

    "zope.sqlalchemy >= 0.4",

    "repoze.tm2 >= 1.0a5",

    "sqlalchemy",

    "sqlalchemy-migrate",

    "repoze.what-quickstart",

    "repoze.what >= 1.0.8",

    "repoze.what-quickstart",

    "repoze.who-friendlyform >= 1.0.4",

    "repoze.what-pylons >= 1.0",

    "repoze.what.plugins.sql",

    "repoze.who==1.0.19",

    "tgext.admin >= 0.3.9",

    "tw.forms",

    "tg.devtools",

    "tw.dojo",

    "tw.dynforms",

       

    ]



if sys.version_info[:2] == (2,4):

    testpkgs.extend(['hashlib', 'pysqlite'])

    install_requires.extend(['hashlib', 'pysqlite'])



print install_requires



setup(

    name='joblauncher',

    version='0.1',

    description='A turbogears system with Tequila enabled',

    author='Yohan Jarosz',

    author_email='yohan.jarosz@epfl.ch',

    #url='',

    setup_requires=["PasteScript >= 1.7"],

    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],

    packages=find_packages(exclude=['ez_setup']),

    install_requires=install_requires,

    include_package_data=True,

    test_suite='nose.collector',

    tests_require=testpkgs,

    package_data={'joblauncher': ['i18n/*/LC_MESSAGES/*.mo',

                                 'templates/*/*',

                                 'public/*/*']},

    message_extractors={'joblauncher': [

            ('**.py', 'python', None),

            ('templates/**.html', 'genshi', None),

            ('public/**', 'ignore', None)]},



    entry_points="""

    [paste.app_factory]

    main = joblauncher.config.middleware:make_app



    [paste.app_install]

    main = pylons.util:PylonsInstaller

    """,

    dependency_links=[

        "http://tg.gy/215/"

        ],

    zip_safe=False

)

