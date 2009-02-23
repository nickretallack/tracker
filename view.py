### VIEWS
import web
from lib import auth
from lib.renderer import render
from database import db
import database

def usernames(rows):
  for row in rows:
    row['commissioner_name'] = db[row['commissioner']]['name']
  return rows
  
def make_timestamp():
  from datetime import datetime
  return datetime.now().isoformat()  



class index_view:
  def GET(self):
    commissions = usernames([row.value for row in database.commissions(db, descending=True)])
    finished = usernames([row.value for row in database.finished(db, descending=True)])
    deleted = usernames([row.value for row in database.deleted(db, descending=True)])

    return render("index", commissions=commissions, finished=finished, deleted=deleted, you=auth.get_you())

class form_view:
  def GET(self):
    return render("form", action="new", commission={}, you=auth.require_you())

  def POST(self):
    you = auth.require_you()
    record = {'type':'commission','commissioner':you.id, 'created':make_timestamp()}

    try:
      commission_ish(record)
    except ValueError:
      return render("form", action="new", commission=record, you=auth.get_you(), error="Unacceptable Price")
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

    web.seeother('/')

def commission_ish(record):
  you = auth.require_you()
  fields = ['price','summary','characters','mood','important','rating']
  params = web.input(button="new", file={})

  if params['file'].value:
    if not 'files' in record:
      record['files'] = {}
    record['files'][params['file'].filename] = True

  if params['button'] == "delete":
    if 'deleted' in record:
      record['deleted'] = None
    else:
      record['deleted'] = make_timestamp()
    
  elif params['button'] == "finish":
    if 'finished' in record:
      record['finished'] = None
    else:
      record['finished'] = make_timestamp()
    
  for field in fields:
    if field in params:
      record[field] = params[field]

  record['updated'] = make_timestamp()
    
  record['price'] = float('0'+record['price'])
  if record['price'] < 5: raise ValueError
  if record['price'] > 500: raise ValueError

  if params['button'] == 'new':
    record_id = db.create(record)
  else:
    record_id = record.id
    db[record.id] = record
    
  if params['file'].value:
    from lib.S3save import s3_save
    s3_save(params['file'], record_id)


class image_view:
  def GET(self, id, filename):
    from lib.S3save import s3_get_url
    return "<img src='%s'>" % s3_get_url(id,filename)



urls = (
    '/',      index_view,
    '/login', web.openid.host,
    '/settings', auth.settings_view,
    '/new', form_view,
    '/(.*)/(.*)', image_view,
    '/(.*)',  edit_view,
    )

application = web.application(urls, locals())