"""
override class for evoke.page

"""

import os, string, re

from calendar import month_name

from evoke.render import html
from evoke.lib import *
from evoke.Page import Page as basePage
from evoke.data import execute


class Page(basePage):

  def get_navbar_links(self):
    "override the evoke version..."
    links=[]
    for uid in (1066,1,442,996,1009,9,10,11,):
      p=self.get(uid)
      links.append(
        (p.name,p.url(),p.name)
        )
#    links.append(("backlinks",self.get(7).url('get_backlinks'),"backlinks within this site"))
    return links

  def post(self,req):
    """fix date and format when posting a draft to diary category 442
       """
    if (self.parent!=442): 
      return basePage.post(self,req)
    if basePage._posted(self,req):  
      self.fix_diary_date(req)
#      self.reform_text(req)
      if not req.error:
       req.warning='diary date set'
    return self.view(req)
  post.permit='create page'

  def fix_diary_date(self,req):
    ""
    try:
     n=self.name.replace(',','')
     kind,day,month,year,place=n.split(' ',4)
#      print i.uid,':',day,' - ',month,' - ',year
     if day[1] in ['0','1','2','3','4','5','6','7','8','9']:
        day=day[:2]
     else:
        day=day[0]
     month=list(month_name).index(month)
     date='%s/%s/%s' % (day,month,year)
     self.when=DATE(date)
#     print "WHEN=>",self.when
     self.set_seq()
     self.flush()
    except:
     req.error="date handling problem - date not set for %s" % self.uid

  def fix_diary_dates(self,req):
    ""
    arts=self.list(parent=442)
    for i in arts:
     i.fix_diary_date(req) 
    req.message="diary dates updated"
    return self.get(1).view(req)

  def autopost(self,req):
    "autoposts oldest draft article"
    p=self.get_todays_article() 
    msg="no draft found" # default message
    if p: # if we have any draft
      p._posted(req) #post it
      msg= "%s posted on %s" % (p.uid,p.when) 
    return msg  
  autopost.permit="admin page"   

  @classmethod
  def get_todays_article(cls):
    """
    find the earliest draft article
    """
    articles=cls.list(stage='draft',orderby='uid',limit='0,1')
    return articles and articles[0] or None

# backlinks

  def save_text(self, req):
    """enhances the basePage version to store the links found in the text
       """
    self.store_backlinks(text=req.text)
    return basePage.save_text(self,req)

  def store_backlinks(self,text=''):
    """ Extracts internal links from a posted page.
        Stores the links in the "backlinks" table
    """
    if self.stage!='posted':
      return False
    # get the links (a list of all internal link uids)
    rule=re.compile(r'(\[\ *)(\d+)')
    # delete any old links
    execute("delete from `%s`.backlinks where page=%s" % (self.Config.database,self.uid))
    # find the new links - using a dictionary to eliminate duplicates
    backlinks={} 
    for i in rule.findall(text or self.text):
      backlinks[int(i[1])]=True
    # and store
    for link in backlinks:
      bl=self.Backlink.new()
      bl.page=self.uid
      bl.link=link
      bl.flush()
    return True

  def fix_backlinks(self,req):
    """ Extract all backlinks for all posted pages.
        Recreates the "backlinks" table from scratch.
    """
    for p in self.list(stage='posted',kind='page'):
      p.store_backlinks()
    req.message='backlinks for all pages updated'
    return self.redirect(req)
  fix_backlinks.permit="admin page"

  def get_backlinks(self,req=None,formatted=False):
    """ returns backlinks to self
    req (request) is required if formatted==True
    """
    backlinks=self.Backlink.list_int(item='page',link=self.uid)
    if backlinks and formatted:
      backlinks.sort(reverse=True)
      count=len(backlinks)
      mdlinks="".join("- [%s]\n" % l for l in backlinks)
      text="**%s backlink%s:**\n\n%s\n" % (count,'' if count==1 else 's',mdlinks)
#      return text
      return TEXT(text).formatted(req)
    return backlinks

#  def xget_backlinks(self,req):
#    """Checks through all posted articles for internal links.
#       Stores the links in md text format in the backlinks field.
#    """
#    # get the links
#    backlinks={}
#    rule=re.compile(r'(\[\ *)(\d+)')
#    for p in self.list(stage='posted',kind='page'):
#      links=[int(i[1]) for i in rule.findall(p.text)] # give list of page uids
#      for i in links:
#        if i in list(backlinks.keys()):
#          backlinks[i].append(p.uid)
#        else:
#          backlinks[i]=[p.uid]
#    backlinks=list(backlinks.items())
#    # format and store
#    for (uid,links) in backlinks:
#      count=len(links)
#      txt="**%s backlink%s:**\n\n%s\n" % (count,'' if count==1 else 's',mdlinks)
#      p=self.get(uid)
#      p.backlinks=txt
#      p.flush() # store the text
#    req.message='backlinks for all pages updated'
#    return self.redirect(req)
#  xget_backlinks.permit="admin page"


