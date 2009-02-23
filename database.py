from settings import db_server, db_name
import couchdb
import socket

server = couchdb.Server(db_server)

try:
  if db_name not in server:
    server.create(db_name)
  db = server[db_name]
except socket.error:
  print "Make sure CouchDB is running"
  exit()

map_users = """
function(doc){
  if(doc.type == "user"){
    emit(doc.slug, {"name":doc.name, "slug":doc.slug})
  }
}"""

map_commissions = """
function(doc){
  if(doc.type == "commission" && !doc.finished && !doc.deleted){
    emit(doc.price, {"price":doc.price,"commissioner":doc.commissioner,"id":doc._id,"summary":doc.summary,"files":doc.files})
  }
}"""

map_finished = """
function(doc){
  if(doc.type == "commission" && doc.finished && !doc.deleted){
    emit(doc.finished, {"price":doc.price,"commissioner":doc.commissioner,"id":doc._id,"summary":doc.summary,"files":doc.files})
  }
}"""

map_deleted = """
function(doc){
  if(doc.type == "commission" && doc.deleted){
    emit(doc.deleted, {"price":doc.price,"commissioner":doc.commissioner,"id":doc._id,"summary":doc.summary,"files":doc.files})
  }
}"""

""""characters":doc.characters,"mood":doc.mood,
"important":doc.important,"rating":doc.rating,"""


from couchdb.design import ViewDefinition as View
users  = View('users','show',map_users)
commissions = View('commissions','fresh',map_commissions)
finished = View('commissions','finished',map_finished)
deleted = View('commissions','deleted',map_deleted)
views = [users,commissions,finished,deleted]

def view_sync():
  View.sync_many(db,views,remove_missing=True)
