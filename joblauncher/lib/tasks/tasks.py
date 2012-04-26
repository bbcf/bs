from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet
from . import get_plugin_byId
import traceback

@task()
def test(x):
    return x * x


@task(ignore_result=True)
def plugin_process(_id, *args, **kw):
    """
    Method wich retrive the plugin by it's id and lauch the processing steps (pre/process/post)
    """
    plugin = _plugin_pre_process(_id, *args, **kw)
    result = _plugin_process(plugin, *args, **kw)
    _plugin_post_process(result)


def _plugin_pre_process(_id, *args, **kw):
    """
    Pre-processing : get plugin, parse parameters
    """
    plug = get_plugin_byId(_id)
    if plug is None:
        raise Exception('Plugin not found by the worker.')
    return plug.plugin_object

def _plugin_process(plugin, *args, **kw):
    """
    Actual process that is defined int the plugin 'process' method
    """
    return plugin.process(*args, **kw)


def _plugin_post_process(result):
    """
    Post-processing : write file, send result, ...
    """
    print result





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