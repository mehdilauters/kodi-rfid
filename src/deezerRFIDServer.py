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
    self.current_item = {}
  
  
  def play_radio(self, serial, item):
    pass
  
  def play_pause(self, serial):
    self.current_item[serial] = {'id': 'play_pause', 'type':'action'}
  
  def volume_up(self, serial):
    self.current_item[serial] = {'id': 'volume_up', 'type':'action'}

  def volume_down(self, serial):
    self.current_item[serial] = {'id': 'volume_down', 'type':'action'}
    
  def next(self, serial):
    self.current_item[serial] = {'id': 'next', 'type':'action'}
  
  def delete_tag(self, tag):
    for t in ['albums_tags', 'addons_tags', 'artists_tags', 'actions_tags', 'urls_tags', 'commands_tags']:
      q = 'delete from %s where tag = "%s"'%(t, tag)
      self.query(q)
    self.commit()
  
  def on_tag_received(self, tag, serial = ''):
      self.last_tag[serial] = tag
      artistid = self.get_artist(serial, tag)
      if artistid is not None:
        self.play_artist(serial, artistid)
      else:
        albumid = self.get_album(serial, tag)
        if albumid is not None:
          self.play_album(serial, albumid)
        else:
          action = self.get_action(serial, tag)
          if action is not None:
            if action == 'play_pause':
              self.play_pause(serial)
            elif action == 'volume_up':
              self.volume_up(serial)
            elif action == 'volume_down':
              self.volume_down(serial)
            elif  action == 'next':
              self.next(serial)
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

  def get_artist(self,_serial, tag):
    q = 'select * from artists_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None

  def get_albums(self, _serial):
    q = 'select * from albums_tags where serial=%s'%_serial
    res = self.fetchall(q)
    return res

  def get_album(self, _serial, tag):
    q = 'select * from albums_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None
  
  def get_actions(self, _serial):
    q = 'select * from actions_tags where serial=%s'%_serial
    res = self.fetchall(q)
    return res
  
  def get_action(self, _serial, tag):
    q = 'select * from actions_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None
  
  def get_commands(self, _serial):
    q = 'select * from commands_tags where serial="%s"'%_serial
    res = self.fetchall(q)
    return res
  
  def get_command(self, _serial, tag):
    q = 'select * from commands_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[1]
    return None
  
  def commit(self):
    self.db.commit()
  
  
  def current_play(self, serial):
    item = {'id':'', 'type':''}
    try:
      item = self.current_item[serial]
    except:
      pass
    self.current_item[serial] = {'id':'', 'type':''}
    return item
  
  def clear_playlist(self,serial, pid):
    pass
    
  def play_artist(self, serial, artistid):
    self.current_item[serial] = {'id': artistid, 'type': 'artist'}
  
  def play_album(self, serial, albumid):
    self.current_item[serial] = {'id': albumid, 'type': 'album'}
    
  def get_availables_albums(self, serial):
      return
 
  def get_availables_artists(self, serial):
      return

  def get_availables_actions(self, serial):
      return self.ACTIONS
  
  def get_availables_types(self, serial):
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