from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import json
from threading import Thread
import threading
import os
#import PrctlTool
import re
import urllib
import urlparse

class WebuiHTTPHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
      pass
    
    def _parse_url(self):
        # parse URL
        path = self.path.strip('/')
        sp = path.split('?')
        if len(sp) == 2:
            path, params = sp
        else:
            path, = sp
            params = None
        args = path.split('/')

        return path,params,args
    
    
    def _get_file(self, path):
      _path = os.path.join(self.server.www_directory,path)
      if os.path.exists(_path):
          try:
          # open asked file
              data = open(_path,'r').read()

              # send HTTP OK
              self.send_response(200)
              self.end_headers()

              # push data
              self.wfile.write(data)
          except IOError as e:
                self.send_500(str(e))
    
    def _get_types(self):
        types = self.server.app.TYPES
        data = json.dumps(types)
        self.wfile.write(data)
    
    def _get_last(self):
        last = self.server.app.last_tag
        data = json.dumps({'id':last})
        self.wfile.write(data)
    
    def _get_albums(self):
        albums = self.server.app.get_availables_albums()
        for i,a in enumerate(albums):
            albums[i]['thumbnail'] = "%s/image/%s"%(self.server.app.args.kodiurl,urllib.quote_plus(albums[i]['thumbnail']))
        data = json.dumps(albums)
        self.wfile.write(data)
        
    def _get_artists(self):
        artists = self.server.app.get_availables_artists()
        for i,a in enumerate(artists):
            artists[i]['thumbnail'] = "%s/image/%s"%(self.server.app.args.kodiurl,urllib.quote_plus(artists[i]['thumbnail']))
        data = json.dumps(artists)
        self.wfile.write(data)
    
    def _get_tags(self, _type):
      tags = []
      if _type == 'album':
          tags = self.server.app.get_albums()
      elif _type == 'addon':
          tags = self.server.app.get_addons()
      elif _type == 'artist':
          tags = self.server.app.get_artists()    
      elif _type == 'action':
          tags = self.server.app.get_actions()
      elif _type == 'url':
          tags = self.server.app.get_urls()
      elif _type == 'command':
          tags = self.server.app.get_commands()
      data = json.dumps(tags)
      self.wfile.write(data)
    
    def _delete(self, tag):
        self.server.app.delete_tag(tag)
        self.wfile.write(True)
    
    def _register(self, data):
        tagid = data['tagid'][0]
        if 'albumid' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_album(tagid, data['albumid'][0])
        elif 'artistid' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_artist(tagid, data['artistid'][0])
        elif 'url' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_url(tagid, data['url'][0])
        elif 'command' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_command(tagid, data['command'][0])
        self.wfile.write(True)
    
    def do_POST(self):
      path,params,args = self._parse_url()
      length = int(self.headers['Content-Length'])
      post = self.rfile.read(length)
      if len(args) == 1 and args[0] == 'delete.json':
        return self._delete(post)
      if len(args) == 1 and args[0] == 'register.json':
        return self._register(urlparse.parse_qs(urlparse.urlsplit(post).path))
    
    def do_GET(self):
        path,params,args = self._parse_url()
        if ('..' in args) or ('.' in args):
            self.send_400()
            return
        if len(args) == 1 and args[0] == '':
            path = 'index.html'
        if len(args) == 1 and args[0] == 'types.json':
            return self._get_types()
        elif len(args) == 1 and args[0] == 'tags.json':
            return self._get_tags(params.split("=")[1])
        if len(args) == 1 and args[0] == 'last.json':
            return self._get_last()
        if len(args) == 1 and args[0] == 'albums.json':
            return self._get_albums()
        if len(args) == 1 and args[0] == 'artists.json':
            return self._get_artists()
        
        return self._get_file(path)
      
class WebuiHTTPServer(ThreadingMixIn, HTTPServer, Thread):
  allow_reuse_address = True
  
  def __init__(self, server_address, app, RequestHandlerClass, bind_and_activate=True):
    HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
    threading.Thread.__init__(self)
    self.app = app
    self.www_directory = "www/"
    self.stopped = False
    
  def stop(self):
    self.stopped = True
    
  def run(self):
      #PrctlTool.set_title('webserver')
      while not self.stopped:
          self.handle_request()