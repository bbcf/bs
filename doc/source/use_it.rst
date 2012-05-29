######
How to
######

'''''''''''
Description
'''''''''''

Several methods are callable to access the application.
They are all accessible via the *form* controller. It means that if your application
is served on ``http://localhost:8080``, all following methods will be accessible at
``http://localhost:8080/form``

**N.B** : all following methods can be viewed directly in JSON. (Just add ``.json`` after the method name)

'''''''
Methods
'''''''


- **methods** : Get a list of methods to use, formatted in a JSON way .

    .. note :: http://localhost:8080/form/methods.json

- **info** : Get documentation and parameters needed for a specific method. You must give the *id* of the method as a parameter.

    .. note:: http://localhost:8080/form/info?id=dd2f5c97a48ab83caa5618a3a8898c54205c91b5 or in `JSON`
              http://localhost:8080/form/info.json?id=dd2f5c97a48ab83caa5618a3a8898c54205c91b5

- **index** : The form to display in your application.

    .. note:: http://localhost:8080/form/index?id=dd2f5c97a48ab83caa5618a3a8898c54205c91b5


The ``index`` method display the form, and you can call it in an ``iframe`` in your application.
The form displayed is the one that you defined in your plugin (see :ref:`plugins`).


''''''''''''''
Initialization
''''''''''''''

In order to use *joblauncher* by your service, you must define it in
``service.ini`` file in joblauncher source folder

Here an example, add it at the end of the file::

    # Define here services allowed to process request on joblauncher
    # Available parameters are :
    # REQUIRED
    #     - contact : an email of contact
    #     - shared_key : a key which identify the service
    # OPTIONAL
    #     - file.root : absolute path to get the file on the filesystem
    # 	    (joblauncher must be installed on the same server as the service)
    #     - url.root : the part of the url given to fetch the file to replace with file_root
    #     - result.root : absolute path where to write results
    #     - operations : the list of plugins to get for the service (default = all)

    [MYSERVICE]
    contact = yohan.jarosz@epfl.ch
    shared_key = asharedkeydifficulkttoguess
    file.root = /srv/data/files/
    url.root = http://localhost:8080/myservice
    result.root = /srv/data/files/job_results/
    callback.url = http://localhost:8080/callback
    operations = ['operationid1', 'operationid2', ...]

In order to help you define what operations identifiers to put in the `operations` parameter, *joblauncher* (on restart)
produce a file called *service.cfg* in the application root directory which list all operations identifiers with the
operation title and description. e.g ::

    [help]
    66d69b6b6bc3fe7539d7391dbb24ca1e4bdea196 = long threshold : Apply a threshold on the track selected.
    dd2f5c97a48ab83caa5618a3a8898c54205c91b5 = merge : It is just an example.

    [main]
    66d69b6b6bc3fe7539d7391dbb24ca1e4bdea196 = []
    dd2f5c97a48ab83caa5618a3a8898c54205c91b5 = ['track_1', 'track_2']

Look at the `[help]` section and the keys are the operations identifiers you have to put in your service
definition

''''''''''
Discussion
''''''''''
Discussion with *joblauncher* is all about ``HTTP``and ``JSON`` requests/responses.

Following examples will be given in python but you can always implement it in any languages that provides HTTP handling.

Following examples will take the example of ``myservice`` which is defined in the previous paragraph.

Following examples will assume that ``myservice`` and ``joblauncher`` runs on the same server but on different ports :
myservice on *8080* and joblauncher on *7520* for instance.


Methods
'''''''
You will get the list of methods that you have allowed by calling the *methods* method on the webserver. It will give you this JSON ::

    {"key" : Operations, "childs":
        [{"key" : "Manipulation", "childs":
                                    [{"key" : "Threshold", "id": "66d69b6b6bc3fe7539d7391dbb24ca1e4bdea196", "fl": []},
                                     {"key": "Merge", "id": "dd2f5c97a48ab83caa5618a3a8898c54205c91b5",  "fl": ["track_1", "track_2"]}]

        }]
    }

It make a hierarchy of operations, each node is labelled by the `key` parameter
and all leaves contains the `id` and `fl` which are the operation id and the parameters
in the operation form to fill with files.

So you can make nice buttons in javascript to call your appliction from this JSON.
It will be provided soon as part of the joblauncher library.


Index
'''''
You are here in a webserver controller method that can be called by your application. Here,
this method is called with an *operation_id* (identify the operation) and the *user_id* (identify the user)::




    def index(self, operation_id, files_params, user_id):
        """
        Some fictive method that serve the joblauncher form.
        """
        # take the joblauncher url from configuration file
        joblauncher_url = 'http://localhost:7520/'

        # take the shared_key from confuguration file
        shared_key = 'asharedkeydifficulttoguess'

        # prepare the request to send with the operation id
        # and the shared key to identify your service
        req = {'id' : operation_id, 'key' : shared_key}


        # add private parameters to the request that you will need after
        someData = database.get_some_data_from_user_id(user_id)
        req['_up'] = {"user_id" : user_id, "data" : someData }

        # add files in the form from the JSON `fl` params (here files_param).
        # [_f.name, f.http_link] will permit to show the file name in the form
        # but pass the http link of the file in the methods.
        # The http link (url.root) can be replaced with the file.root if you defined it in the
        # service.ini file.
        if len(json.loads(files_params)) > 0:
            gen_files = [[_f.name, _f.http_link] for _f in database.get_files_from_user_id(user_id)]
            for param in json.loads(files_param):
                req[param]= json.dumps(gen_files)

        # send the request on joblauncher service
        res = urllib2.urlopen(joblauncher_url, urllib.urlencode(req))

        # serve the form as a response in your application
        return res.read()


Callback
''''''''
Another important method is about *callback*. If you have defined ``callback.url`` in
the *service.ini* file. With this example, *joblauncher* will callback *http://localhost:8080/myservice/callback*::

    def callback(self, user_id, data, fid, tid, st, tn, td, **kw):
        # This method is called with some private parameters that you
        # passed in the '_up' parameters in the request. Here user_id and data

        do_something(user_id, data)

        # Other following parameters are defined below

        do_other(fid, tid, st, tn. td)

        # Other actions depending on the status
        if st == 'RUNNING':
            database.set_my_operation(id=tid, launched=True)

        elif st == 'ERROR':
            database.set_my_operation(id=tid, finished=True, with_error=True, error=kw.get('error'))

        elif st == 'SUCCESS':
            database.set_my_operation(id=tid, finished=True, with_error=False, result=kw.get('result'))


- *fid* : the operation identifier (or form identifier)
- *tid* : the task identifier that identify the job launched on joblauncher
- *st* : the status of the task. Can be
         ``RUNNING``,
         ``SUCCESS`` (you can retrieve the job result with ``kw.get('result')``) or
         ``ERROR`` (retrieve the error with ``kw.get('error')``)
- *tn* : the operation name (can be used to display something understandable for users)
- *td* : the operation description.

