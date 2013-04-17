from fabric.api import run, cd, local, prefix, task, hosts
from fabric.colors import green


def _run(locally):
    if locally:
        return local
    return run


@task
def push(branch='master', remote='origin', locally=True):
    print(green('[x] PUSHING repository'))
    _run(locally)("git push %s %s" % (remote, branch))


@task
def pull(branch='master', remote='origin', locally=True):
    print(green('[x] PULLING repository'))
    _run(locally)("git pull %s %s" % (remote, branch))


@task
def sync(branch='master', remote='origin', locally=True):
    print(green('[x] SYNCING repository'))
    pull(branch, remote, locally)
    push(branch, remote, locally)


@task
def serve(conf_file, branch='master', remote='origin', opts='--reload', workon='bs', locally=True):
    print(green('[x] SERVING ...'))
    _run(locally)('paster serve %s %s' % (opts, conf_file))


## for updating dev server on sugar from local
# e.g:
# update bioscript and restart service: $ fab update deploy
# update all bioscript and all libraires: $ fab update:libs=True (fab update:True)

sugar_libs = ['bbcflib', 'bsPlugins', 'tw2.bs']


@task
@hosts('yo@sugar.epfl.ch')
def sync_sugar():
    with cd('/data/dev/bs'):
        pull(locally=False)
        push(locally=False)


@task(alias='update')
@hosts('yo@sugar.epfl.ch')
def update_sugar(libs=False):
    print(green('[x] Updating bioscript ...'))
    with cd('/data/dev/bs'):
        pull(locally=False)
    if libs:
        with cd('/data/dev/libs'):
            print(green('[x] Updating libs on sugar ...'))
            for lib in sugar_libs:
                print(green('\t[x] %s' % lib))
                with cd(lib):
                    pull(locally=False)


@task(alias='deploy')
@hosts('yo@sugar.epfl.ch')
def deploy_sugar(cmd='restart'):
    print(green('[x] Service %sing on sugar ... ' % cmd))
    with cd('/data/dev/bs'):
        with prefix('workon bs'):
            _run(locally=False)("./webserverctl %s && ./workerctl %s" % (cmd, cmd))
