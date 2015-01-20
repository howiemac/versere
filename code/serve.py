"""
evoke app server script

this is for serving a single app

"""

#fix the path
import os,sys
#sys.path.append(os.path.abspath('.')) 
#sys.path.append(os.path.abspath('../..'))
sys.path.insert(0,os.path.abspath('.')) 
sys.path.insert(1,os.path.abspath('../..'))

from twisted.application import service
from base.serve import start

## Twisted requires the creation of the root-level application object to take place in this file
application = service.Application("evoke application")
## stitch it all together...
start(application)

