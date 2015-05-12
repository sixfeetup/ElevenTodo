.. -*- coding: utf-8 -*-
...  Copyright 2015 Six Feet Up, Inc.

     Licensed under the Apache License, Version 2.0 (the "License");
     you may not use this file except in compliance with the License.
     You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

     Unless required by applicable law or agreed to in writing, software
     distributed under the License is distributed on an "AS IS" BASIS,
     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     See the License for the specific language governing permissions and
     limitations under the License.

:title: Pyramid web app
:event: Eleven Fifty
:author: Calvin Hendryx-Parker
:pygments: tango
:css: custom.css

.. |space| unicode:: 0xA0 .. non-breaking space
.. |br| raw:: html
    <br />

-----

Overview
====================

Installation instructions:

Install Python 3.4

Install virtualenv, and virtualenvwrapper, sitewide. (on Windows, install virtualenvwrapper-win)::

    pip install virtualenv
    
    pip install virtualenvwrapper

    -or-

    pip install virtualenvwrapper-win

Install the eleventodo app::

    git clone git@github.com:sixfeetup/ElevenTodo.git
    cd ElevenTodo/eleventodo
    mkvirtualenv eleventodo --python=python3.4
    workon eleventodo
    pip install -r requirements.txt
    python setup.py develop
    initialize_eleventodo_db development.ini
    pserve development.ini --reload

Note: on Windows, you may need to specify the full path to Python 3.4 when making the virtualenv.::

    mkvirtualenv eleventodo --python=C:\Python34\python.exe

To install the final version of the app, checkout branch ``master``. Each chapter has its own branch that you can check out as well. Each chapter branch contains the code as it is at the end of the chapter. 


Chapter 1 - Scaffolding
===============================================

Check out the starting point::

    git checkout 00-beginning

Note: don't do ``python setup.py develop`` for this chapter.

Use the ``pcreate`` utility to set up the scaffolding for a new project using SQLAlchemy to access data.::

    pcreate -s alchemy eleventodo

Inspect the files that pyramid creates for you.

Chapter 2 - ToDo Item
===============================================

Check out the starting point::

    git checkout 01-scaffolding
    python setup.py develop

Create a data model for the basic entity of the app - the ToDo item.

Edit ``models.py``. Remove the MyModel model, and the Index. Add this.

.. code:: python

    class TodoItemModel(Base):
        """This is the main model in our application. This is what powers
        the tasks in the todo list.
        """
        __tablename__ = 'todoitems'
        id = Column(Integer, primary_key=True)
        task = Column(Text, nullable=False)

        def __init__(self, task):
            self.task = task

-----

Create a view for it too. Populate with some sample data, and view the results.

Edit ``views.py``. 

In the import section, replace ``MyModel`` with ``TodoItemModel``.

Replace my_view with this.

.. code:: python

    @view_config(route_name='home', renderer='templates/todotemplate.pt')
    def todo_item_view(request):
        try:
            task_one = DBSession.query(TodoItemModel).filter(TodoItemModel.id == 1).first()
        except DBAPIError:
            return Response(conn_err_msg, content_type='text/plain', status_int=500)
        return {'first_task': task_one.task, 'project': 'eleventodo'}

-----

Let's make the simplest possible template

Make a new file in eleventodo/templates called ``todotemplate.pt``.

Here's what it should contain::

    <!DOCTYPE html>
    <html lang="${request.locale_name}">
      <head>
        <meta charset="utf-8">
        <title>ToDo List View</title>
      </head>

      <body>
        <div>
          <span>Welcome to the ${project}</span>
        </div>
        <div>
          <span>The first item on the ToDo list is: ${first_task}</span>
        </div>

      </body>
    </html>

-----

Initialize the database with some test data.

Edit ``eleventodo/scripts/initializedb.py``. 

In the import section, replace ``MyModel`` with ``TodoItemModel``.

Where it says ``with transaction.manager:``, replace this::

    model = MyModel(name='one', value=1)            

with this::

    model = TodoItemModel(task='Write a ToDo app')  

Now let's tell the database about the new model and the new sample data.::

    initialize_eleventodo_db development.ini

If you get an error, delete the eleventodo.sqlite database file and try again.

-----

Change the tests to match the new behavior of the application.

We only need to change one test. Replace the existing ``TestMyViewSuccessCondition`` class  with this.

.. code:: python

    class TestMyViewSuccessCondition(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            from sqlalchemy import create_engine
            engine = create_engine('sqlite://')
            from .models import (
                Base,
                TodoItemModel,
                )
            DBSession.configure(bind=engine)
            Base.metadata.create_all(engine)
            with transaction.manager:
                model = TodoItemModel(task='test task')
                DBSession.add(model)

        def tearDown(self):
            DBSession.remove()
            testing.tearDown()

        def test_passing_view(self):
            from .views import todo_item_view
            request = testing.DummyRequest()
            info = todo_item_view(request)
            self.assertEqual(info['first_task'], 'test task')
            self.assertEqual(info['project'], 'eleventodo')

Run the tests::

    pip install pytest
    py.test eleventodo\tests.py


    ========================== 2 passed in 0.87 seconds ===========================

-----

Now, let's run it and see our very basic page::

    rm eleventodo.sqlite
    initialize_eleventodo_db development.ini
    pserve development.ini --reload

See it at http://localhost:6543   You should see this text.


Welcome to the eleventodo
The first item on the ToDo list is: Write a ToDo app



Chapter 3 - Update the database
===============================================

Check out the starting point::

    git checkout 02-todo-item
    python setup.py develop

----

Add routes. Edit ``__init__.py``. Replace the 'home' route with this::

    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('close', '/close/{id}')

----

Edit ``models.py``. Add ``Boolean`` to the list of imports. Make the model look like this.

.. code:: python

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

----

We renamed our model class to just ``TodoItem``. Change the ``scripts/initializedb`` file so that it imports the new model name. Also, lets add a few more rows to the database to start out.::

    with transaction.manager:
        item = TodoItem(task='Write a ToDo app')
        DBSession.add(item)
        item = TodoItem(task='Read the documentation', closed=True)
        DBSession.add(item)

----

The views change.  Add this imort to the top of ``views.py``::

    from pyramid.httpexceptions import HTTPFound


Then set up the new views

.. code:: python


    @view_config(route_name='list', renderer='templates/list.pt')
    def list_view(request):
        # rs = request.db.execute("select id, name from tasks where closed = 0")
        rows = DBSession.query(TodoItem).filter(TodoItem.closed == 0).all()
        tasks = [dict(id=row.id, name=row.task) for row in rows]
        return {'tasks': tasks}


    @view_config(route_name='new', renderer='templates/new.pt')
    def new_view(request):
        if request.method == 'POST':
            if request.POST.get('name'):
                new_task = TodoItem(
                    task = request.POST['name'],
                    closed = False,
                )
                DBSession.merge(task)
                request.session.flash('New task was successfully added!')
                return HTTPFound(location=request.route_url('list'))
            else:
                request.session.flash('Please enter a name for the task!')
        return {}


    @view_config(route_name='close')
    def close_view(request):
        task_id = int(request.matchdict['id'])
        item = DBSession.query(TodoItem).filter(TodoItem.id == task_id)
        item.update({"closed" : True})
        # request.db.execute("update tasks set closed = ? where id = ?",
        #                    (1, task_id))
        # request.db.commit()
        request.session.flash('Task was successfully closed!')
        return HTTPFound(location=request.route_url('list'))


    @view_config(context='pyramid.exceptions.NotFound', renderer='templates/notfound.pt')
    def notfound_view(request):
        request.response.status = '404 Not Found'
        return {}

----

We need a new template for the list view to use. Make a new file in the ``templates`` directory, called ``list.pt``.

.. code:: html


    <!DOCTYPE html>
    <html>
    <head>

      <meta charset="utf-8">
      <title>To Do Item List</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="notfound">
        <h1>List of To Do Items</h1>
      </div>

    </body>
    </html>


----

Add a very simple 404 Not Found page. Save it as ``templates\notfound.pt``

.. code:: html


    <!DOCTYPE html>
    <html>
    <head>

      <meta charset="utf-8">
      <title>Not Found</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="notfound">
        <h1>404 - PAGE NOT FOUND</h1>
      </div>

    </body>
    </html>



----

Update the tests. The test classes should look like this now.

.. code:: python


    class TodoItemModelTests(unittest.TestCase):

        def test_default_value(self):
            from .models import TodoItem
            item = TodoItem("Run tests")
            self.assertEqual(item.task, "Run tests")
            self.assertEqual(item.closed, False)

        def test_supplied_value(self):
            from .models import TodoItem
            item = TodoItem(task="Run more tests", closed=True)
            self.assertEqual(item.task, "Run more tests")
            self.assertEqual(item.closed, True)


    class TestListViewSuccessCondition(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            from sqlalchemy import create_engine
            engine = create_engine('sqlite://')
            from .models import (
                Base,
                TodoItem,
                )
            DBSession.configure(bind=engine)
            Base.metadata.create_all(engine)
            with transaction.manager:
                model = TodoItem(task='test task')
                DBSession.add(model)

        def tearDown(self):
            DBSession.remove()
            testing.tearDown()

        def test_passing_view(self):
            from .views import list_view
            request = testing.DummyRequest()
            info = list_view(request)
            self.assertEqual(info['tasks'], [{'name': 'test task', 'id': 1}])


    class TestListViewFailureCondition(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            from sqlalchemy import create_engine
            engine = create_engine('sqlite://')
            from .models import (
                Base,
                TodoItem,
                )
            DBSession.configure(bind=engine)
            Base.metadata.create_all(engine)

        def tearDown(self):
            DBSession.remove()
            testing.tearDown()

        def test_failing_view(self):
            from .views import list_view
            request = testing.DummyRequest()
            info = list_view(request)
            # self.assertEqual(info.status_int, 500)
            self.assertEqual(info, {'tasks' : []})




Run the tests::

    py.test eleventodo\tests.py


    ========================== 4 passed in 1.20 seconds ===========================

-----

Now, let's run it::

    rm eleventodo.sqlite
    initialize_eleventodo_db development.ini
    pserve development.ini --reload

See it at http://localhost:6543   





Chapter 4 - Edit items
===============================================

Our requirements have changed, now we are tracking the due date rather than a boolean completed flag. We'll change the model and the view to match

Then, we'll make views that allow the user to add, edit, and delete todo items.

----

Check out the starting point::

    git checkout 03-update-db
    python setup.py develop

----

Change the routes in ``__init__.py``::


    config.add_route('add', '/add')
    config.add_route('edit_todo_item', '/edit/{id}')
    config.add_route('delete', '/delete/{id}')

----


Change ``models.py``. Change the import of the ``Boolean`` to ``DateTime``. The model looks like this now

.. code:: python

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

----

When we change the model, we change the ``Initializedb.py`` script as well. Import the ``datetime`` module at the top of the file.

Change the sample data so it looks like this

.. code:: python


    with transaction.manager:
        item = TodoItem(description='Write a ToDo app')
        DBSession.add(item)
        due_date = datetime.datetime(2015, 5, 7, 20, 48, 19, 118000)
        item = TodoItem(description='Read the documentation', due_date=due_date)
        DBSession.add(item)

----

Add some more activity to ``views.py``. First, add this import

.. code:: python

    from pyramid.httpexceptions import HTTPNotFound

Now, change the ``new`` view, call it ``add`` instead.


.. code:: python

    @view_config(route_name='add', renderer='templates/add.pt')
    def add_todo_item(request):
        if request.method == 'POST':
            if request.POST.get('description'):
                if request.POST.get('due_date'):
                    due_date = request.POST['due_date']
                else:
                    due_date = datetime.datetime.now()
                new_todo_item = TodoItem(
                    description = request.POST['description'],
                    due_date = due_date,
                )
                DBSession.add(new_todo_item)
                request.session.flash('New todo item was successfully added!')
                return HTTPFound(location=request.route_url('list'))
            else:
                request.session.flash('Please enter a description for the todo item!')
                return HTTPNotFound()
        else:
            save_url = request.route_url('add')
            return dict(save_url=save_url)

Not Found is simple

.. code:: python

    @view_config(context='pyramid.exceptions.NotFound', renderer='templates/notfound.pt')
    def notfound_view(request):
        request.response.status = '404 Not Found'
        return {}


Allow the user to edit todo items

Note: eventually we will combine the ``add`` and ``edit`` views.

.. code:: python


    @view_config(route_name='edit_todo_item', renderer='templates/edit.pt')
    def edit_todo_item(request):
        """Get the values to fill in the edit form
        """
        todo_id = int(request.matchdict['id'])
        if todo_id is None:
            return False
        todo_item = DBSession.query(TodoItem).filter(
            TodoItem.id == todo_id).one()
        if 'form.submitted' in request.params:
            todo_item.description = request.params['description']
            if request.POST.get('due_date'):
                due_date = request.POST['due_date']
            else:
                due_date = datetime.datetime.now()
            todo_item.due_date = due_date
            # todo_item.due_date = None
            DBSession.add(todo_item)
            return HTTPFound(location = request.route_url('list'))
        return dict(
            todo_item=todo_item,
            save_url = request.route_url('edit_todo_item', id=todo_id),
            )

And delete them


.. code:: python

    @view_config(route_name='delete')
    def delete_todo_item(request):
        """Delete a todo list item
        """
        todo_id = int(request.matchdict['id'])
        if todo_id is not None:
            todo_item = DBSession.query(TodoItem).filter(
                TodoItem.id == int(todo_id))
            todo_item.delete()
            request.session.flash('Todo item has been deleted!')
        return HTTPFound(location = request.route_url('list'))

And see a list of all todo items


.. code:: python

    @view_config(route_name='list', renderer='templates/list.pt')
    def todo_item_list(request):
        """This is the main functional page of our application. It
        shows a listing of the todo items.
        """
        rows = DBSession.query(TodoItem).all()
        todo_items = [dict(id=row.id,
                           description=row.description,
                           due_date=row.due_date) for row in rows]
        return {'todo_items': rows}





----

We'll need a new template for adding todo items. Make ``templates/add.pt``

.. code:: html


    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>

      <meta charset="utf-8">
      <title>New To Do Item</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="wrap">
        <div id="middle">
          <div>
            <form action="${save_url}" method="post">
              <textarea name="description" content="" rows="10" cols="60"></textarea>
              <br/>
              <input type="submit" name="form.submitted" value="Save"/>
            </form>
          </div>
        </div>
      </div>

    </body>
    </html>

----

Also make a template for editing todo items. Later, we will merge ``edit.pt`` and ``add.pt``

.. code:: html


    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>

      <meta charset="utf-8">
      <title>Edit To Do Item</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="wrap">
        <div id="middle">
          <div>
            <form action="${save_url}" method="post">
              <textarea name="description" tal:content="todo_item.description" rows="10"
                        cols="60"/><br/>
              <input type="submit" name="form.submitted" value="Save"/>
            </form>
          </div>
        </div>
      </div>

    </body>
    </html>

----

This template displays a list of todo items. ``list.pt``

.. code:: html


    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>

      <meta charset="utf-8">
      <title>To Do Item List</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="wrap">
        <div id="middle">
          <ul>
            <li tal:repeat="todo_item todo_items">
              ${todo_item.id} - ${todo_item.description} - ${todo_item.due_date}
            </li>
          </ul>
        </div>
      </div>

    </body>
    </html>

----

We changed some names, change them in the ``tests.py`` file as well.

.. code:: python


    import unittest
    import transaction
    import datetime

    from pyramid import testing

    from .models import DBSession

    class TodoItemModelTests(unittest.TestCase):

        def test_default_value(self):
            from .models import TodoItem
            item = TodoItem("Run tests")
            self.assertEqual(item.description, "Run tests")
            self.assertNone(item.due_date)

        def test_supplied_value(self):
            from .models import TodoItem
            test_date_time = datetime.datetime(2015, 5, 7, 20, 48, 19, 118000)
            item = TodoItem(description="Run more tests", due_date=test_date_time)
            self.assertEqual(item.description, "Run more tests")
            self.assertEqual(item.due_date, test_date_time)


    class TestListViewSuccessCondition(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            from sqlalchemy import create_engine
            engine = create_engine('sqlite://')
            from .models import (
                Base,
                TodoItem,
                )
            DBSession.configure(bind=engine)
            Base.metadata.create_all(engine)
            with transaction.manager:
                model = TodoItem(description='test todo item')
                DBSession.add(model)

        def tearDown(self):
            DBSession.remove()
            testing.tearDown()

        def test_passing_view(self):
            from .views import todo_item_list
            request = testing.DummyRequest()
            info = todo_item_list(request)
            self.assertEqual(info['todo_items'], [{'description': 'test todo item', 'id': 1}])


    class TestListViewFailureCondition(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            from sqlalchemy import create_engine
            engine = create_engine('sqlite://')
            from .models import (
                Base,
                TodoItem,
                )
            DBSession.configure(bind=engine)
            Base.metadata.create_all(engine)

        def tearDown(self):
            DBSession.remove()
            testing.tearDown()

        def test_failing_view(self):
            from .views import todo_item_list
            request = testing.DummyRequest()
            info = todo_item_list(request)\
            # self.assertEqual(info.status_int, 500)
            self.assertEqual(info, {'todo_items' : []})




-----

Now, let's run it::

    rm eleventodo.sqlite
    initialize_eleventodo_db development.ini
    pserve development.ini --reload


The model, view, and template changes are in place. 

Go to http://localhost:6543/add to add an item.

Go to http://localhost:6543/edit/1 to edit item 1

Go to http://localhost:6543/delete/1 to delete item 1

Go to http://localhost:6543/ to view the items.







Chapter 5 - Tags
===============================================

Let's add tags to our items

----

Check out the starting point::

    git checkout 04-edit-items
    python setup.py develop

----

Add a route to ``__init__.py``::

    config.add_route('tags', '/tags')

----

To add tags to our items, we start with the model. In ``models.py``, we'll need a few more imports.


.. code:: python


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

----

This table will implement the many-to-many relationship between tags and todo items.

.. code:: python

    todoitemtag_table = Table(
        'todoitemtag',
        Base.metadata,
        Column('tag_id', Integer, ForeignKey('tags.name')),
        Column('todo_id', Integer, ForeignKey('todoitems.id')),
    )

----

Our Tag model.


.. code:: python

    class Tag(Base):
        """The Tag model is a many to many relationship to the TodoItem.
        """
        __tablename__ = 'tags'
        name = Column(Text, primary_key=True)
        todoitem_id = Column(Integer, ForeignKey('todoitems.id'))

        def __init__(self, name):
            self.name = name

----

The todo item model now looks like this.

.. code:: python

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

----

The ``views.py`` file needs a number of changes.

First, some more imports

.. code:: python


    import datetime

    #from pyramid.response import Response
    from pyramid.view import view_config
    from pyramid.httpexceptions import HTTPFound, HTTPNotFound

    #from sqlalchemy.exc import DBAPIError

    from .models import (
        DBSession,
        TodoItem,
        Tag,
        )

Some utility functions

.. code:: python

    date_format_string = '%Y-%m-%d'

    def parse_post(request_post):
        """
        Read and normalize the values from the POST.
        """
        description = request_post['description']
        due_date = request_post.get('due_date')
        if due_date is not None:
            due_date = datetime.datetime.strptime(due_date, date_format_string)
        tags = request_post.get('tags', [])
        if tags:
            tags = tags.split(',')

        return (description, due_date, tags)

    def date_to_string(date_object):
        """
        Return a string representation of a possible date object. If the object can not
        be converted to a date string, returns an empty string.
        """
        try:
            return date_object.strftime(date_format_string)
        except AttributeError:
            return ""


----

The add view changes so it can share a template with the edit view.


.. code:: python

    @view_config(route_name='add', renderer='templates/edit.pt')
    def add_todo_item(request):
        if request.method == 'POST':
            if request.POST.get('description'):
                (description,
                 due_date,
                 tags,
                ) = parse_post(request.POST)
                new_todo_item = TodoItem(
                    description=description,
                    due_date=due_date,
                    tags=tags,
                )
                DBSession.add(new_todo_item)
                request.session.flash('New todo item was successfully added!')
                return HTTPFound(location=request.route_url('list'))
            else:
                request.session.flash('Please enter a description for the todo item!')
                return HTTPNotFound()
        else:
            return dict(
                description="",
                due_date="",
                tags="",
                action='Add',
                save_url=request.route_url('add'),
                )


    @view_config(route_name='edit_todo_item', renderer='templates/edit.pt')
    def edit_todo_item(request):
        """Get the values to fill in the edit form
        """
        todo_id = int(request.matchdict['id'])
        if todo_id is None:
            return False
        if 'form.submitted' in request.params:
            # Submit edits to database
            (description,
             due_date,
             tags,
            ) = parse_post(request.POST)

            edited_todo_item = TodoItem(
                description=description,
                tags=tags,
                due_date=due_date,
            )

            edited_todo_item.id=todo_id


            #todo_item.description = description
            #todo_item.due_date = due_date
            #todo_item.tags = tags

            DBSession.merge(edited_todo_item)
            return HTTPFound(location=request.route_url('list'))
        else:
            # Display item for editing
            todo_item = DBSession.query(TodoItem).filter(
            TodoItem.id == todo_id).one()



----

The item list view gains some more information


.. code:: python


    @view_config(route_name='list', renderer='templates/list.pt')
    def todo_item_list(request):
        """This is the main functional page of our application. It
        shows a listing of the todo items.
        """
        rows = DBSession.query(TodoItem).all()
        todo_items = [dict(id=row.id,
                           description=row.description,
                           due_date=date_to_string(row.due_date)) for row in rows]
        return {'todo_items': todo_items}


----

And, we make a view for the new tags page.


.. code:: python

    @view_config(route_name='tags', renderer='templates/tags.pt')
    def tag_list(request):
        """This page lists the tags in the application.
        """
        tags = DBSession.query(Tag).all()
        return {'tags': tags}



----

The ``edit.pt`` template is now used for additions and for edits.

.. code:: html


    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>

      <meta charset="utf-8">
      <title>${action} To Do Item</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="wrap">
        <div id="Top">
          <div>
            <h1>${action} To Do Item</h1>
          </div>
        </div>
        <div id="middle">
          <div>
            <form action="${save_url}" method="post">
              <span>Description</span>
              <br/>
              <textarea name="description" tal:content="description" rows="10" cols="60"/>
              <br/>
              <span>Tags - comma separated</span>
              <br/>
              <textarea name="tags" tal:content="tags" rows="1" cols="60"/>
              <br/>
              <span>Due Date - YYYY-MM-DD</span>
              <br/>
              <textarea name="due_date" tal:content="due_date" rows="1" cols="60"/>
              <br/>
              <input type="submit" name="form.submitted" value="Save"/>
            </form>
          </div>
        </div>
      </div>

    </body>
    </html>

----

This simple template displays all the tags

.. code:: html


    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>

      <meta charset="utf-8">
      <title>To Do Item Tags</title>
      <link rel="stylesheet" href="/static/theme.css">

    </head>

    <body>

      <div id="wrap">
        <div id="middle">
          <ul>
            <li tal:repeat="tag tags">
              ${tag.name}
            </li>
          </ul>
        </div>
      </div>

    </body>
    </html>



----




Now, let's run it::

    rm eleventodo.sqlite
    initialize_eleventodo_db development.ini
    pserve development.ini --reload


The model, view, and template changes are in place. 

Go to http://localhost:6543/add to add an item.

Go to http://localhost:6543/edit/1 to edit item 1

Go to http://localhost:6543/delete/1 to delete item 1

Go to http://localhost:6543/ to view the items.

Go to http://localhost:6543/tags to view the tags.







Chapter 6 - Links
===============================================

Instead of manually typing in urls to work our app, let's add some links.





----

Check out the starting point::

    git checkout 05-tags
    python setup.py develop

----

Add a route to ``__init__.py``

.. code:: python

    config.add_route('tag', '/tags/{tag_name}')

----

In ``views.py``, the parse_post function gains support for tags.


.. code:: python

    def parse_post(request_post):
        """
        Read and normalize the values from the POST.
        """
        description = request_post['description']
        due_date = request_post.get('due_date')
        if due_date:
            due_date = datetime.datetime.strptime(due_date, date_format_string)
        else:
            due_date = None
        tags = request_post.get('tags')
        if tags:
            tags = tags.split(',')
        else:
            tags = []

        return (description, due_date, tags)



----

In ``views.py``, the edit view allows us to edit the due date.


.. code:: python


    @view_config(route_name='edit_todo_item', renderer='templates/edit.pt')
    def edit_todo_item(request):
        """Get the values to fill in the edit form
        """
        todo_id = int(request.matchdict['id'])
        if todo_id is None:
            return False
        if 'form.submitted' in request.params:
            # Submit edits to database
            (description,
             due_date,
             tags,
            ) = parse_post(request.POST)

            edited_todo_item = TodoItem(
                description=description,
                due_date=due_date,
                tags=tags,
            )
            edited_todo_item.id=todo_id

            DBSession.merge(edited_todo_item)
            return HTTPFound(location=request.route_url('list'))
        else:
            # Display item for editing
            todo_item = DBSession.query(TodoItem).filter(
                TodoItem.id == todo_id).one()
            return dict(
                description=todo_item.description,
                due_date=date_to_string(todo_item.due_date),
                tags=','.join([tag.name for tag in todo_item.sorted_tags]),
                action='Edit',
                save_url=request.route_url('edit_todo_item', id=todo_id),
                )





----

Show the tags in list view

.. code:: python


    @view_config(route_name='list', renderer='templates/list.pt')
    def todo_item_list(request):
        """This is the main functional page of our application. It
        shows a listing of the todo items.
        """
        rows = DBSession.query(TodoItem).all()
        todo_items = [dict(id=row.id,
                           description=row.description,
                           due_date=date_to_string(row.due_date),
                           tags=row.sorted_tags,
                          )
                      for row in rows
                     ]
        return {'todo_items': todo_items,
                'header_text': 'All Items',
               }




----

And, tags get their own page

.. code:: python


    @view_config(route_name='tag', renderer='templates/list.pt',
                 permission='view')
    def tag_view(request):
        """Very similar to the list_view, this view just filters the
        list of tags down to the tag selected in the url based on the
        tag route replacement marker that ends up in the `matchdict`.
        """
        tag_name = request.matchdict['tag_name']

        #todo_items = DBSession.query(TodoItem).filter(
        #    TodoItem.tags.any(Tag.name.in_([tag_name])))
        todo_items = DBSession.query(TodoItem).filter(TodoItem.tags.any(Tag.name.in_([tag_name]))).all()

        count = len(todo_items)
        item_label = 'Items' if count > 1 or count == 0 else 'Item'
        return {'todo_items': todo_items,
                'header_text': '%s tagged %s' % (item_label,
                                                 tag_name,
                                                ),
               }

----

Let's style those links a bit

.. code:: css


    @import url(//fonts.googleapis.com/css?family=Open+Sans:300,400,600,700);
    body {
      font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
      font-weight: 300;
      color: #ffffff;
      background: #bc2131;
    }
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
      font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
      font-weight: 300;
    }
    p {
      font-weight: 300;
    }

    a {
        text-decoration: none;
        color: #ffffff;
        padding: .1em .3em;
        border-radius: .2em;
    }

    a.delete {
        /*visibility: hidden;*/
        display: none;
    }

    a:hover {
        background-color: #f0f0f0;
        color: #1295C1;
    }

    span.list_item:hover > a.delete{
        /*visibility: visible;*/
        display: inline;
    }

    li {
        margin-bottom: 1em;
    }

    span.tag{
        margin-left: .5em;
        margin-right: .5em;
    }

    .font-normal {
      font-weight: 400;
    }
    .font-semi-bold {
      font-weight: 600;
    }
    .font-bold {
      font-weight: 700;
    }



----

The ``list.pt`` template gets a new header, and also displays tags.

.. code:: html


    <body>

      <div id="wrap">
        <div id="top">
          <h1>${header_text}</h1>
        </div>
        <div id="middle">
          <ul>
            <li tal:repeat="todo_item todo_items">
              <span class="list_item">
                <a href="/edit/${todo_item.id}">${todo_item.id} - ${todo_item.description} - ${todo_item.due_date}</a>
                <a class="delete" href="/delete/${todo_item.id}">Delete</a>
              </span>
              <br/>
              <span class="tag" tal:repeat="tag todo_item.tags">
                <a href="/tags/${tag.name}">${tag.name}</a>
              </span>
            </li>
          </ul>
        </div>
        <div id="bottom">
          <h2><a href="/add">Add new item</a></h2>
        </div>
      </div>

    </body>



----







Now, let's run it::

    rm eleventodo.sqlite
    initialize_eleventodo_db development.ini
    pserve development.ini --reload


The model, view, and template changes are in place. 


Go to http://localhost:6543/ to view the items.

There are links to click for adding, editing and deleting items.






Chapter 7 - Better forms with Deform
===============================================

The Deform library handles the creation and validation of forms. 

Also in this chapter, we use deform-bootstrap to improve the look of the app.




----

This is a big change, so check it out directly::

    git checkout 07-deform
    python setup.py develop

----


Now, let's run it::

    rm eleventodo.sqlite
    initialize_eleventodo_db development.ini
    pserve development.ini --reload


The model, view, and template changes are in place. 


Go to http://localhost:6543/ to view the items.


----

The key point in form handling is that a form view does two things: it serves the page where the form is rendered, and it handles the POST request when the form is submitted. 

Watch for the ``if 'submit' in request.POST:`` lines. That's where the view decides if it is serving a form page or handling a POSTed form.
















































































.


