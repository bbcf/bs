import hashlib, os, json, wordlist
from pkg_resources import resource_filename
from yapsy.IPlugin import IPlugin


import string, random, tempfile
random_name = lambda x : ''.join(random.choice(string.ascii_lowercase + string.digits) for i in xrange(x))


class OperationPlugin(IPlugin):

    def __init__(self):

        if not hasattr(self, 'info') : self.info = {}

        self.title = self.info.get('title', '')
        self.description = self.info.get('description', '')
        self.path = self.info.get('path', None)
        self.output = self.info.get('output', '')
        self.in_parameters = self.info.get('in', [])
        self.out_parameters = self.info.get('out', [])
        self.meta = self.info.get('meta', '')

        self.uid = None
        self.service = None
        self.in_files = []
        self.tmp_files = []



    def unique_id(self):
        '''
        It's an unique identifier for your plugin.
        Do not override
        '''
        if self.uid is None:
            self.uid = hashlib.sha1(self.path.__str__()).hexdigest()
        return self.uid



    def new_file(self, fpath, fparam):
        """
        Append a file to the result
        """
        added = False
        for p in self.out_parameters:
            if p.get('id') == fparam:
                added = True
                ftype = p.get('type')
                self.in_files.append([fpath, ftype])
                break
        if not added :
            raise Exception('You must give the same id as one of the out parameters.')


    def in_params_typeof(self, typeof):
        return [param for param in self.in_parameters if wordlist.is_of_type(param.get('type'), typeof)]


    def temporary_path(self, fname=None, ext=None):
        """
        Get a temporary path to write a file.
        File will be automatically deleted at the end of the plugin
        process.
        :param fname: the file name
        :return: a path
        """
        try:
            import tg
            tmp_dir = tg.config.get('temporary.directory',
                resource_filename('bs', 'tmp'))
        except:
            tmp_dir = resource_filename('bs', 'tmp')

        tmp_dir = tempfile.mkdtemp(dir=tmp_dir)
        if fname is None or fname == '': fname = random_name(6)
        if ext is not None:
            if ext.startswith('.') : fname += ext
            else : fname = '%s.%s' % (fname, ext)

        fpath = os.path.join(tmp_dir, fname)
        self.tmp_files.append(tmp_dir)
        return fpath




import tw2.core
import tw2.forms
import tw2.dynforms as twd

class BaseForm(tw2.forms.TableForm):
    pp = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()
    up = tw2.forms.HiddenField()

class MultipleFileUpload(twd.GrowingGridLayout):
    file = tw2.forms.FileField()
