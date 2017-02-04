#!/usr/bin/env python

import os
import imp
import subprocess
import pychromecast
from pychromecast.controllers.youtube import YouTubeController

from baseRFIDServer import *


class ChromecastRFIDServer(baseRFIDServer):
  TYPES = ['url', 'command']
  ACTIONS = ['play_pause', 'volume_up', 'volume_down', 'next']
  ADDONS = []
  
  def __init__(self, args):
    baseRFIDServer.__init__(self,args)
    self.name = 'Chromecast'
    chromecasts = pychromecast.get_chromecasts()
    self.chromecasts = [cc.device.friendly_name for cc in chromecasts]
    print 'found %s chromecast'%len(self.chromecasts)
    self.selected_chromecast = next(cc for cc in chromecasts if cc.device.friendly_name == self.chromecasts[0])
    print "selected %s"%self.selected_chromecast.device.friendly_name
    self.selected_chromecast.wait()
    self.mc = self.selected_chromecast.media_controller
    self.youtube = YouTubeController()
    self.selected_chromecast.register_handler(self.youtube)
  
  
  def play_url(self, url):
    self.youtube.play_video('nwIqTTRSjKg')
    print self.mc.status
  
  def play_pause(self):
    print self.mc.status
  
  def volume_up(self):
    self.current_item = {'id': 'volume_up', 'type':'action'}

  def volume_down(self):
    self.current_item = {'id': 'volume_down', 'type':'action'}
    
  def next(self):
    self.current_item = {'id': 'next', 'type':'action'}
  
  def delete_tag(self, tag):
    for t in ['actions_tags', 'urls_tags', 'commands_tags']:
      q = 'delete from %s where tag = "%s"'%(t, tag)
      self.query(q)
    self.commit()
  
  def on_tag_received(self, tag, serial = ''):
      self.last_tag[serial] = tag
      if self.args.edit:
        self.delete_tag(tag)
        return self.register_tag(tag)
      url = self.get_url(tag)
      if url is not None:
        self.play_url(url)
        print url
      else:
        action = self.get_action(tag)
        if action is not None:
          if action == 'play_pause':
            self.play_pause()
          elif action == 'volume_up':
            self.volume_up()
          elif action == 'volume_down':
            self.volume_down()
          elif  action == 'next':
            self.next()
          else:
            print "action not available"
            
      

  def query(self, query):
    self.query_db.execute(query)

  def createDatabase(self):
    self.query('''CREATE TABLE version
      (version integer)''')
    self.query('''CREATE TABLE actions_tags
      (action string, tag text)''')
    self.query('''CREATE TABLE urls_tags
      (url string, tag text)''')
    self.query('''CREATE TABLE commands_tags
      (command string, tag text)''')

  def fetchall(self, query):
    with self.lock:
      self.query_db.execute(query)
      return self.query_db.fetchall()

  def fetchone(self, query):
    self.query_db.execute(query)
    return self.query_db.fetchone()

  def get_actions(self):
    q = 'select * from actions_tags'
    res = self.fetchall(q)
    return res
  
  def get_action(self, tag):
    q = 'select * from actions_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
  def get_commands(self):
    q = 'select * from commands_tags'
    res = self.fetchall(q)
    return res
  
  def get_command(self, tag):
    q = 'select * from commands_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
  def commit(self):
    self.db.commit()
  
  
  def clear_playlist(self,pid):
    pass

  def get_availables_actions(self):
      return self.ACTIONS
  
  def get_availables_types(self):
      return self.TYPES

  def get_urls(self):
    q = 'select * from urls_tags'
    res = self.fetchall(q)
    return res
  
  def get_url(self, tag):
    q = 'select * from urls_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
  def register_url(self, tag, url):
    q = 'insert into urls_tags (url, tag) values ("%s","%s")'%(url, tag)
    self.query(q)
    self.commit()
  
  def register_tag(self, tag):
    print "registering %s"%tag
  
      
      
    return False