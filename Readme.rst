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


