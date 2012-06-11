import string, random, tempfile, os

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


def temporary_path(fname=None, ext=None, dir=None):
    """
    Get you a temporary path for writing files
    """
    if ext is not None:
        ext = '.' + ext
    else :
        ext = ''

    if fname is None:
        _f = tempfile.NamedTemporaryFile(suffix=ext, delete=True)
        _f.close()
        return _f.name

    tmp_dir = tempfile.mkdtemp(dir=None)
    return os.path.join(tmp_dir, fname + ext)