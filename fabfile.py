from fabric.api import run, cd, local, prefix, task, hosts
from fabric.colors import green


settings = {
    'paths': {
        'sugar': {
            'bs': '/data/dev/bs'
        }
    }
}


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


## for updating dev server on sugar from local
# e.g:
# update bioscript and restart service: $ fab update deploy
# update all bioscript and all libraires: $ fab update:libs=True (fab update:True)

sugar_libs = ['bbcflib', 'bsPlugins', 'tw2.bs']


@task
@hosts('yo@sugar.epfl.ch')
def sugar_sync_repo(project='bs'):
    path = settings['paths']['sugar'][project]
    with cd(path):
        pull(locally=False)
        push(locally=False)


@task(alias='supdate')
@hosts('yo@sugar.epfl.ch')
def sugar_update(libs=False, project='bs'):
    print(green('[x] Updating bioscript ...'))
    path = settings['paths']['sugar'][project]
    with cd(path):
        pull(locally=False)
    if libs:
        with cd('/data/dev/libs'):
            print(green('[x] Updating libs on sugar ...'))
            for lib in sugar_libs:
                print(green('\t[x] %s' % lib))
                with cd(lib):
                    pull(locally=False)


@task(alias='sdeploy')
@hosts('yo@sugar.epfl.ch')
def deploy_sugar(cmd='restart', project='bs'):
    print(green('[x] Service %sing on sugar ... ' % cmd))
    path = settings['paths']['sugar'][project]
    with cd(path):
        with prefix('workon %s' % project):
            _run(locally=False)("./webserverctl %s && ./workerctl %s" % (cmd, cmd))

@task(alias='webserver')
@hosts('yo@sugar.epfl.ch')
def deploy_sugar(cmd='restart', project='bs'):
    print(green('[x] Service %sing on sugar ... ' % cmd))
    path = settings['paths']['sugar'][project]
    with cd(path):
        with prefix('workon %s' % project):
            _run(locally=False)("./webserverctl %s" % cmd)
