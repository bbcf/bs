from bs import model


def get_user(request):
    user_id = request.environ['bs-uid']
    return model.DBSession.query(model.User).filter(model.User.id == user_id).first()


def print_traceback():
    import sys
    import traceback
    traceback.print_exception(*sys.exc_info())
