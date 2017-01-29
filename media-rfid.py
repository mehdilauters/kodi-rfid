#!/usr/bin/env python

import os
import argparse
import imp
import subprocess
from threading import Lock

from src.WebUi import *
from src.kodiRFIDServer import *
from src.deezerRFIDServer import *


default_baseurl='http://localhost:8080'
default_database='./kodi-rfid.db'
playlist_id = 0


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--port', help='tcp server port')
  parser.add_argument("-d", "--database", help="tags database")
  parser.add_argument("-k", "--kodiurl", help="tags database")
  parser.add_argument("-e", "--edit", action='store_true', help="tags database")
  parser.add_argument("-s", "--shuffle", action='store_true', help="shuffle added items")
  parser.add_argument("-m", "--mode", action='store_true', help="deezer version")
  parser.add_argument("-w", "--www", help="webui port")
  return parser.parse_args()


def main(args):
  if args.port is None:
   args.port = 4444
  else:
   args.port = int(args.port)
  
  if args.kodiurl is None:
    args.kodiurl = default_baseurl
  if args.database is None:
    args.database = default_database
  
  server = None
  if not args.mode:
    server = kodiRFIDServer(args)
  else:
    server = deezerRFIDServer(args)
  
  if args.www is not None:
    args.www = int(args.www)
    httpd = WebuiHTTPServer(("", args.www),server, WebuiHTTPHandler)
    httpd.www_directory = '%s/www'%os.path.dirname(os.path.realpath(__file__))
    httpd.start()
  
  server.listen()

try:
  main(parse_args())
except KeyboardInterrupt:
  pass
