from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet
from . import get_plugin_byId
from joblauncher.lib import io
import os, urllib, urllib2, json
from celery.task.http import HttpDispatchTask


@task()
def plugin_process(_id, service_name, tmp_dir, out_path, name, description, callback_url=None, **kw):
    """
    Method which retrieve the plugin by it's id and launch the processing steps (pre/process/post)
    """
    task_id = plugin_process.request.id

    user_parameters = json.loads(kw.get('_up', "{}"))
    if callback_url is not None:
        callback_service(callback_url, _id, task_id, 'RUNNING', name, description, additional=user_parameters)

    try :
        plugin = _plugin_pre_process(_id, service_name, **kw)
        result = _plugin_process(plugin, **kw)
        _plugin_post_process(service_name, plugin, tmp_dir, out_path)


        if callback_url is not None:
            user_parameters.update({'result' : result})
            callback_service(callback_url, _id, task_id, 'SUCCESS', name, description, files=plugin.files, additional=user_parameters)
        return result



    except Exception as e:
        if callback_url is not None:
            import sys, traceback
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)

            user_parameters.update({'error' : e})
            callback_service(callback_url, _id, task_id, 'ERROR', name, description, additional=user_parameters)
        raise e

    finally :
        # remove temporary directory where input files where stored
        io.rm(tmp_dir)

def _plugin_pre_process(_id, service_name, **kw):
    """
    Pre-processing : get plugin, parse parameters
    """
    plug = get_plugin_byId(_id)
    if plug is None:
        raise Exception('Plugin not found by the worker.')
    plugin = plug.plugin_object
    plugin._pre_process(service_name)
    return plugin

def _plugin_process(plugin, **kw):
    """
    Actual process that is defined int the plugin 'process' method
    """
    return plugin.process(**kw)


def _plugin_post_process(service_name, plugin, tmp_dir, out_path):
    """
    Post-processing : write file, send result, call callback
    """
    task_id = plugin_process.request.id
    # write files in the output directory
    new_files(service_name, task_id, out_path, plugin.files)




def new_files(service_name, task_id, out_path, _files):
    """
    Write the files in the service directory
    """
    out = os.path.join(out_path, task_id)
    try:
        os.mkdir(out)
    except OSError, e:
        if e.errno == errno.EEXIST:
            io.rm(out)
            return new_files(service_name, task_id, out_path, _files)

    for _f in _files:
        io.mv(_f[0], out)
        fname = os.path.split(_f[0])[1]
        _f[0] = os.path.join(out, fname)



def callback_service(url, form_id, task_id, status, name, desc, files=None, additional=None):
    """
    Send a response back to the callback url with parameters of the job launched
    :param form_id : the form identifier
    :param task_id : the task identifier
    :param status : the status of the task
    :param name : the task name
    :param desc : the task description
    :param files : the output files added by the operation
    :param additional : a dict with some additional parameters that can be needed
    ('error' : when an error occurs, 'result' when a task finish with success)
    """
    params = {'fid' : form_id,
              'tid' : task_id,
              'st' : status,
              'tn' : name,
              'td' : desc}
    if files is not None:
        params.update({'fo' : json.dumps(files)})
    if additional is not None:
        params.update(additional)
    try :
        req = urllib2.urlopen(url, data=urllib.urlencode(params))
    except Exception as e:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)