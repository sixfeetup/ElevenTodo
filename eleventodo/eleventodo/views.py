import datetime

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    TodoItem,
    )

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


@view_config(context='pyramid.exceptions.NotFound', renderer='templates/notfound.pt')
def notfound_view(request):
    request.response.status = '404 Not Found'
    return {}

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








conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_eleventodo_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
