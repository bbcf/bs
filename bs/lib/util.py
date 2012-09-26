import string, random, tempfile, os
from bs.lib import constants
import tg

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
    if d is None: d = constants.temporary_directory()
    return tempfile.mkdtemp(dir=d)

def tmppath(d=None, fname=None):
    d = tmpdir(d=d)
    if fname is None: fname = id_generator(5)
    return os.path.join(d, fname)




def debug(*args):
    if tg.config.get('debug', False):
        import inspect
        print '[x] %s [x] %s' % (inspect.stack()[1][1], args)