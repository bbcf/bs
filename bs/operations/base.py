import os

BASE = os.path.dirname(__file__)
TMP_DIR = os.path.normpath(os.path.join(BASE, os.path.pardir, 'tmp'))

import tw2.core
import tw2.forms
import tw2.dynforms


class BaseForm(tw2.forms.TableForm):
    bs_private = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()


class DynForm(tw2.dynforms.CustomisedTableForm):
    bs_private = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()


class Multi(tw2.dynforms.GrowingGridLayout):
    """A modified GridLayout that is centered on multifile upload"""

    def _validate(self, value, state=None):
        value = [v for v in value if not ('del.x' in v and 'del.y' in v)]
        return value
