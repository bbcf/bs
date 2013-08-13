from __future__ import absolute_import
from celery.task import task
from celery.task.http import URL

from bs.lib import operations, util
import os
import tg
import urllib
import urllib2
try:
    import simplejson as json
except ImportError:
    import json
import errno
import shutil
from bs.lib import io
from celery import Celery

from celery import current_app

ROOT_DIRECTORY = os.path.dirname(__file__)
TMP_DIR = tg.config.get('root.directory')
if not TMP_DIR:
    TMP_DIR = os.path.normpath(os.path.join(ROOT_DIRECTORY, os.path.pardir, 'tmp'))

if 'ROOT_DIRECTORY' in current_app.conf:
    ROOT_DIRECTORY = current_app.conf['ROOT_DIRECTORY']
    TMP_DIR = os.path.normpath(os.path.join(ROOT_DIRECTORY, 'tmp'))

print '[x] temporary data path is %s' % TMP_DIR

DEBUG_PLUGINS = True





def shutilerror(func, path, einfo):
    print '[shutil error] with %s. On path %s' % (func, path)
    util.print_traceback()


def check_data_paths():
    if not os.path.exists(ROOT_DIRECTORY):
        print "Directory '%s' does not exist: trying to create it..." % ROOT_DIRECTORY
        os.mkdir(ROOT_DIRECTORY)
        print 'ok'
    if not os.path.exists(TMP_DIR):
        print "Directory '%s' does not exist: trying to create it..." % TMP_DIR
        os.mkdir(TMP_DIR)
        print 'ok'

check_data_paths()

DEBUG_LEVEL = 1


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[tasks] %s%s' % ('\t' * t, s)


@task
def delete_task_results(dirpath, bs_path):
    if file_is_in_bs(bs_path, dirpath):
        shutil.rmtree(dirpath, ignore_errors=True)


def file_is_in_bs(bs_path, filepath):
    bs_path = os.path.normpath(bs_path)
    filepath = os.path.normpath(filepath)
    return filepath.startswith(bs_path)


@task(track_started=True)
def testtask(x=10):
    import time
    try:
        x = int(x)
    except ValueError:
        x = 10
    time.sleep(x)
    return 1

from celery import current_task

@task()
def fetchfiles(error=False, t=2):
    print 'fetchingfiles'
    import time
    time.sleep(10)
    result = {}
    if error:
        result['error'] = 'Error while fetching files'
        return result
    return {'fetched' : ['pathone', 'pathto', 'blabla']}


@task()
def pluginprocess(fetchedfiles, error=False, t=2):
    if 'error' in fetchedfiles:
        raise Exception(fetchedfiles['error'])
    print 'plugin process'
    print 'got fetched files : %s' % fetchedfiles
    
    import time
    time.sleep(10)
    if error:
        raise Exception('Error while computing')
    return 1

from bs.lib.filemanager import fetchurls
@task()
def fetch_files(user, plug, **kw):
    # fetch files if any
    debug('fetching files ...', 2)
    debug(kw, 3)
    inputs_directory = ''
    try:
        inputs_directory = fetchurls(user, plug, kw)
    except Exception as e:
        return {'error': 'error while fetching files : ' + str(e)}
        debug('Failed to fetch inputs', 3)
    return {'inputs_dir' : inputs_directory}



@task()
def plugin_job(user, plug, inputs_directory, outputs_directory, dwdfiles, plugin_info,
               user_parameters, service_callback, bioscript_callback, **form_parameters):


    # FETCHING FILES
    current_task.update_state(state='FETCHING FILES')
    inputs_directory = fetchurls(user, plug, dwdfiles, inputs_directory, form_parameters)


    # PLUGIN PROCESS
    current_task.update_state(state='STARTED')
    try:
        try:
            user_parameters = json.loads(user_parameters)
        except TypeError:
            pass
        task_id = plugin_job.request.id

        if service_callback is not None:
            callback_service(service_callback, plugin_info['generated_id'], task_id, 'RUNNING', additional=user_parameters)

        debug('task launched user.name: %s, indir: %s, oudir: %s' % (user.name, inputs_directory, outputs_directory))
        # get plugin class
        plugin = operations.get_plugin_byId(plugin_info['generated_id'])
        if plugin is None:
            raise Exception('Plugin not found by the worker.')
        plugin.is_debug = DEBUG_PLUGINS

        debug('plugin operation start')
        plugin._start_timer()
        results = []
        # call plugin with form parameters
        try:
            ret = plugin(**form_parameters)
            results = [{'is_file': False,
                        'value': ret}]
        except Exception as e:
            debug("ERROR")
            if service_callback is not None:
                user_parameters.update({'error': e})
                callback_service(service_callback, plugin_info['generated_id'], task_id, 'FAILED', additional=user_parameters)
            # deleting plugin temporary files
            for todel in plugin.tmp_files:
                debug('deleting %s' % todel)
                shutil.rmtree(todel, onerror=shutilerror)
            #debug('deleting %s' % outputs_directory)
            #shutil.rmtree(outputs_directory, onerror=shutilerror)
            if file_is_in_bs(TMP_DIR, inputs_directory):
                debug('deleting %s' % inputs_directory)
                shutil.rmtree(inputs_directory, onerror=shutilerror)

            if len(plugin.debug_stack) > 0:
                debug("Adding debug stack to error")
                debug_error = '\n [x] DEBUG STACK : %s' % '\n'.join([d for d in plugin.debug_stack])
                if not e.args:
                    e.args = ('',)
                e.args = (e.args[0] + debug_error,) + e.args[1:]
            raise

        # mkdir output directory
        out = os.path.join(outputs_directory, task_id)
        debug('mkdir out path : %s' % out)
        try:
            os.mkdir(out)
        except OSError, e:
            if e.errno == errno.EEXIST:
                io.rm(out)
                os.mkdir(out)
        debug('moving files')
        # moving files to the output directory
        for output_file, output_type in plugin.output_files:
            debug('f: %s' % output_file, 1)
            out_path = os.path.join(out, os.path.split(output_file)[1])
            io.mv(output_file, out)
            results.append({'is_file': True, 'path': out_path, 'type': output_type})

        # deleting plugin temporary files
        for todel in plugin.tmp_files:
            debug('deleting %s' % todel)
            shutil.rmtree(todel, onerror=shutilerror)
        if file_is_in_bs(TMP_DIR, inputs_directory):
                debug('deleting %s' % inputs_directory)
                shutil.rmtree(inputs_directory, onerror=shutilerror)

        # updating bioscript with the results
        URL(bioscript_callback).get_async(task_id=task_id, results=json.dumps(results))

        # callback
        if service_callback is not None:
            callback_service(service_callback, plugin_info['generated_id'], task_id, 'SUCCESS',
                results=json.dumps(results), additional=user_parameters)
    except Exception as e:
        if service_callback is not None:
                callback_service(service_callback, plugin_info['generated_id'], task_id, 'FAILED', additional=e.message)
        raise
# @task()
# def plugin_process(_id, service_name, tmp_dir, out_path, name, description, callback_url=None, **kw):
#     """
#     Method which retrieve the plugin by it's id and launch the processing steps (pre/process/post)
#     """
#     task_id = plugin_process.request.id

#     user_parameters = json.loads(kw.get('_up', "{}"))
#     if callback_url is not None:
#         callback_service(callback_url, _id, task_id, 'RUNNING', name, description, additional=user_parameters)

#     try:
#         plugin = _plugin_pre_process(_id, service_name, **kw)
#         result = _plugin_process(plugin, **kw)
#         _plugin_post_process(service_name, plugin, tmp_dir, out_path)


#         if callback_url is not None:
#             user_parameters.update({'result' : result})
#             callback_service(callback_url, _id, task_id, 'SUCCESS', name, description, files=plugin.files, additional=user_parameters)
#         return result




#     except Exception as e:
#         import sys, traceback
#         etype, value, tb = sys.exc_info()
#         traceback.print_exception(etype, value, tb)
#         if callback_url is not None:
#             user_parameters.update({'error': e})
#             callback_service(callback_url, _id, task_id, 'ERROR', name, description, additional=user_parameters)
#         raise e

#     finally :
#         # remove temporary directory where input files where stored
#         io.rm(tmp_dir)

# def _plugin_pre_process(_id, service_name, **kw):
#     """
#     Pre-processing : get plugin, parse parameters
#     """
#     plug = util.get_plugin_byId(_id)
#     if plug is None:
#         raise Exception('Plugin not found by the worker.')
#     plugin = plug.plugin_object
#     return plugin.__class__()

# def _plugin_process(plugin, **kw):
#     """
#     Actual process that is defined int the plugin 'process' method
#     """
#     return plugin(**kw)


# def _plugin_post_process(service_name, plugin, tmp_dir, out_path):
#     """
#     Post-processing : write file, send result, call callback
#     """
#     task_id = plugin_process.request.id
#     # write files in the output directory
#     # TODO loop over result and call URL(plugin service).get_async(job_id= .. , results = {'isfile' : true/false, 'path' : .. , 'value' : ..})
#     new_files(service_name, task_id, out_path, plugin.in_files)
#     # delete tmp files
#     for f in plugin.tmp_files:
#         print 'deleting %s' % f
#         shutil.rmtree(f)




# def new_files(service_name, task_id, out_path, _files):
#     """
#     Write the files in the service directory
#     """
#     out = os.path.join(out_path, task_id)
#     print 'new files'
#     print out_path
#     print _files
#     print out
#     try:
#         os.mkdir(out)
#     except OSError, e:
#         if e.errno == errno.EEXIST:
#             io.rm(out)
#             return new_files(service_name, task_id, out_path, _files)

#     for _f in _files:
#         fname = io.mv(_f[0], out)
#         _f[0] = os.path.join(out, fname)
#     return True


def callback_service(url, plugin_id, task_id, status, results=None, additional=None):
    """
    Send a response back to the callback url with parameters of the job launched
    :param plugin_id : the plugin identifier
    :param task_id : the task identifier
    :param status : the status of the task
    :param results : the output files added by the operation
    :param additional : a dict with some additional parameters that can be needed
    ('error' : when an error occurs, 'result' when a task finish with success)
    """
    params = {'plugin_id': plugin_id,
              'task_id': task_id,
              'status': status}
    debug('callback %s with params %s & results %s & additionnals %s' % (url, params, results, additional))
    if results is not None:
        params.update({'results': results})
    if additional is not None:
        params['bs_private'] = json.dumps(additional)
    try:
        debug('Callback on URL %s with parameters %s : ' % (url, ', '.join(['%s : %s' % (k, v) for k, v in params.iteritems()])))
        urllib2.urlopen(url, data=urllib.urlencode(params))
    except Exception:
        import sys
        import traceback
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
