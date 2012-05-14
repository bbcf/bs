from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet
from . import get_plugin_byId
from joblauncher.lib import io
import os, urllib, urllib2
from celery.task.http import HttpDispatchTask


@task()
def test(x):
    return x * x


@task()
def plugin_process(_id, service_name, tmp_dir, out_path, callback_url=None, **kw):
    """
    Method which retrieve the plugin by it's id and launch the processing steps (pre/process/post)
    """
    task_id = plugin_process.request.id

    if callback_url is not None:
        callback_service(callback_url, {'form_id' : _id, 'task_id' : task_id, 'status' : 'RUNNING'})

    try :
        plugin = _plugin_pre_process(_id, service_name, **kw)
        result = _plugin_process(plugin, **kw)
        _plugin_post_process(service_name, plugin, tmp_dir, out_path)


        if callback_url is not None:
            callback_service(callback_url, {'form_id' : _id, 'task_id' : task_id, 'status' : 'SUCCESS', 'result' : result})
        return result



    except Exception as e:
        if callback_url is not None:
            callback_service(callback_url, {'form_id' : _id,
                                            'task_id' : task_id,
                                            'status' : 'ERROR',
                                            'error' : e})
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
        io.mv(_f, out)



def callback_service(url, result):
    req = urllib2.urlopen(url + '?' + urllib.urlencode(result))
