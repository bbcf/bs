from bs import model


def get_user(request):
    user_id = request.environ['bs-uid']
    return model.DBSession.query(model.User).filter(model.User.id == user_id).first()
