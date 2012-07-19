import string, random, tempfile, os
from joblauncher.lib import constants

def to_datagrid(grid_type, grid_data, grid_title, grid_display):
    '''
    Special method which format the parameters to fit
    on the datagrid template.
    @param grid_type : The DataGrid.
    @type grid_type : a DataGrid Object
    @param grid_data : The data.
    @type grid_data : a list of Object to fill in the DataGrid.
    @param grid_title : DataGrid title
    @type grid_title : A string.
    @param grid_display :True if the DataGrid has to be displayed.
    @type grid_display : a boolean. (Normally it's the len() of the 'grid_data' )
    '''
    return {'grid':grid_type,
    'grid_data':grid_data,
    'grid_title':grid_title,
    'grid_display':grid_display}



def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in xrange(size))



def tmpdir(d=None):
    if d is None:
        d = constants.temporary_directory()
    return tempfile.mkdtemp(dir=d)

def tmpfile(prefix='', suffix='', d=None, delete=False):
    if d is None:
        d = tmpdir()
    return tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, dir=d, delete=delete)