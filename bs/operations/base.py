import os
import tg


TMP_DIR = tg.config.get('root.directory')
from celery import current_app
if 'ROOT_DIRECTORY' in current_app.conf:
    ROOT_DIRECTORY = current_app.conf['ROOT_DIRECTORY']
    TMP_DIR = os.path.normpath(os.path.join(ROOT_DIRECTORY, 'tmp'))


print TMP_DIR

import tw2.core
import tw2.forms
import tw2.dynforms
import warnings


class BaseForm(tw2.forms.TableForm):
    bs_private = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()


class DynForm(tw2.dynforms.CustomisedTableForm):
    bs_private = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()


class Multi(tw2.dynforms.GrowingGridLayout):
    """A modified GridLayout that is centered on multifile upload"""
    warnings.warn('Multi is deprected, use twb.BsMulti instead', DeprecationWarning)

    def _validate(self, value, state=None):
        value = [v for v in value if not ('del.x' in v and 'del.y' in v)]
        return value
