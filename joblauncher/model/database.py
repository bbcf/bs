# -*- coding: utf-8 -*-
'''
Database model. Put here the rest of the database.
'''



from sqlalchemy import ForeignKey, Column, Sequence
from sqlalchemy.types import Integer, DateTime, VARCHAR, TypeDecorator, PickleType, Text
from joblauncher.lib import constants
from sqlalchemy.orm import relationship, synonym
from joblauncher.model import DeclarativeBase, DBSession
import transaction
import json
from datetime import datetime

prefix = "jl_"


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    Usage::
        JSONEncodedDict(255)
    """
    impl = VARCHAR
    def process_bind_param(self, value, dialect):
        if value is None: return None
        return json.dumps(value)
    def process_result_value(self, value, dialect):
        if value is None: return None
        return json.loads(value)




class Task(DeclarativeBase):
    __tablename__ = "celery_taskmeta"

    id = Column('id', Integer, Sequence('task_id_sequence'), primary_key=True, autoincrement=True )
    task_id = Column(VARCHAR(255), unique=True)
    status = Column(VARCHAR(50), default='PENDING')
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)
    traceback = Column(Text, nullable=True)

    def __init__(self, task_id):
        self.task_id = task_id

class Request(DeclarativeBase):
    __tablename__ = "%srequest" % prefix

    id = Column(Integer, autoincrement=True, primary_key=True)
    parameters = Column(JSONEncodedDict(255))
    _date_done = Column(DateTime, default=datetime.now, nullable=False)
    result = relationship("Result", backref="request", uselist=False)

    def _get_date(self):
        return self._date_done.strftime(constants.date_format)

    def _set_date(self,date):
        self._date_done = date

    date_done = synonym('_date_done', descriptor=property(_get_date, _set_date))

    def __str__(self):
        return "<Request %s %s %s>" % (self.id, self.date_done, self.result)

class Result(DeclarativeBase):
    __tablename__ = "%sresult" % prefix
    id = Column(Integer, autoincrement=True, primary_key=True)
    request_id = Column(Integer, ForeignKey("%srequest.id" % prefix, ondelete="CASCADE"), nullable=False)
    path = Column(VARCHAR(255), nullable=True)
    task_id = Column(Integer, ForeignKey('celery_taskmeta.task_id', ondelete="CASCADE"), nullable=False)
    task = relationship("Task", backref="request_result")



    def __str__(self):
        return "<Result %s %s %s %s>" % (self.id, self.path, self.task_id, self.task.traceback)


