from tw import forms as twf
from tw.forms import validators as twv
from joblauncher.lib.plugins import validator
from tg import tmpl_context


def get_options():
    '''
    Method to put in options in a 'select' field.
    :param tag : name of the object to get
    '''
    return [(o.id, o.name) for o in tmpl_context.toto]



class ThresholdForm(twf.TableForm):

    submit_text = 'Submit job'     # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
                                   twf.HiddenField('_pp'),                          # field needed to transfert information to the validation system


#                                   twf.SingleSelectField(id='track', label_text='Track : ',    # simple 'select' field with a custom validator
#                                       help_text = 'Select the track to apply the threshold on.', options=get_options,
#                                       validator=validator.TrackValidator(datatype='signal', not_empty=True)),

                                   twf.Spacer(),                                                # a spacer between two field

                                   twf.TextField(label_text='Threshold', id='thr',              # a simple input field (with a simple validator)
                                       help_text = 'Input the trhreshold here', validator=twv.NotEmpty()),
                                   ]

class ImageForm(twf.TableForm):

    submit_text = 'Compute image'            # text of the submit button
    hover_help = True                        # show help_text with mouse onHover
    show_errors = True                       # show red labels when validators failed
    fields = [                               # define the fields you need in your form
                                   twf.HiddenField('_private_params'),    # field needed to transfert information to the validation system

                                   twf.SingleSelectField(id='my_track', label_text='Track : ',    # simple 'select' field with a custom validator
                                       help_text = 'Select the most beautiful track you have.', options=get_options,
                                       validator=validator.TrackValidator(datatype='features', not_empty=True)),

                                   twf.Spacer(),
                                   twf.CheckBox(id='per_chromosomes', label_text='Per chromosomes', help_text='Display a count per chromosomes'),
                                   ]

def get_options():
    return [(o.id, o.name) for o in tmpl_context.files]


class FilesForm(twf.TableForm):

    submit_text = 'Merge the files'     # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
        twf.HiddenField('_pp'),                          # field needed to transfert information to the validation system
        twf.SingleSelectField(id='track1', label_text='File 1 : ',    # simple 'select' field with a custom validator
            help_text = 'Select the first file',
                              validator=twv.NotEmpty()),
        twf.Spacer(),                                                # a spacer between two field
        twf.SingleSelectField(id='track_2', label_text='File 2 : ',    # simple 'select' field with a custom validator
            help_text = 'Select the second file',
            validator=twv.NotEmpty()),
        twf.TextField(label_text='Threshold', id='thr',              # a simple input field (with a simple validator)
            help_text = 'Input the trhreshold here', validator=twv.NotEmpty()),
           ]

