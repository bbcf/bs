CELERY_IMPORTS = ('bs.lib.tasks',)

# Result storage settings
CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = 'sqlite:///bs-database.sqlite'

# Transport URL
BROKER_URL = 'sqla+sqlite:///celery-transport.sqlite'

