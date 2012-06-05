from tw import forms as twf
from tw.forms import validators as twv
from joblauncher.lib.plugins import validator
from tg import tmpl_context




import tw2.core
import tw2.forms

class BaseForm(tw2.forms.TableForm):
    pp = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()
    up = tw2.forms.HiddenField()


class TestForm(BaseForm):
    submit_text = 'Submit job'
    hover_help = True
    show_errors = True
    one = tw2.forms.TextField(label='the parameter one : ', help_text='Some description.', hover_help=True)
    two = tw2.forms.SingleSelectField()
    three = tw2.forms.CheckBox()



class TT(twf.TableForm):

    submit_text = 'Submit job'     # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form

            twf.SingleSelectField(label_text='Threshold', id='thr', options=['one', 'two'],     # a simple input field (with a simple validator)
            help_text = 'Input the threshold here', validator=twv.NotEmpty()),
                                   ]



class FilesForm(twf.TableForm):

    submit_text = 'Merge the files'                                    # text of the submit button

    hover_help = True                                                  # show help_text with mouse onHover

    show_errors = True                                                 # show red labels when validators failed

    fields = [                                                         # define the fields you need in your form

        twf.HiddenField('_pp'),                                        # field needed to transfert information to the validation system
                                                                       # REQUIRED and don't modify it

        twf.HiddenField('key'),                                        # field needed to identify the service
                                                                       # REQUIRED and don't modify it

        twf.HiddenField('_up'),                                        # field needed to transfert user parameters if needed
                                                                       # REQUIRED you can pass some parameters needed by your application
                                                                       # in this field

        twf.SingleSelectField(id='track_1', label_text='File 1 : ',    # simple 'select' field with a custom validator
            help_text = 'Select the first file',                       # you can customize your own
                              validator=twv.NotEmpty()),

        twf.Spacer(),                                                  # a spacer between two field

        twf.SingleSelectField(id='track_2', label_text='File 2 : ',    # simple 'select' field with a custom validator
            help_text = 'Select the second file',
            validator=twv.NotEmpty()),

        twf.TextField(label_text='Threshold', id='thr',                # a simple input field (with a simple validator)
            help_text = 'Input the trhreshold here', validator=twv.NotEmpty()),
           ]

