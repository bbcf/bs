##################
BioScript Embedded
##################

`bs` can be embedded in a third party application that uses HTTP request. So any web application could use bs.

The purpose of such a thing is that you doesn't loose the user with a different interface in your application, or you don't redirect him on another website. 
Moreover you can, instead of letting the user choose some file on his filesystem, you can directly provide to bs the file that are in your service.
One other great advantage of bs in terms of computing power management is to run scripts from different applications on a dedicated machine with adapted features (available number of CPUs and memory). 

All you have to do is to design 3 HTTP controllers and insert 1 JS & 1 CSS file into your application.


''''''''''''''''''''''
Design the controller
''''''''''''''''''''''
bs new at least 3 HTTP routes to be functionnal:
 * Index : Where the user will go and see the list of operations availables
 * Get : Method that will fetch the operations 'form' from bs webserver
 * Validation : Method get called once a form is submitted & validated by bs webserver. 

You have an example of these 3 methods with the DevController in bs.controllers.dev.py.


'''''''''''''''''''''''
Javascript an CSS files
'''''''''''''''''''''''
 

bs.js & bs.css (under the bs.public directory) also need to be served by your application, as in the dev controller.
By default you just need to give some parameters to be fully functionnal:
For instance, you can add this at the end of your HTML file where you want to deploy bs operations::

    <script>
        window.onload = function(){
            var options = {
                'operation_list': ${oplist|n},
                'get_url': ${gurl|se,n},
                'validation_url': ${validation_url|se,n},
                'bs_server_url': ${bs_serv_url|se,n},
                'bs_form_container_selector': '#bs_form_container',
                'root_name' : 'Operations'
            }
            $('#bs_operations').bioscript(options).bioscript('operation_list');
        };
    </script>

Explanation
-----------
Tell bs to show the operations list under the HTML DOM element with the id 'bs_operations'. (JQuery selector)::
     
     $('#bs_operations').bioscript(options).bioscript('operation_list');

The options to give to bs::
    
    var options = {

The JSON you retrive by calling the list of plugins on bs webserver::
    
    'operation_list': ${oplist|n},

The "Index" route::
    
    'get_url': ${gurl|se,n},

The "validation" route::

    'validation_url': ${validation_url|se,n},
        
URl where bs webserver can be contacted::

    'bs_server_url': ${bs_serv_url|se,n},

Form will appears under this HTML DOM element::

    'bs_form_container_selector': '#bs_form_container',

The Display name::

    'root_name' : 'Operations'

.. note :: In order to be functionnal, bs javascript need JQuery (check the version `here <https://github.com/bbcf/bs/tree/master/bs/public/javascript/jslib>`_)

''''''''''
Overriding
''''''''''
If you don't want the 'default' functionnality, you can override some method to change the behaviour. You can have an example 
in the direct controller (bs.controllers.direct)::

    window.onload = function(){
        var options = {
            operation_list : ${oplist|n},
            show_plugin : function(plugin_id){
                window.location = ${serv|se,n} + 'direct/' + ${method|se,n}+ '?id=' + plugin_id;
            },
            'root_name' : 'Operations'
        }
        $('#bs_operations').bioscript(options).bioscript('operation_list');
    };

When the user click on an operation, the form will not appears, but the user will be redirected (window.location).
Use the method `show_plugin` to do that.


On the second page, you will also need to override a function::

    window.onload = function(){
        var options = {
            'bs_server_url' : ${bs_server_url|se,n},
            'validation_successful' : function(plugin_id, task_id){
                window.location = ${bs_server_url|se,n} + 'jobs?task_id=' + task_id;
            }
        };

        $('body').bioscript(options).bioscript('hack_submit');
    };

The user will be redirected after a successful validation of the form.
You need to tell bioscript to `hack` the default behaviour of the form to perform AJAX Cross browser requests::
     
     $('body').bioscript(options).bioscript('hack_submit');



''''''''''''''''''''
Register the service
''''''''''''''''''''
If you want to customize your access to bioscript (access to only a subset of operations, control how file are fetched from your service, ....) you can register the service in a bs configuration file.

In the root directory, there is a file called `services.ini` which define how a service have access to `bs`.
There is no restrictions by default, and a service have full access to `bs`.

If you want to configure your access, define your service::

    [GDV]
    contact = amail.contact@somewhere.ch   # a contact email (required)
    shared_key = 626dbfb70438367c01e1ee09bd4046b6cd0e6b6a  # a secret key to identify your service (required)
    
    # all others parameters are optionnals    
    callback.url = http://ptbbpc2.epfl.ch/pygdv/plugins/callback  # a url where `bs` can callback about jobs statuses

    # now, if your service & bs will be served and have access to the same filsystem
    # it is better for `bs` to fetch files from the filesystem than from an url.
    file.root = /absolute/path/of/some/shared/directory  # where files will be fetched from
    url.root = http://someserver.ch/something  # a url to reference a file
    result.root = //absolute/path/of/some/shared/directory  # where result files will be written

For instance, if you want to give a file to `bs` that have this path : /srv/files/projects/Rap1/coverage.bed, you don't want to give the full path of that file via a POST request, so you have defined the parameters::

   file.root = /srv/files/projects
   url.root = http://myserver.ch/somedata

You will give to `bs` the URL : http://myserver.ch/somedata/Rap1/coverage.bed and `bs` will know that it will have to fetch the file from /srv/files/projects/Rap1/coverage.bed instead of trying to fetch it from URL (it will not even try, so the url doesn't have to be valid).
