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

Introduction to the Pyramid web framework
===============================================

----

# TODO insert introductory text here

----

Make a directory to hold our Pyramid app::

    mkdir C:\Users\[My Username]\Projects\pyramid_hello

or::

    mkdir ~/projects/pyramid_hello

----

Change to that directory::

    cd C:\Users\[My Username]\Projects\pyramid_hello

or::

    cd ~/projects/pyramid_hello

----

Use virtualenvwrapper to make a new virtualenv, and tie it to the project directory::

    mkvirtualenv pyramid_hello
    setprojectdir .

or::

    mkproject pyramid_hello

----

Make sure the virtualenv is activated. Your command prompt should look like this::

    (pyramid_hello)C:\Users\[My Username]\Projects\pyramid_hello>

or::

    (pyramid_hello)~/projects/pyramid_hello$

----

Make sure we are using Python 3.4::

    python --version

should display::

    python 3.4.3

----

Install Pyramid in to the virtualenv

    pip install pyramid

----



The simplest Pyramid app

Save this to hello.py

.. code:: python

    from wsgiref.simple_server import make_server
    from pyramid.config import Configurator
    from pyramid.response import Response

    def hello_world(request):
        return Response('Hello world!')

    if __name__ == '__main__':
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()


----

Run it::

    python hello.py


----

See it

Go to ``http://localhost:8000/hello``

----

Stop it

Press Ctrl-C in the command line window to stop the server

----

A closer look - Import

Here we import just the things we need from the framework

.. code:: python

    from wsgiref.simple_server import make_server
    from pyramid.config import Configurator
    from pyramid.response import Response

----

A closer look - Our logic

When a request arrives, we return a response. That's it!

This is the entirety of our program. The rest is plumbing.

.. code:: python

    def hello_world(request):
        return Response('Hello world!')


----

A closer look - The Plumbing

Here we connect all the pieces together.

.. code:: python

    if __name__ == '__main__':
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()
----

A closer look - Zoom and Enhance

"Run this code if you are running as a script, not if you are imported"

.. code:: python

    if __name__ == '__main__':


----

A closer look - Zoom and Enhance

Tell Pyramid about the ``/hello`` url. When that url is requested, call our ``hello_world`` function.

.. code:: python

    if __name__ == '__main__':
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')

-----

A closer look - Zoom and Enhance

Connect our app to the server plumbing.

.. code:: python

    if __name__ == '__main__':
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)

----

A closer look - Zoom and Enhance

Turn it loose!

.. code:: python

    if __name__ == '__main__':
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()


----

Tests

If it doesn't have automated tests, it's not done.

----

Our first test

Put this in a file called test_hello.py

.. code:: python

    import unittest

    class HelloWorldUnitTests(unittest.TestCase):
        def test_hello_world(self):
            from hello import hello_world
            result = hello_world({})
            self.assertEqual(result.body, b'hello!')


----

Install a test runner::

    pip install pytest

.. note::

    Staying motivated to write tests is hard. A test runner makes it easier to write tests. It helps to eliminate some boilerplate, and formats the results nicely.

----


Run that test!::

    python test_hello.py



----

Fail!::

    ================================== FAILURES ===================================       
    ____________________ HelloWorldUnitTests.test_hello_world _____________________       
                                                                                          
    self = <test_hello.HelloWorldUnitTests testMethod=test_hello_world>                   
                                                                                          
        def test_hello_world(self):                                                       
            from hello import hello_world                                                 
            result = hello_world({})                                                      
    >       self.assertEqual(result.body, b'hello!')                                      
    E       AssertionError: b'Hello world!' != b'hello!'                                  
                                                                                          
.. note::

    Failing is good. Never trust a test you haven't seen fail.

    py.test helpfully gives us the error message, and shows us the line that failed.

----

Now what?

Fix the test or fix the code. Maybe both.

----

Let's fix the test::

    self.assertEqual(result.body, b'Hello world!')

And run it again:

    py.test

----

Success!::

    test_hello.py .

    ========================== 1 passed in 0.64 seconds ===========================


----

URLs::

    http://localhost:8000/hello
    http://localhost:8000/hello/

.. note::

    URLs are touchy. Our app is available at http://localhost:8000/hello. Try adding a slash at the end of that url. Sad Face.

    The app should respond to both urls. Let's write a test to make sure it does so.

----

Functional tests::

    pip install WebTest



.. note::

    Functional tests test the applcation as a whole. Unit tests test one behavior of a function or method. WebTest is a helper for testing web applications.

----

Break up our code to make it more easily testable

.. code:: python

    def main():
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        return app

    if __name__ == '__main__':
        app = main()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()

----


Write our first functional test

.. code:: python

    class HelloWorldFunctionalTests(unittest.TestCase):
        def setUp(self):
            from hello import main
            app = main()
            from webtest import TestApp
            self.testapp = TestApp(app)

        def test_without_slash(self):
            res = self.testapp.get('/hello', status=200)
            self.assertTrue(b'Hello world!' in res.body)

----

Run it::

    py.test

    test_hello.py ..

    ========================== 2 passed in 0.76 seconds ===========================

.. note::

    Now we have two test passing. Make the new test fail, then fix it again.

----

Add a failing test for the trailing slash

.. code:: python

        def test_with_slash(self):
            res = self.testapp.get('/hello/', status=200)
            self.assertTrue(b'Hello world!' in res.body)


.. note::

    We wrote the test before the code it was supposed to test! Whaaaa????

    This is the idea behind TDD. Test first!

----

Fix the failing test. Make the main() function in hello.py look like this.

.. code:: python

    def main():
        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(hello_world, route_name='hello')
        config.add_route('hello_with_slash', '/hello/')
        config.add_view(hello_world, route_name='hello_with_slash')
        app = config.make_wsgi_app()
        return app

----

We just added two lines, a route for ``/hello/``, and a view pointing that route to our existing ``hello_world`` function.


.. code:: python

        config.add_route('hello_with_slash', '/hello/')
        config.add_view(hello_world, route_name='hello_with_slash')

----


Run the test again::

    py.test

    test_hello.py ...

    ========================== 3 passed in 0.75 seconds ===========================

Success!







































.
