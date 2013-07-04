# -*- coding: utf-8 -*-
'''
Database model. Put here the rest of the database.
'''

from sqlalchemy import ForeignKey, Column, Sequence
from sqlalchemy.types import Integer, DateTime, VARCHAR, TypeDecorator, PickleType, Text, Boolean, Unicode
from sqlalchemy.orm import relationship, backref, synonym
from bs.model import DeclarativeBase, DBSession
import json
import datetime as dt
from datetime import datetime
import uuid
import re

prefix = "jl_"
delta = dt.timedelta(days=1)
TB_PATTERN = re.compile("\w*Error.*|\w*Exception.*")


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    Usage::
        JSONEncodedDict(255)
    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        print "BIND PARAM"
        print value
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        print "R VALUE"
        print value
        if value is None:
            return None
        return json.loads(value)


class Task(DeclarativeBase):
    __tablename__ = "celery_taskmeta"

    id = Column('id', Integer, Sequence('task_id_sequence'), primary_key=True, autoincrement=True)
    task_id = Column(VARCHAR(255), unique=True)
    status = Column(VARCHAR(50), default='PENDING')
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)
    traceback = Column(Text, nullable=True)

    def __init__(self, task_id):
        self.task_id = task_id


class Connection(DeclarativeBase):
    __tablename__ = "%sconnection" % prefix

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="connections")
    ip = Column(Text)
    user_agent = Column(Text)
    url = Column(Text)
    referer = Column(Text)
    method = Column(Text)
    body = Column(Text)
    content_length = Column(Text)
    content_type = Column(Text)
    query_string = Column(Text)
    date_done = Column(DateTime, default=datetime.now, nullable=True)


class Plugin(DeclarativeBase):
    __tablename__ = "%splugin" % prefix
    id = Column(Integer, autoincrement=True, primary_key=True)
    generated_id = Column(Text, unique=True)
    deprecated = Column(Boolean)
    info = Column(JSONEncodedDict)


class PluginRequest(DeclarativeBase):
    __tablename__ = "%splugin_request" % prefix

    id = Column(Integer, autoincrement=True, primary_key=True)
    plugin_id = Column(Integer, ForeignKey("%splugin.id" % prefix, ondelete="CASCADE"), nullable=False)
    plugin = relationship("Plugin", backref="requests")
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="requests")
    parameters = Column(JSONEncodedDict)
    date_done = Column(DateTime, default=datetime.now, nullable=True)
    status = Column(Text, default='PENDING')
    error = Column(Text)


class Job(DeclarativeBase):
    __tablename__ = "%sjob" % prefix
    id = Column(Integer, autoincrement=True, primary_key=True)
    request_id = Column(Integer, ForeignKey("%splugin_request.id" % prefix, ondelete="CASCADE"), nullable=False)
    request = relationship("PluginRequest", backref="job", uselist=False)
    task_id = Column(VARCHAR(255), nullable=False)
    task = relationship('Task', uselist=False, backref='job', primaryjoin='Job.task_id == Task.task_id', foreign_keys='Task.task_id')

    @property
    def status(self):
        if not self.task:
            stat = self.request.status
            if stat.lower() == 'pending':
                if (self.request.date_done + delta) < datetime.now():
                    return 'FAILURE'
            return stat
        return self.task.status

    @property
    def error(self):
        if not self.task:
            return ''
        return self.task.traceback

    @property
    def simple_error(self):
        if self.error:
            try:
                return re.findall(TB_PATTERN, self.error)[-1]
            except:
                return self.error
        return ''


class Result(DeclarativeBase):
    __tablename__ = "%sresult" % prefix
    id = Column(Integer, autoincrement=True, primary_key=True)
    job_id = Column(Integer, ForeignKey("%sjob.id" % prefix, ondelete="CASCADE"), nullable=False)
    job = relationship("Job", backref="results")
    result = Column(Text)
    _type = Column(Text)
    is_file = Column(Boolean)
    path = Column(Text)
    fname = Column(Text)


class User(DeclarativeBase):
    """
    User definition.
    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    """
    __tablename__ = 'User'

    def setdefaultkey(self):
        uid = str(uuid.uuid4())
        while DBSession.query(User).filter(User.key == uid).first():
            uid = str(uuid.uuid4())
        return uid

    # columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255))
    _email = Column(Unicode(255), unique=True, nullable=True, info={'rum': {'field': 'Email'}})
    _created = Column(DateTime, default=datetime.now)
    key = Column(Unicode(255), unique=True, default=setdefaultkey)
    is_service = Column(Boolean, default=False)
    remote = Column(Unicode(255), unique=False, nullable=True)

    def _get_date(self):
        return self._created.strftime(date_format)

    def _set_date(self, date):
        self._created = date

    created = synonym('_created', descriptor=property(_get_date, _set_date))

    # email and user_name properties
    def _get_email(self):
        return self._email

    def _set_email(self, email):
        self._email = email.lower()

    email = synonym('_email', descriptor=property(_get_email, _set_email))

    def __repr__(self):
        return '<User: id=%r, name=%r, email=%r, key=%r, service=%s>' % (self.id, self.name, self.email, self.key, self.is_service)

    def __unicode__(self):
        return self.name
