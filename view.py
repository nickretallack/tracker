### VIEWS
import web
from lib import auth
from lib.renderer import render
from database import db
import database

class index_view:
  def GET(self):
    commissions = [row.value for row in database.commissions(db, descending=True)]
    for commission in commissions:
      commission['commissioner_name'] = db[commission['commissioner']]['name']
    return render("index", commissions=commissions, you=auth.get_you())

class form_view:
  def GET(self):
    return render("form", action="new", commission={}, you=auth.require_you())

  def POST(self):
    you = auth.require_you()
    record = {'type':'commission','commissioner':you.id}

    try:
      commission_ish(record)
    except ValueError:
      return render("form", action="new", commission=record, you=auth.get_you(), error="Unacceptable Price")

    db.create(record)
    web.seeother('/')

class edit_view:
  def GET(self, commission_id):
    you = auth.require_you()
    if commission_id not in db:
      raise web.notfound()
    commission = db[commission_id]
    if commission['commissioner'] != you.id and you['openids'] != ["xri://=!E68D.731D.F0A8.BFA8"]:
      raise web.notfound()
    
    #if web.openid.status() == "xri://=!E68D.731D.F0A8.BFA8":
    #  return "awesome powers"
    return render("form", action=commission_id, commission=commission, you=auth.get_you())

  def POST(self, commission_id):
    you = auth.require_you()
    if commission_id not in db:
      raise web.notfound()
    commission = db[commission_id]
    if commission['commissioner'] != you.id and you['openids'] != ["xri://=!E68D.731D.F0A8.BFA8"]:
      raise web.notfound()

    try:
      commission_ish(commission)
    except ValueError:
      return render("form", action=commission_id, commission=commission, you=you, error="Unacceptable Price")

    db[commission_id] = commission
    web.seeother('/')

def commission_ish(record):
  you = auth.require_you()
  fields = ['price','summary','characters','mood','important','rating']
  params = web.input()
  for field in fields:
    if field in params:
      record[field] = params[field]
      
  record['price'] = float('0'+record['price'])
  if record['price'] < 5: raise ValueError
  if record['price'] > 500: raise ValueError
  return record



urls = (
    '/',      index_view,
    '/login', web.openid.host,
    '/settings', auth.settings_view,
    '/new', form_view,
    '/(.*)',  edit_view,
    )

application = web.application(urls, locals())