import datetime

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from deform import Form
from deform import ValidationFailure

import transaction

from .schema import TodoSchema

from .models import (
    DBSession,
    TodoItem,
    Tag,
    )


date_format_string = '%Y-%m-%d'

#def parse_post(request_post):
#    """
#    Read and normalize the values from the POST.
#    """
#    description = request_post['description']
#    due_date = request_post.get('due_date')
#    if due_date:
#        due_date = datetime.datetime.strptime(due_date, date_format_string)
#    else:
#        due_date = None
#    tags = request_post.get('tags')
#    if tags:
#        tags = tags.split(',')
#    else:
#        tags = []
#
#    return (description, due_date, tags)

def date_to_string(date_object):
    """
    Return a string representation of a possible date object. If the object can not
    be converted to a date string, returns an empty string.
    """
    try:
        return date_object.strftime(date_format_string)
    except AttributeError:
        return ""

def process_todo_item_form(form, request):
    """This helper code processes the todo_item from that we have
    generated from Colander and Deform.

    This handles both the initial creation and subsequent edits for
    a task.
    """
    try:
        # try to validate the submitted values
        controls = request.POST.items()
        captured = form.validate(controls)
        action = 'created'
        with transaction.manager:
            tags = captured.get('tags', [])
            if tags:
                tags = tags.split(',')
            due_date = captured.get('due_date')
            description = captured.get('description')
            task = TodoItem(
                description=description,
                tags=tags,
                due_date=due_date,
            )
            task_id = captured.get('id')
            if task_id is not None:
                action = 'updated'
                task.id = task_id
            DBSession.merge(task)

        # Back to the list
        return HTTPFound(location=request.route_url('list'))

        #msg = "To Do Item <b><i>%s</i></b> %s successfully" % (description, action)
        #request.session.flash(msg, queue='success')
        ## Reload the page we were on
        #location = request.url
        #return Response(
        #    '',
        #    headers=[
        #        ('X-Relocate', location),
        #        ('Content-Type', 'text/html'),
        #    ]
        #)

        #html = form.render({})

    except ValidationFailure as e:
        # the submitted values could not be validated
        #html = e.render()
        return Response(e.render())

def generate_task_form(formid="deform"):
    """This helper code generates the form that will be used to add
    and edit the tasks based on the schema of the form.
    """
    schema = TodoSchema()
    options = """
    {success:
      function (rText, sText, xhr, form) {
        deform.focusFirstInput();
        var loc = xhr.getResponseHeader('X-Relocate');
        if (loc) {
          document.location = loc;
        };
       }
    }
    """
    # Unneeded deform javascript options
    #    deform.processCallbacks();
    return Form(
        schema,
        buttons=('submit',),
        formid=formid,
        use_ajax=True,
        ajax_options=options,
    )




@view_config(route_name='add', renderer='templates/edit.pt')
def add_todo_item(request):

    form = generate_task_form()
    if 'submit' in request.POST:
        return process_todo_item_form(form, request)
    return {
        'action' : 'Add',
        'form': form.render(),
    }


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
    return HTTPFound(location=request.route_url('list'))

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

@view_config(route_name='tags', renderer='templates/tags.pt')
def tag_list(request):
    """This page lists the tags in the application.
    """
    tags = DBSession.query(Tag).all()
    return {'tags': tags}

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
