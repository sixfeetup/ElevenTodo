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

----

Overview
====================

Installation instructions:

Install Python 3.4

Install virtualenv, and virtualenvwrapper (on Windows, install virtualenvwrapper-win)::

    pip install virtualenv
    
    pip install virtualenvwrapper

    -or-

    pip install virtualenvwrapper-win

Install the eleventodo app::

    git clone git@github.com:sixfeetup/ElevenTodo.git
    cd ElevenTodo/eleventodo
    mkvirtualenv eleventodo --python=python3.4
    workon eleventodo
    python setup.py develop
    initialize_eleventodo_db development.ini
    pserve development.ini --reload

Note: on Windows, you may need to specify the full path to Python 3.4 when making the virtualenv.::

    mkvirtualenv eleventodo --python=C:\Python34\python.exe

To install the final version of the app, checkout branch ``master``. Each chapter has its own branch that you can check out as well. Do ``python setup.py develop`` after each checkout.

Chapter 1 - Scaffolding
===============================================

Use the ``pcreate`` utility to set up the scaffolding for a new project using SQLAlchemy to access data.

Chapter 2 - ToDo Item
===============================================

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

----

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

----

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

----

Initialize the database with some test data.

Edit ``eleventodo/scripts/initializedb.py``. 

In the import section, replace ``MyModel`` with ``TodoItemModel``.

Where it says ``with transaction.manager:``, replace this::

    model = MyModel(name='one', value=1)            

with this::

    model = TodoItemModel(task='Write a ToDo app')  

Now let's tell the database about the new model and the new sample data.::

    initialize_eleventodo_db development.ini

----

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

    py.test eleventodo\tests.py


    ========================== 2 passed in 0.87 seconds ===========================

----

Now, let's run it and see our very basic page::

    pserve development.ini --reload

See it at http://localhost:6543   You should see this text.


Welcome to the eleventodo
The first item on the ToDo list is: Write a ToDo app


