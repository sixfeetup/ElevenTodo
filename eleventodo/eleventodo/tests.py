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
