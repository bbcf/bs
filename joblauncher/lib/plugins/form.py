from tw import forms as twf
from tw.forms import validators as twv
from joblauncher.lib.plugins import validator
from tg import tmpl_context




class ThresholdForm(twf.TableForm):

    submit_text = 'Submit job'     # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
                                   twf.HiddenField('_pp'),                          # field needed to transfert information to the validation system

                                   twf.HiddenField('key'),                                        # field needed to identify the service
                                                                                                  # REQUIRED and don't modify it

                                   twf.Spacer(),                                                # a spacer between two field

                                   twf.TextField(label_text='Threshold', id='thr',              # a simple input field (with a simple validator)
                                       help_text = 'Input the trhreshold here', validator=twv.NotEmpty()),
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

