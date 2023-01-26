import os
import logging
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
db_logger = logging.getLogger('db')

print('This is a test of the logger')

db_logger.info('this is a info log', extra={'custom_category':'Email'})
db_logger.warning('This is  a warning log', extra={'custom_category':'History Migration'})

try:
    1/0

except Exception as e:
    db_logger.exception(e, extra={'custom_category':'Email'})
