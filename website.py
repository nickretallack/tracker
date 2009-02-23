#!/usr/bin/env python

if __name__ == "__main__":
  import web
  web.config.debug = True

  from os import environ
  if 'AMAZON_SECRET' not in environ or 'AMAZON_KEY' not in environ:
    print "Set your AMAZON_KEY and AMAZON_SECRET environment variables"

  from database import view_sync
  view_sync()
  
  from view import application
  application.run()
