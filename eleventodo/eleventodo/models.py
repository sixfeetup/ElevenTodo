from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
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
    the items in the todo list.
    """
    __tablename__ = 'todoitems'
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    due_date = Column(DateTime)

    def __init__(self, description, due_date=None):
        self.description = description
        self.due_date = due_date


