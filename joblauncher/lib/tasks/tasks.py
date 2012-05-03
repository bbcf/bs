from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet
from . import get_plugin_byId
from joblauncher.lib import io
import os
from celery.task.http import HttpDispatchTask


@task()
def test(x):
    return x * x


@task(ignore_result=True)
def plugin_process(_id, service_name, tmp_dir, out_path, callback_url=None, **kw):
    """
    Method which retrieve the plugin by it's id and launch the processing steps (pre/process/post)
    """
    plugin = _plugin_pre_process(_id, service_name, **kw)
    result = _plugin_process(plugin, **kw)
    _plugin_post_process(service_name, plugin, tmp_dir, out_path, result, callback_url)


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


def _plugin_post_process(service_name, plugin, tmp_dir, out_path, result, callback_url):
    """
    Post-processing : write file, send result, call callback
    """
    task_id = plugin_process.request.id
    # write files in the output directory
    new_files(service_name, task_id, out_path, plugin.files)
    # remove temporary directory where input files where stored
    io.rm(tmp_dir)
    # callback
    if callback_url is not None:
        HttpDispatchTask.delay(url=callback_url, method="GET", result=result)
        URL(callback_url).get_async((result,))

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


#@task()
#def plugin_process(plugin_id, _private_params, *args, **kw):
#    from pygdv.handler.plugin import get_plugin_byId
#    from pygdv.handler.job import new_tmp_job
#    plug = get_plugin_byId(plugin_id, model.Manager)
#    if plug :
#        _private_params = json.loads(_private_params)
#        session = model.DBSession()
#        _private_params['session'] = session
#        project = session.query(model.Project).filter(model.Project.id == _private_params['project_id']).first()
#        _private_params['project'] = project
#        #        job = new_tmp_job(plug.plugin_object.title(), project.user_id, project.id, session=session)
#        #        _private_params['job'] = job
#        kw.update(_private_params)
#        try :
#            value = plug.plugin_object.process(*args, **kw)
#            return value
#        except Exception as e:
#            job = kw['job']
#            job.data = str(e)
#            job.output = constants.JOB_FAILURE
#            session.add(job)
#        finally : 
#            session.commit()
#            session.close()
#
#    return 0