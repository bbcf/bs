from bs.model import DBSession, Request, Result
import json

def new_request(parameters, task_id, out_path):
    """
    Store a new Request in the database with the initialization
    of a Result
    :param parameters: the request parameters
    :param task_id : the task launched
    :param out_path : where the result will be written
    """
    # request
    ps = json.dumps(parameters)
    req = Request()
    req.parameters = ps
    DBSession.add(req)
    DBSession.flush()
    # result
    res = Result()
    res.request_id = req.id
    res.path = out_path
    res.task_id = task_id
    DBSession.add(res)

    DBSession.flush()


