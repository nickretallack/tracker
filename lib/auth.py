import web
from database import db

import database as dbview
from renderer import render

# Modified slugging routines originally stolen from patches to django
def slugify(value):
  """ Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.  """
  import unicodedata
  import re
  #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
  value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
  return re.sub('[-\s]+', '-', value)


class settings_view:
  def GET(self):
    return render("settings", you=require_you())
  
  def POST(self):
    you = require_you()
    params = web.input(name='')

    unique = True
    name = params['name']
    if name and name != you.get('name',None):
      from helper import slugify
      slug = slugify(name)
      for row in dbview.users(db, startkey=slug, endkey=slug):
        if slug == row.key:
          unique = False
          break
    
      if unique:
        you['name'] = name
        you['slug'] = slug
    elif not name and 'name' in you:
      # blanking your name makes you anonymous, and makes your page inaccessible
      del you['name']
      del you['slug']

    db[you.id] = you

    if unique:
      web.redirect('/')
    else:
      return render('settings', errors="Sorry, that name's taken!", you=you)

def get_you():
  openid = web.openid.status()
  if openid:
    key = "user-%s" % openid
    if key in db:
      return db[key]
    else:
      from random_name import random_name
      from time import time
      while True:
        unique = True
        name = random_name("%s-%d" % (openid,time()))
        slug = slugify(name)
        for row in dbview.users(db, startkey=slug, endkey=slug):
          if slug == row.key:
            unique = False
            break

        if unique:
          break

      you = {'type':'user', 'openids':[openid], "name":name, "slug":slug}
      db[key] = you
      return you


def require_you():
  you = get_you()
  if not you:
    raise web.HTTPError("401 unauthorized", {}, "You must be logged in")
  return you