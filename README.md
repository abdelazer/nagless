nagless
=======

Nagless helps you interact better with colleagues by managing the timing of reminders and check-ins

Developer setup
===============

    virtualenv --python=python2.7 --prompt="(nagless)" ve
    . ve/bin/activate
    setup.py develop --always-unzip
    ./manage.py syncdb --noinput
    ./manage.py runserver 8073

Host Installation
=================

- Create nagless user: 
    useradd --create-home --shell /bin/bash --groups www-data nagless

Sudoers
-------
Add the following lines to /etc/sudoers:

    nagless ALL = (root) NOPASSWD: /sbin/start uwsgi, /sbin/stop uwsgi, /sbin/restart uwsgi, /sbin/reload uwsgi
    nagless ALL = (root) NOPASSWD: /usr/sbin/service nginx reload, /usr/sbin/service nginx restart

Install Software
----------------
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install nginx postgresql build-essential libpq-dev python-virtualenv python-dev 

Configure Postgres
------------------
As user postgres:

    createuser nagless --createdb --no-adduser --no-createrole

Deploy
------
    fab dev deploy
