from cStringIO import StringIO
import datetime
import fnmatch
import functools
import os
import os.path
import re
import sys
import tempfile
import time

from fabric.api import env, local, put, sudo, settings, cd, lcd, run, hide, runs_once, task
from fabric.api import abort, puts
from fabric.contrib.files import exists


DEPLOYMENT_DIR = '/var/www'
DEPLOYMENT_SYMLINK_DIR = 'the_deployment'
TIME_FMT = "%Y%m%d%H%M%S"

# Pass hosts on the command-line


env.user = 'nagless' 
env.project_key = 'nagless' 
env.tree_is_dirty = False

# -------------------------------------- 
@task
def production():
    """Commands will use the dev server."""
    env.host_key = '%s-prod' % env.project_key
    env.deployment_base_dir = os.path.join(DEPLOYMENT_DIR, env.host_key)
    env.deployment_symlink_dir = os.path.join(env.deployment_base_dir, DEPLOYMENT_SYMLINK_DIR)
    env.hosts = ['nagless.com',
                ]

# -------------------------------------- 

@task
def deploy():
    """Deploy code to a host"""
    if not env.hosts:
        print "You need to specify an environment destination, either:"
        print "   fab dev deploy"
        print "or"
        print "   fab production deploy"
        return
    if not os.path.exists("./fabfile.py"):
        print "Run in the directory containing fabfile.py"
        return
    check_working_tree()

    now = datetime.datetime.utcnow()
    timestamp = now.strftime(TIME_FMT)

    build_archive(timestamp)
    deploy_to_app(timestamp)

# -------------------------------------- 



@task
@runs_once
def build_archive(timestamp, include_built_assets=True):
    """Create the archive(s) to be copied to servers."""
    if not os.path.exists("./manage.py"):
        print "Run in the directory with manage.py!"
        sys.exit(1)
    local('mkdir -p dist')
    # Get the hash of the current HEAD
    commit_hash = local('git rev-parse HEAD', capture=True)

    # Remove old archives so there's only one
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        if os.path.exists("dist/archive") and not os.path.isdir("dist/archive"):
            local('rm dist/archive')
        local('mkdir -p dist/archive')
        local('rm dist/*.tar')
        local('mv dist/*.tar.gz dist/archive')
        # Trim away old files, keep latest ten
        with lcd('dist/archive'):
            local('ls -t1 | tail -n +11 | xargs -r rm -r')

    # Build the new archives
    # Note: see .gitattributes for a list of excluded files and directories
    # Any file in version control is implicitly in the archive
    tar_fn = '%s-%s-%s.tar' % (env.project_key, commit_hash, timestamp)
    local('git archive --format=tar -o dist/%s HEAD' % (tar_fn)) # Use tar format, then gzip later

    # We want a gzipped output for speed over the wire
    local('gzip dist/%s' % (tar_fn))


def deploy_to_app(timestamp):
    # Move the new code to the server
    _deliver_tar(timestamp)

    _update_packages()
    _migrate_db()
    _prepare_static_files()

    _restart_services()
    

# -------------------------------------- 

def _deliver_tar(timestamp):
    """Move and unpack a tar file to a remote directory.
    
    If you call this function twice for the same tar file and directory
    on the same host, only the first one will actually copy anything.
    """
    # Remove previous deployments
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        run('rm /tmp/%s*.tar.gz' % env.project_key)

    # Add the new one
    put('dist/%s*.tar.gz' % env.project_key, '/tmp/')

    new_dir = os.path.join(env.deployment_base_dir, "%s_%s" % (env.project_key, timestamp))
    if not exists(new_dir):
        run('mkdir %s' % new_dir)

    with cd(env.deployment_base_dir):
        # Unpack
        run('tar -x -zf /tmp/%s*.tar.gz -C %s' % (env.project_key, new_dir))

        # Make the new tree available through a shortname link.
        run('ln -sfT %s %s' % (new_dir, env.deployment_symlink_dir))

        # Keep the 5 latest trees.
        with settings(warn_only=True):
            run('ls -td1 %s_* | tail -n +6 | xargs -r rm -r' % (env.project_key))

def _migrate_db():
    with cd(env.deployment_symlink_dir):
        run('../ve/bin/python ./manage.py syncdb --noinput')
        run('../ve/bin/python ./manage.py migrate')

def _prepare_static_files():
    with cd(env.deployment_symlink_dir):
        run('../ve/bin/python ./manage.py collectstatic --noinput')

def _restart_services():
    status = sudo('/sbin/reload uwsgi', shell=False, warn_only=True)
    if status.failed:
        sudo('/sbin/start uwsgi', shell=False)
    sudo('/usr/sbin/service nginx reload', shell=False)

def _update_build_timestamp():
    return timestamp

def _update_packages():
    with cd(env.deployment_base_dir):
        run('virtualenv --python=python2.7 --prompt="(nagless)" ve')
    with cd(env.deployment_symlink_dir):
        run('../ve/bin/python setup.py develop --always-unzip')


@runs_once
def check_working_tree():
    '''Examine the tree, if there are changes to be checked in, stop.'''
    if not env.tree_is_dirty:
        with hide('running'):
            # --porcelain gives us an easy to parse machine format that is backwards compatible.
            # --untracked-files=no means don't show us any untracked files.
            status = local('git status --porcelain --untracked-files=no', capture=True)
        if status:
            print "*** There are uncommited changes here:"
            print status
            abort("Won't deploy from an uncommitted tree")
