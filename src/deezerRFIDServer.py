#!/usr/bin/env python

import os
import imp
import subprocess


from baseRFIDServer import *


class deezerRFIDServer(baseRFIDServer):
  TYPES = ['album', 'artist', 'action', 'command']
  ACTIONS = ['play_pause', 'volume_up', 'volume_down', 'next']
  ADDONS = []
  
  def __init__(self, args):
    baseRFIDServer.__init__(self,args)
    self.name = 'deezer'
    self.current_item = {'id':'', 'type':''}
  
  
  def play_radio(self, item):
    pass
  
  def play_pause(self):
    self.current_item = {'id': 'play_pause', 'type':'action'}
  
  def volume_up(self):
    self.current_item = {'id': 'volume_up', 'type':'action'}

  def volume_down(self):
    self.current_item = {'id': 'volume_down', 'type':'action'}
    
  def next(self):
    self.current_item = {'id': 'next', 'type':'action'}
  
  def delete_tag(self, tag):
    for t in ['albums_tags', 'addons_tags', 'artists_tags', 'actions_tags', 'urls_tags', 'commands_tags']:
      q = 'delete from %s where tag = "%s"'%(t, tag)
      self.query(q)
    self.commit()
  
  def on_tag_received(self, tag, serial = ''):
      self.last_tag[serial] = tag
      if self.args.edit:
        self.delete_tag(tag)
        return self.register_tag(tag)
      artistid = self.get_artist(tag)
      if artistid is not None:
        self.play_artist(artistid)
      else:
        albumid = self.get_album(tag)
        if albumid is not None:
          self.play_album(albumid)
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
    self.query('''CREATE TABLE albums_tags
      (serial integer, albumid integer, tag text)''')
    self.query('''CREATE TABLE addons_tags
      (serial integer, addonid text, tag text, parameters text)''')
    self.query('''CREATE TABLE artists_tags
      (serial integer, artistid integer, tag text)''')
    self.query('''CREATE TABLE actions_tags
      (serial integer, action string, tag text)''')
    self.query('''CREATE TABLE urls_tags
      (serial integer, url string, tag text)''')
    self.query('''CREATE TABLE commands_tags
      (serial integer, command string, tag text)''')

  def fetchall(self, query):
    with self.lock:
      self.query_db.execute(query)
      return self.query_db.fetchall()

  def fetchone(self, query):
    self.query_db.execute(query)
    return self.query_db.fetchone()

  def get_addons(self):
      return []

  def get_artists(self, _serial):
    q = 'select * from artists_tags where serial=%s'%_serial
    res = self.fetchall(q)
    return res

  def get_artist(self, tag):
    q = 'select * from artists_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None

  def get_albums(self, _serial):
    q = 'select * from artists_tags where serial=%s'%_serial
    res = self.fetchall(q)
    return res

  def get_album(self, tag):
    q = 'select * from albums_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None
  
  def get_actions(self, _serial):
    q = 'select * from actions_tags where serial=%s'%_serial
    res = self.fetchall(q)
    return res
  
  def get_action(self, tag):
    q = 'select * from actions_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None
  
  def get_commands(self, _serial):
    q = 'select * from commands_tags serial="%s"'%_serial
    res = self.fetchall(q)
    return res
  
  def get_command(self, tag):
    q = 'select * from commands_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None
  
  def commit(self):
    self.db.commit()
  
  
  def current_play(self):
    item = self.current_item
    self.current_item = {'id':'', 'type':''}
    return item
  
  def clear_playlist(self,pid):
    pass
    
  def play_artist(self, artistid):
    self.current_item = {'id': artistid, 'type': 'artist'}
  
  def play_album(self, albumid):
    self.current_item = {'id': albumid, 'type': 'album'}
    
  def get_availables_albums(self):
      return
 
  def get_availables_artists(self):
      return

  def get_availables_actions(self):
      return self.ACTIONS
  
  def get_availables_types(self):
      return self.TYPES

  def register_album(self, serial, tag, albumid):
      q = 'insert into albums_tags (serial, albumid, tag) values (%s, %s,"%s")'%(serial, albumid, tag)
      self.query(q)
      self.commit()

  def register_artist(self, serial, tag, artistid):
      q = 'insert into artists_tags (serial, artistid, tag) values (%s, "%s","%s")'%(serial, artistid, tag)
      self.query(q)
      self.commit()
      
  def register_command(self, serial, tag, cmd):
      q = 'insert into commands_tags (serial, command, tag) values (%s, "%s","%s")'%(serial, cmd, tag)
      self.query(q)
      self.commit()

  def register_action(self, serial, tag, action):
      q = 'insert into actions_tags (serial, action, tag) values (%s, "%s","%s")'%(serial, action, tag)
      self.query(q)
      self.commit()
  

  
  def register_tag(self, serial, tag):
    print "registering %s"%tag
  
      
      
    return False