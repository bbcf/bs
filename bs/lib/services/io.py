# from . import service_manager
# from bs.lib import constants, io, util
# import os, tempfile, errno, urllib2





# def fetch(service, fparams, form_parameters):
#     """
#     Fetch files in BioScript.
#     :param service: the user or service doing the request
#     :param fparams: parameters that are files
#     :param form_parameters: the form parameters
#     """
#     service_name = service.name
#     file_root = None
#     url_root = None
#     try:
#         parameters = service_manager.get(service_name)
#         file_root = parameters.get(constants.SERVICE_FILE_ROOT_PARAMETER, None)
#         url_root = parameters.get(constants.SERVICE_URL_ROOT_PARAMETER, None)
#     except Exception:
#         util.debug(service_name + ' is not a service')


#     util.debug('tmpdir')
#     tmp_dir = temporary_directory()
#     util.debug('plop')
#     print fparams
#     for fparam in fparams:
#         util.debug('fparam %s ' % fparam)
#         value = form_parameters.get(fparam, None)
#         util.debug(value)
#         if value is None or value == '' : continue
#         util.debug(value)
#         # it's not a file field
#         if isinstance(value, basestring):
#             util.debug('not a file field')
#             tmp_file = util.tmppath(d=tmp_dir, fname=None)
#             if tmp_file and file_root is not None and url_root is not None:
#                 # remove //. Servide defined a directory where to take & put files
#                 # so the urls are fakes
#                 value = value.replace('//', '/').replace(':/', '://')
#                 new = value.replace(url_root, file_root)
#                 io.copy(new, tmp_file)
#             elif tmp_file:
#                 # fetch files from url
#                 io.download(value, tmp_file)
#             tmp_files = [tmp_file]
#         # here we should have a file field
#         elif isinstance(value, (list, tuple)): tmp_files = [_take_file(v, tmp_dir) for v in value]
#         else :                               tmp_files = _take_file(value, tmp_dir)

#         if len(tmp_files) == 1:
#             tmp_files = tmp_files[0]
#         util.debug("FILE FETCHED IN %s" % tmp_files)
#         form_parameters[fparam] = tmp_files

#     return tmp_dir


# def fetch_file_field(user, _files, form_parameters):
#     tmp_dir = temporary_directory()
#     try :
#         for form_parameter in _files:
#             if form_parameters.has_key(form_parameter):
#                 value = form_parameters.get(form_parameter)
#                 if isinstance(value, (list, tuple)):
#                     tmp_files = [_take_file(v) for v in value]
#                 else :
#                     tmp_files = _take_file(value)
#                 util.debug("FILE FETCHED AT %s" % tmp_files)
#                 form_parameters[form_parameter] = tmp_files
#     except IOError as e:
#         io.rm(tmp_dir)
#         raise e
#     return tmp_dir

# def _take_file(value, tmp_dir):
#     filename = value.filename
#     file_value = value.value
#     with open(util.tmppath(d=tmp_dir, fname=filename), 'w') as tmp_file:
#         tmp_file.write(file_value)
#     return tmp_file.name

# def fetch_files(service, _files, form_parameters):
#     """
#     Fetch the file given in parameter.
#     The files are stored in _files parameters but only those
#     specified in the form_parameters.
#     This update the form_parameters with the new value
#     """
#     service_name = service.name
#     parameters = service_manager.get(service_name)

#     file_root = parameters.get(constants.SERVICE_FILE_ROOT_PARAMETER, None)
#     url_root = parameters.get(constants.SERVICE_URL_ROOT_PARAMETER, None)

#     tmp_dir = temporary_directory()
#     try :
#         for form_parameter in _files:
#             if form_parameters.has_key(form_parameter):
#                 value = form_parameters.get(form_parameter)
#                 tmp_file = util.tmppath(d=tmp_dir, fname=None)

#                 if tmp_file and file_root is not None and url_root is not None:
#                     # remove //
#                     value = value.replace('//', '/').replace(':/', '://')
#                     new = value.replace(url_root, file_root)
#                     io.copy(new, tmp_file)
#                 elif tmp_file:
#                     io.download(value, tmp_file)

#                 form_parameters[form_parameter] = tmp_file
#     except IOError as e:
#         io.rm(tmp_dir)
#         raise e
#     return tmp_dir

# def _format_submission_parameters(files, params):
#     t = files.get('simple', [])
#     t += files.get('multiple', [])
#     for m in files.get('multiple', []):
#         mlist = []
#         todel = []
#         for k, v in params.iteritems():
#             if k.startswith(m) and len(k.split(':')) == 3:
#                 p, n, f = k.split(':')
#                 if p == m and f == 'file':
#                     if v != '':
#                         mlist.append(v)
#                     todel.append(k)
#         for d in todel: del params[d]
#         params[m] = mlist
#     return t





# def out_path(service_name):
#     parameters = service_manager.get(service_name)
#     out = parameters.get(constants.SERVICE_RESULT_ROOT_PARAMETER, False)
#     if not out:
#         out = service_manager.out_path
#     return out




# def temporary_path(service_name, extension=None, filename='in'):
#     """
#     Build a temporary path in a temporary directory
#     """
#     unique = util.id_generator()
#     tmp_dir = os.path.join(service_manager.in_path, service_name, unique)
#     try:
#         os.mkdir(tmp_dir)
#     except OSError, e:
#         if e.errno == errno.EEXIST:
#             return temporary_path(service_name, extension, filename)
#         else: #this error must be raised to tell that something wrong with mkdir
#             raise OSError

#     unique_path = os.path.join(tmp_dir, filename)
#     if extension is not None:
#         return '%s.%s' % (unique_path, extension)
#     return tmp_dir, unique_path

# def temporary_directory():
#     """
#     Build a temporary directory in the service directory
#     """
#     return util.tmpdir(d=service_manager.in_path)
