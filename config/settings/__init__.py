# config/settings/__init__

from .base import *

import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# you need to set "myproject = 'prod'" as an environment variable
# in your OS (on which your website is hosted)
if env('PROJECT_ENVIRONMENT') == 'prod':
   from .prod import *
else:
   from .dev import *