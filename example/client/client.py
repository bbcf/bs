from bottle import Bottle, run, static_file, view, request
import urllib, urllib2, json, os

# BioScript server url
bs_url = "http://sugar.epfl.ch/bs"
bs_op_path = bs_url + '/plugins?ordered=t' 
bs_form = bs_url + '/form/index'
shared_key = 'asharedkey'

# default application
app = Bottle()


# set default functions to this app for templates
from bottle import SimpleTemplate
SimpleTemplate.defaults["u"] = app.get_url


# SERVE STATIC FILES
@app.route('/static/<filename:path>', name='static')
def server_static(filename):
    return static_file(filename, root='static')



# THE HOME PAGE WITH OPERATIONS LIST
@app.route('/')
@view('home')
def home_display_operations_available():
    # two needed variable for bs javascript
    res = urllib2.urlopen(bs_op_path)
    return {'title' : 'Operations list', 'bs_url' : res.read(), 
            'bs_redirect' : app.get_url('/my_form_page')}

# THE PAGE WITH THE FORM
@app.route('/my_form_page')
@view('operation')
def my_form_page():
    operation_id = request.GET.get("id")
    if operation_id is None:
        raise Exception("There is no operation id");

    return {'title' : 'Operations', 'ifrsrc' : app.get_url('/operations') + '?id=' + operation_id}


# THE PAGE INSIDE THE IFRAME
@app.route('/operations')
def display_form():
    operation_id = request.GET.get("id")
    if operation_id is None:
        raise Exception("There is no operation id");
    

    # Prepare the request to send with the operation id
    # and the shared key to identify your service on BioScript
    req = {'id' : operation_id, 'key' : shared_key}


    # Add any private parameters to the request that 
    # BioScript will send you back with the callback
    # This is optionnal
    some_data = {'user_id' : 3}
    req['_up'] = {"data" : some_data }

    # Now prefill some parameter (Optionnal)
    # We want the user to select file we have in this client
    # application (in the samples directory).
    # So we will take care of `track` and `image` parameters.
    def get_file(fname):
        """
        from a file name `fname`, returns a tuple :
        (file path, file name)
        """
        return (app.get_url('static', filename='samples/%s' % fname), fname)

    prefill = {'image' : [get_file('sample.png'), get_file('sample.gif')],
     'track' : [get_file('sample.gff'), get_file('sample.wig'), get_file('sample.bed'), get_file('sample.fasta')]}
    req['prefill'] = json.dumps(prefill)
    # you can have a list of all parameters you can prefill on BioScript server at `vocab` method
    
    # send the request on bs service
    res = urllib2.urlopen(bs_form, urllib.urlencode(req))
    # serve the form as a response in your application
    return res
    




run(app, host='localhost', port=8080, reloader=True)
