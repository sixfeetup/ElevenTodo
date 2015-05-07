from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    TodoItem,
    )

# @view_config(route_name='home', renderer='templates/todotemplate.pt')
# def todo_item_view(request):
#     try:
#         task_one = DBSession.query(TodoItem).filter(TodoItem.id == 1).first()
#     except DBAPIError:
#         return Response(conn_err_msg, content_type='text/plain', status_int=500)
#     return {'first_task': task_one.task, 'project': 'eleventodo'}




#   ======================
# views
@view_config(route_name='list', renderer='templates/list.pt')
def list_view(request):
    # rs = request.db.execute("select id, name from tasks where closed = 0")
    rows = DBSession.query(TodoItem).filter(TodoItem.closed == 0).all()
    tasks = [dict(id=row.id, name=row.task) for row in rows]
    return {'tasks': tasks}



# task = TodoItem(
#     user=self.user_id,
#     task=task_name,
#     tags=tags,
#     due_date=due_date,
# )
# task_id = captured.get('id')
# if task_id is not None:
#     action = 'updated'
#     task.id = task_id
# DBSession.merge(task)

@view_config(route_name='new', renderer='templates/new.pt')
def new_view(request):
    if request.method == 'POST':
        if request.POST.get('name'):
            # request.db.execute(
            #     'insert into tasks (name, closed) values (?, ?)',
            #     [request.POST['name'], 0])
            # request.db.commit()
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

#   ======================









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
