"""
config file for versere (evoke app)

"""


sitename='versere'
#meta_description="" #site description text for search engines
#meta_keywords="" #comma separated list of keywords for search engines

#permits={} #basis of permit system

guests=True #do guests have access by default?
attribution=True
default_class="Page"
registration_method="admin" # "admin" : admin has to register each user
                              # "approve" : online self registration with approval by admin
default_page=1 #
urlpath=""  # no /evoke in url

from evoke.data.schema import *  #for data definition

class Backlink(Schema):
  table='backlinks'
  page = INT,KEY
  link = INT,KEY

# include config.py files from class folders

#from evoke.config_base import Page



