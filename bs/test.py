def callback(self, user_id, data, fid, tid, st, tn, td. **kw):
# This method is called with some private parameters that you
# passed in the '_up' parameters in the request. Here user_id and data

do_something(user_id, data)

# Other following parameters are defined below

do_other(fid, tid, st, tn. td)

# Other actions depending on the status
if st == 'RUNNING':
    database.set_my_operation(id=tid, launched=True)

elif st == 'ERROR':
    database.set_my_operation(id=tid, finished=True, with_error=True, error=kw.get('error'))

elif st == 'SUCCESS':
    database.set_my_operation(id=tid, finished=True, with_error=False, result=kw.get('result'))
