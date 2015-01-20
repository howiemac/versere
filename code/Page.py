"""
override class for base.page

"""
from base.render import html
from base.lib import *
from base.Page import Page as basePage

import os, string, re

from calendar import month_name


class Page(basePage):

  def post(self,req):                                                                                                                      
    """fix date and format when posting a draft to diary category 442"""
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
    "autoposts oldest draft article, and updates backlinks"
    p=self.get_todays_article() 
    msg="no draft found" # default message
    if p: # if we have any draft
      p._posted(req) #post it
      msg= "%s posted on %s" % (p.uid,p.when) 
    self.get_backlinks(req) # update the backlinks (by crudely re-calculating the whole shebang - so this also allows for edit changes)
    return msg  
  autopost.permit="admin page"   

  @classmethod
  def get_todays_article(cls):
    """
    find the earliest draft article 
    """  
    articles=cls.list(stage='draft',orderby='uid',limit='0,1')
    return articles and articles[0] or None

  def get_backlinks(cls,req):
    "checks through all posted articles for internal links, and stores the link-count for each page in Page 7 text"
    # get the links 
    backlinks={}
    rule=re.compile(r'(\[\ *)(\d+)')
    for p in cls.list(stage='posted'):
      links=[int(i[1]) for i in rule.findall(p.text)] # give list of page uids
      for i in links:
        if i in backlinks.keys():
	  backlinks[i]+=1
	else:
	  backlinks[i]=1
    backlinks=backlinks.items()
    backlinks.sort(cmp=lambda x,y: cmp(x[1], y[1]), reverse=True) # sort in order of count
    # format and store  	    
    statpage=cls.get(7)
    txt=''
    for (uid,count) in backlinks:
      txt+="[%d]: %s\n" % (uid,count)
    statpage.text=txt
    statpage.flush() # store the text
    return statpage.view(req)
  get_backlinks.permit="admin page" 
  get_backlinks=classmethod(get_backlinks)
      
#=========================================

# extract diary entries from a special page
  
  def extract(self,req):
    "extract a new posted page for each diary entry per page 876"
    if self.uid!=876:
      return self.error(req,'can only extract from page 876')
    arts=self.text.split('\n==')
    nam=arts[0]
    for a in arts[1:]:
      lines=a.split('\n')
      p=self.new()
      p.kind='article'
      p.parent=442
      p.text='\n'.join(lines[1:-1])
#      p.name='%s %s' % (self.name,nam.replace(' :',',').replace(':',','))
      p.name='%s %s' % (self.name,nam.split(' ',1)[1].replace(' :',',').replace(':',',')) # remove leading day of week
      p.lineage='.1.442.'
      p.who=self.who
      p.stage='posted'
      p.group=1
      p.stamp()
      p.flush_page(req)
      p.seed_rating(req) 
      p.fix_diary_date(req)
      nam=lines[-1] #next title
    req.message='%s articles added' % (len(arts)-1,)  
    return self.view(req)

      


