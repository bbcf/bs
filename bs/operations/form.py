import tw2.forms as twf
import tw2.core as twc
from bs.operations.base import BaseForm
from bs.operations import wordlist



type2widget = {
    'default' : twf.TextField,
    'boolean' : twf.CheckBox,
    'text' : twf.TextField,
    'numeric' : twf.TextField,
    'file' : twf.FileField,
}


type2validator = {
    'int' : twc.IntValidator,
}


def validator(ptype, required):
    """
    Get the right validator for the ptype given
    """
    if type2validator.get(ptype, False):
        if required: return twc.IntValidator(required=True)
        return twc.IntValidator
    elif required :
        if wordlist.is_of_type(ptype, wordlist.FILE):
            if required : return twf.FileValidator(required=True)
            return twf.FileValidator
        return twc.Required
    return None

def generate_form(parameters):
    """
    Generate a default form from plugins parameters
    """
    field_list = []

    # look all plugin parameters
    for param in parameters:
        pid = param.get('id')
        ptype = param.get('type')
        generic_type = wordlist.parent_type(ptype)



        pmultiple = param.get('multiple', False)
        prequired = param.get('required', False)

        # find the corresponding widget
        widget = type2widget.get(generic_type)(id=pid)

        # fill specificities
        widget.validator = validator(ptype, prequired)
        if pmultiple:
            pass

        field_list.append(widget)

    # add the "Hidden field from BaseForm"
    for c in BaseForm.child.children:
        field_list.insert(0, c)

    form_widget = twf.TableForm()
    form_widget.children = field_list
    return form_widget
