# config/settings/__init__

from .base import *

# you need to set "myproject = 'prod'" as an environment variable
# in your OS (on which your website is hosted)
if env('PROJECT_ENVIRONMENT') == 'prod':
   from .prod import *
elif env('PROJECT_ENVIRONMENT') == 'dev':
   from .dev import *
else:
   from .test import *