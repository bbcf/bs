from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet



@task
def test(x):
    return x * x