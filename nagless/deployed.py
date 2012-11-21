import os.path


# For deployments, it is three up from these
# We are here: /var/www/{host-key/the_deployment/{project}/deployed.py
# We want: /var/www/{host-key}/
DEPLOYED_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# We want the {host-key} section
DEPLOYED_KEY = DEPLOYED_ROOT.split("/")[3]
STATIC_ROOT = os.path.join(DEPLOYED_ROOT, 'static')
LOG_FN = os.path.join('/', 'var', 'log', DEPLOYED_KEY, 'nagless.log')


SYSLOG_SOCKET = '/dev/log' # Mac is /var/run/syslog

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'syslog': {
            'format': 'NAGLESS[%(levelname)s] %(module)s: %(message)s',
        },
        'simple': {
            'format': '%(module)s[%(levelname)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'syslog': {
            'level': 'DEBUG',
            'formatter': 'syslog',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.SysLogHandler',
            'address': SYSLOG_SOCKET,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['syslog'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'syslog'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
