##################
BioScript Embedded
##################

`bs` can without to much work be embedded in a third party application. We call it a service.

As so, a service can provide it's own files to the `bs` system.


bs application itself is embedded. Direct access is provided by the `direct` controller. To
do the same in your service, you must reproduce the methods that are in this controller.

Your service will need also to serve a javascript file : `bs.js` that is located under `javascript` under the `public` directory.

`bs` also need latest javascript from jquery.


''''''''''''''''''''
Register the service
''''''''''''''''''''

In the root directory, there is a file called `services.ini` which define how a service have access to `bs`.
There is no restrictions by default, and a service have full access to `bs`.

If you want to configure your access, define your service :

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

For instance, if you want to give a file to `bs` that have this path : /srv/files/projects/Rap1/coverage.bed, you don't want to give the full path of that file via a POST request, so you have defined the parameters :

   file.root = /srv/files/projects
   url.root = http://myserver.ch/somedata

You will give to `bs` the URL : http://myserver.ch/somedata/Rap1/coverage.bed and `bs` will know that it will have to fetch the file from /srv/files/projects/Rap1/coverage.bed instead of trying to fetch it from URL (it will not even try, so the url doesn't have to be valid).


''''''''''
Index page
''''''''''
This is a page on your application where you want to display `bs` operations.

Serve two javascript files :

<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
<script type="text/javascript" src="${tg.url('/javascript/bs.js')}"></script>
 and one CSS file :

<link href="/css/bs.css" media="screen" type="text/css" rel="stylesheet">

Put in your HTML file a div where the available operations will be displayed and remember the id


=> display operations
Call some javascript to display the operations.
    <script>
        window.onload = function(){
            var options = {
                show_plugin : function(plugin_id){
                    window.location = 'http://myserver.ch/plugin?id=' + plugin_id;  # when the user click on this button
                                                                                    # he will be redirected on that url
                },
                'root_name' : 'Operations'                                         
            }
            $('#bs_operations').bioscript(options).bioscript('operation_list');    # call this to initialize the rendering of
                                                                                   # the operations
        };
    </script>

get the operation list back
 bs_url = bs_server_url + 'plugins?ordered=true'
        # get the operation list back
        operation_list = urllib2.urlopen(bs_url).read()




=> TARGET FROM OPERATION CLICK
''''''
Plugin
''''''
 req['_up']
  req['key']
   req['prefill']
=> serve bs javascript


=> hack submit
var options = {
            'bs_server_url' : ${bs_server_url|se,n},
            'validation_successful' : function(plugin_id, task_id){
                window.location = ${bs_server_url|se,n} + 'jobs?task_id=' + task_id;
            }
        };

        $('body').bioscript(options).bioscript('hack_submit');


