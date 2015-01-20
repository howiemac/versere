"""
override class for base.user

"""

from base.User import User as baseUser

class User(baseUser):
  
  @classmethod
  def default_page(self,req):
    "override for default page to give latest 'daily bread' article"
    try:
      return self.Page.list(kind='article',stage='posted', orderby="`when` desc",limit="0,1")[0]
    except:
#      raise
      return self.Page.get(self.Config.page_default or 1)

    



