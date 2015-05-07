from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Boolean,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class TodoItem(Base):
    """This is the main model in our application. This is what powers
    the tasks in the todo list.
    """
    __tablename__ = 'todoitems'
    id = Column(Integer, primary_key=True)
    task = Column(Text, nullable=False)
    closed = Column(Boolean, nullable=False)

    def __init__(self, task, closed=False):
        self.task = task
        self.closed = closed
