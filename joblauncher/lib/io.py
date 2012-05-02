import urllib2, urlparse, shutil


block_sz = 8192


def download(_from, _to):
        u = urlparse.urlparse(_from)
        if not u.hostname:
            raise HTTPError('%s is not a valid URL.' % _from)
        try:
            u = urllib2.urlopen(_from)
            with open(_to, 'w') as out:
                while True:
                    buffer = u.read(block_sz)
                    if not buffer: break
                    out.write(buffer)
            return True
        except HTTPError as e:
            print '%s : %s' % (_from, e)
            raise e


def copy(_from,_to):
    shutil.copy2(_from, _to)

def rm(_dir):
    shutil.rmtree(_dir, ignore_errors=True)