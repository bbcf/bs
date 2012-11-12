from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.http import URL

from bs.lib import io
from bs.operations import util
import os
import urllib
import urllib2
import json
import errno
import shutil


@task()
def plugin_job(username, inputs_directory, outputs_directory, plugin_info,
    user_parameters, service_callback, bioscript_callback, **form_parameters):

    task_id = plugin_job.request.id

    if service_callback is not None:
        callback_service(service_callback, plugin_info['generated_id'], task_id,
            'RUNNING', additional=user_parameters)

    # get plugin class
    plug = util.get_plugin_byId(plugin_info['generated_id'])
    if plug is None:
        raise Exception('Plugin not found by the worker.')
    plugin = plug.plugin_object.__class__()

    # call plugin with form parameters
    ret = plugin(**form_parameters)
    results = [{'is_file': False,
                'value': ret
    }]

    # mkdir output directory
    out = os.path.join(outputs_directory, task_id)
    try:
        os.mkdir(out)
    except OSError, e:
        if e.errno == errno.EEXIST:
            io.rm(out)
            os.mkdir(out)

    # moving files to the output directory
    for output_file, output_type in plugin.output_files:
        out_path = os.path.join(out, output_file)
        io.mv(output_file, out)
        results.append({'is_file': True, 'path': out_path, 'type': output_type})

    # deleting plugin temporary files
    for todel in plugin.tmp_files:
        print 'deleting %s' % todel
        shutil.rmtree(todel)

    # updating bioscript with the results
    print 'bioscript callback'
    print bioscript_callback
    URL(bioscript_callback).get_async(task_id=task_id, results=json.dumps(results))

    # callback
    if service_callback is not None:
        callback_service(service_callback, plugin_info['id'], task_id, 'SUCCESS',
            results=json.dumps(results), additional=user_parameters)


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

    if results is not None:
        params.update({'results': results})
    if additional is not None:
        params.update(additional)
    try:
        urllib2.urlopen(url, data=urllib.urlencode(params))
    except Exception:
        import sys
        import traceback
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
