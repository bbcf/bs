import urllib2, urlparse, shutil, re, os


block_sz = 8192


def download(_from, _to):
        u = urlparse.urlparse(_from)
        if not u.hostname:
            raise urllib2.HTTPError('%s is not a valid URL.' % _from)
        try:
            u = urllib2.urlopen(_from)
            with open(_to, 'w') as out:
                while True:
                    buffer = u.read(block_sz)
                    if not buffer: break
                    out.write(buffer)
            return True
        except urllib2.HTTPError as e:
            print '%s : %s' % (_from, e)
            raise e


def copy(_from,_to):
    shutil.copy2(_from, _to)

def rm(_dir):
    shutil.rmtree(_dir, ignore_errors=True)

def mv(src, dst):
    fname = os.path.split(src)[1]
    fdst = os.path.join(dst, fname)
    if os.path.exists(fdst) : # change fdst name if already exist
        dir, fname = os.path.split(fdst)
        reg = re.compile('(%s\()(\d+)(\).*)' % fname)
        for f in os.listdir(dir):
            max = 1
            matcher = reg.match(f)
            if matcher:
                n, i, e = matcher.groups()
                max = max(max, int(1))
        fdst = os.path.join(dir, '%s(%s)' % (fname, (max + 1)))
    if os.path.exists(src):
        shutil.move(src, fdst)
    return os.path.split(fdst)[1]
