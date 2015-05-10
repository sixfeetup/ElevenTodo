from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Table,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


todoitemtag_table = Table(
    'todoitemtag',
    Base.metadata,
    Column('tag_id', Integer, ForeignKey('tags.name')),
    Column('todo_id', Integer, ForeignKey('todoitems.id')),
)


class Tag(Base):
    """The Tag model is a many to many relationship to the TodoItem.
    """
    __tablename__ = 'tags'
    name = Column(Text, primary_key=True)
    todoitem_id = Column(Integer, ForeignKey('todoitems.id'))

    def __init__(self, name):
        self.name = name


class TodoItem(Base):
    """This is the main model in our application. This is what powers
    the items in the todo list.
    """
    __tablename__ = 'todoitems'
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    due_date = Column(DateTime)
    tags = relationship(Tag, secondary=todoitemtag_table, lazy='dynamic')

    def __init__(self, description, tags=None, due_date=None):
        self.description = description
        self.due_date = due_date
        if tags is not None:
            self.apply_tags(tags)

    def apply_tags(self, tags):
        """This helper function merely takes a list of tags and
        creates the associated tag object. We strip off whitespace
        and lowercase the tags to keep a normalized list.
        """
        for tag_name in tags:
            tag = tag_name.strip().lower()
            self.tags.append(DBSession.merge(Tag(tag)))

    @property
    def sorted_tags(self):
        """Return a list of sorted tags for this task.
        """
        return sorted(self.tags, key=lambda x: x.name)

    @property
    def past_due(self):
        """Determine if this task is past its due date. Notice that we
        compare to `utcnow` since dates are stored in UTC.
        """
        return self.due_date and self.due_date < datetime.utcnow()
