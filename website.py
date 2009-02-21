#!/usr/bin/env python

if __name__ == "__main__":
  import web
  web.config.debug = True

  from database import view_sync
  view_sync()
  
  from view import application
  application.run()
