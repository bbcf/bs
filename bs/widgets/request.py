import tw.forms as twf
from bs.lib.helpers import parameters_display
import genshi


request_list = twf.DataGrid(fields = [
    ('id', 'id'),
    ('Date', 'date_done'),
    ('Parameters', lambda x :genshi.Markup(parameters_display(x.parameters))),
    ('Result_id', 'result.id'),
    ('Status', 'result.task.status'),
    ('Output path', 'result.path'),
    ('Task id', 'result.task_id'),
    ('Result', 'result.task.result'),
    ('Traceback', 'result.task.traceback'),
])



def request_object(obj):
    return {'id' : obj.id,
            'date_done' : obj.date_done,
            'parameters' : obj.parameters,
            'status' : obj.result.task.status,
            'output_path' : obj.result.path,
            'task_id' : obj.result.task_id,
            'result' : obj.result.task.result,
            'traceback' : obj.result.task.traceback
    }
