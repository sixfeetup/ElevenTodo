import unittest
import transaction

from pyramid import testing

from .models import DBSession

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
