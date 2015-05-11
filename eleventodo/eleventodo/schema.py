from colander import MappingSchema
from colander import SchemaNode
from colander import String
from colander import Integer
from colander import DateTime
from deform.widget import HiddenWidget
from deform.widget import SelectWidget
from deform.widget import DatePartsWidget



class TodoSchema(MappingSchema):
    """This is the form schema used for list_view and tag_view. This is
    the basis for the add and edit form for tasks.
    """
    id = SchemaNode(
        Integer(),
        missing=None,
        widget=HiddenWidget(),
    )
    description = SchemaNode(String())
    tags = SchemaNode(String(),
        missing=[],
    )
    due_date = SchemaNode(
        DateTime(),
        widget = DatePartsWidget(),
        missing=None,
    )
