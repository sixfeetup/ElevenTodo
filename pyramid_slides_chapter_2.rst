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

Introduction to Pyramid - Chapter 2
===============================================

----

Pyramid Workflow

.. note::

    We've done the simplest possible Pyramid app - just a simple Hello World. Now we're going to introduce the standard Pyramid way of setting up a web application.

----


Make a new virtualenv::

    mkvirtualenv eleventodo
    pip install pyramid WebTest

    python --version
    3.4.3

----


Change to your project directory::

    cd C:\Users\[My Username]\Projects\

or::

    cd ~/projects/

Make a new directory, and change to it::
    
    mkdir ElevenTodo
    cd ElevenTodo

Make sure your virtualenv is active. The name of the virtualenv should apper in parenteses at the start of your command prompt.

----

Pyramid Scaffold::

    pcreate -s alchemy eleventodo

    . . .

    Welcome to Pyramid.  Sorry for the convenience.
    ===============================================================================
.. note::

    We are using the ``pcreate`` command line utility to make us a new Pyramid project with a lot of the configuration already filled in for us. This project will use SQLAlchemy to interact with its data store. The name of the new project is eleventodo.

    Pyramid sets up a lot of new files, then prints its rather passive-agressive tagline.

----

Pyramid Scaffold

Let's look around at what Pyramid Scaffold made for us::

    cd eleventodo

    tree /f

or::

    tree

.. note::

    It set up a whole Pyramid project structure. development.ini is configuration for our development environment, and production.ini is configuration for a production deployment.

    setup.py is an ordinary setuptools file, like you can find in any python project.
----

Going Deeper

Inside the eleventodo folder is another eleventodo folder. What does it contain?::

    models.py
    tests.py
    views.py
    . . .

.. note::

    Inside the eleventodo folder is another eleventodo folder. That has files for models, tests and views. We have already seen a simple view, our Hello World page. We have also already written some tests. Models are a new idea. Models define the data needed by our app.

----

Domain Models

.. note::

    TODO talk about Models here

    A domain model is a way of representing and acessing the oersistent data related to your application. For example, the data might be stored in a database. In this tutorial, we will be using models from SQL Alchemy.

----

Git

Let's get this newly-generated project checked in to git.

Make sure we are in the Pyramid app directory::

    cd C:\Users\[My Username]\Projects\ElevenTodo\eleventodo

or::

    cd ~/projects/ElevenTodo/eleventodo

----

Git::

    git init
    git add .
    git commit -m "Inital package from pcreate alchemy scaffold"


----

Install dependencies

Make sure your virtualenv is active. The name of the virtualenv should apper in parenteses at the start of your command prompt.

The ``pcreate`` utility made us a new ``setup.py`` file. We can use it to install this new package and all its dependencies.::

    python setup.py develop

.. note::

    If you use ``pip install -e .`` here, then the ``pserve development.ini --reload`` command won't work. Use ``python setup.py develop`` instead.

    
----

Initialize the database::

    initialize_eleventodo_db development.ini

    [sqlalchemy.engine.base.Engine][MainThread] ()
    [sqlalchemy.engine.base.Engine][MainThread] COMMIT
    [sqlalchemy.engine.base.Engine][MainThread] CREATE UNIQUE INDEX my_index ON models (name)
    . . .

----

We don't want to check the database in to version control, so we add it to ``.gitignore``.::

    echo "eleventodo.sqlite" > .gitignore
    git add .gitignore
    git commit -m "Ignore the SQLite database"

----

Run our new project::

    pserve development.ini

View it in the browser at http://localhost:6543

Hit Ctrl-C to kill the server process when you are done.
.. note::

    Talk about the Pyramid debug toolbar. If the toolbar is not visible, check the ``debugtoolbar.hosts`` setting in development.ini.

----

Cleanup

Get rid of some of the scaffolding that we don't need.

Add a line to ``.gitignore`` for the ``pyramid.pid`` file

----

Cleanup

Tell git to delete the ``static`` and ``templates`` directories::

    cd eleventodo
    git rm static/*
    git rm templates/*

Re-create an empty ``static`` directory.::

    mkdir static

Add an empty ``.gitignore`` file to the ``static`` directory, we will be using it later.

Tell git about the new (empty) ``.gitignore`` file::

    git add static/.gitignore

Commit the cleanup to git::

    git commit -m "Remove boilerplate templates"

----

Run tests

The Pyramid scaffold includes some basic tests to get you started.::

    py.test eleventodo/tests.py

    ========================== 2 passed in 0.87 seconds ===========================


