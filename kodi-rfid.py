#!/usr/bin/env python

import os
import argparse
import imp
import subprocess
from threading import Lock

from src.WebUi import *

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'esp8266-rfid/tools/RFIDServer.py')

rfid = imp.load_source('RFIDServer', path)

from xbmcjson import XBMC, PLAYER_VIDEO
import json
import urllib
import sqlite3

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
  return parser.parse_args()


class kodiRFIDServer(rfid.RFIDServer):
  TYPES = ['album', 'addon', 'artist', 'video', 'url', 'action', 'command']
  ACTIONS = ['play_pause', 'mute','party_mode']
  YOUTUBE_ACTIONS = ['video', 'playlist']
  ADDONS = ['plugin.video.youtube', 'plugin.audio.radio_de', 'plugin.video.arteplussept']
  
  def __init__(self, args):
    self.args = args
    rfid.RFIDServer.__init__(self,'0.0.0.0', args.port)
    self.kodi = XBMC("%s/jsonrpc"%args.kodiurl)
    self.db = sqlite3.connect(args.database, check_same_thread=False)
    self.query_db = self.db.cursor()
    self.lock = Lock()
    self.last_tag = None

    try:
      self.query('''select * from albums_tags''')
    except:
      self.createDatabase()

  
  def play_arte(self, item):
    raw_shows =  self.kodi.Files.GetDirectory(directory='plugin://plugin.video.arteplussept/listing', properties=['title','genre'])
    for show in raw_shows["result"]['files']:
      if show['title'] == item:
        print "playing %s"%show['file']
        self.kodi.Player.Open(item={'file':show['file']})
        break
  
  def play_radio(self, item):
    self.kodi.Player.Open(item={'file':item})
  
  def play_pause(self):
    for p in self.get_active_player():
      self.kodi.Player.PlayPause(playerid=p['playerid'])
  
  def play_url(self, url):
    if os.path.isdir(url):
      self.kodi.Player.Open(item={'directory':url}, options={"shuffled":self.args.shuffle})
    else:
      self.kodi.Player.Open(item={'file':url})
  
  def party_mode(self, party=True):
    print self.kodi.Player.SetPartyMode(playerid=0, partymode=party)
  
  def delete_tag(self, tag):
    for t in ['albums_tags', 'addons_tags', 'artists_tags', 'actions_tags', 'urls_tags', 'commands_tags']:
      q = 'delete from %s where tag = "%s"'%(t, tag)
      self.query(q)
    self.commit()
  
  def play_youtube(self, uri):
    self.kodi.Player.Open(item={'file':uri})
    if 'playlist_id' in uri:
      self.kodi.Player.Open(item={'playlistid':1, 'position':0})
  
  def on_tag_received(self, tag):
      self.last_tag = tag
      if self.args.edit:
        self.delete_tag(tag)
        return self.register_tag(tag)
      albumid = self.get_album(tag)
      if albumid is not None:
        print albumid
        self.play_album(albumid)
      else:
        addon = self.get_addon(tag)
        if addon is not None:
          if addon[0] == 'plugin.video.arteplussept':
            self.play_arte(addon[2])
          elif addon[0] == 'plugin.audio.radio_de':
            self.play_radio(addon[2])
          elif addon[0] == 'plugin.video.youtube':
            self.play_youtube(addon[2])
        else:
          artistid = self.get_artist(tag)
          if artistid is not None:
            self.play_artist(artistid)
          else:
            action = self.get_action(tag)
            if action is not None:
              if action == 'play_pause':
                self.play_pause()
              elif action == 'party_mode':
                self.party_mode()
            else:
              url = self.get_url(tag)
              if url is not None:
                  self.play_url(url)
              else:
                command = self.get_command(tag)
                if command is not None:
                  subprocess.Popen(command, shell=True)
                else:
                  print "unknown tag %s"%tag

  def query(self, query):
    self.query_db.execute(query)

  def createDatabase(self):
    self.query('''CREATE TABLE albums_tags
      (albumid integer, tag text)''')
    self.query('''CREATE TABLE addons_tags
      (addonid text, tag text, parameters text)''')
    self.query('''CREATE TABLE artists_tags
      (artistid integer, tag text)''')
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

  def get_addons(self):
      return self.kodi.Addons.GetAddons(properties=['name'])["result"]["addons"]

  def get_artists(self):
    q = 'select * from artists_tags'
    res = self.fetchall(q)
    return res

  def get_artist(self, tag):
    q = 'select * from artists_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None

  def get_albums(self):
    q = 'select * from artists_tags'
    res = self.fetchall(q)
    return res

  def get_album(self, tag):
    q = 'select * from albums_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
  def get_addons(self):
    q = 'select * from addons_tags'
    res = self.fetchall(q)
    return res
  
  def get_addon(self, tag):
    q = 'select * from addons_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res
    return None
  
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
  
  def get_active_player(self):
    players = self.kodi.Player.GetActivePlayers()
    return players['result']
  
  def clear_playlist(self,pid = playlist_id):
    self.party_mode(False)
    self.kodi.Playlist.Clear(playlistid=pid)
    
  def play_artist(self, artistid, pid = playlist_id):
    self.clear_playlist(pid)
    self.kodi.Playlist.Add(playlistid=pid, item={'artistid':artistid})
    self.kodi.Player.Open(item={'playlistid':pid, 'position':0}, options={"shuffled":self.args.shuffle})
  
  def play_album(self, albumid, pid = playlist_id):
    self.clear_playlist(pid)
    self.kodi.Playlist.Add(playlistid=pid, item={'albumid':albumid})
    self.kodi.Player.Open(item={'playlistid':pid, 'position':0}, options={"shuffled":self.args.shuffle})
    
  def get_availables_albums(self):
      return self.kodi.AudioLibrary.GetAlbums(properties=['artist', 'title', 'thumbnail'])["result"]["albums"]
 
  def get_availables_artists(self):
      return self.kodi.AudioLibrary.GetArtists(properties=['thumbnail'])["result"]["artists"]

  def get_availables_addons(self):
      return self.ADDONS

  def get_availables_actions(self):
      return self.ACTIONS
  
  def get_availables_types(self):
      return self.TYPES

  def register_album(self, tag, albumid):
      q = 'insert into albums_tags (albumid, tag) values (%s,"%s")'%(albumid, tag)
      self.query(q)
      self.commit()

  def register_artist(self, tag, artistid):
      q = 'insert into artists_tags (artistid, tag) values ("%s","%s")'%(artistid, tag)
      self.query(q)
      self.commit()

  def register_url(self, tag, url):
      q = 'insert into urls_tags (url, tag) values ("%s","%s")'%(url, tag)
      self.query(q)
      self.commit()
      
  def register_command(self, tag, cmd):
      q = 'insert into commands_tags (command, tag) values ("%s","%s")'%(cmd, tag)
      self.query(q)
      self.commit()

  def register_action(self, tag, action):
      q = 'insert into actions_tags (action, tag) values ("%s","%s")'%(action, tag)
      self.query(q)
      self.commit()

  def register_tag(self, tag):
    print "registering %s"%tag
    print "please select a type of item"
    for i,t in enumerate(self.TYPES):
      print "- [%s] %s"%(i, t)
    tag_type = 0
    try:
      tag_type = int(raw_input('Select the type [0]: '))
    except:
      pass
    
    print "%s selected"%self.TYPES[tag_type]
    
    if tag_type == 0: # album
      albums = {}
      albums_raw = self.get_availables_albums()
      for album in albums_raw:
        albums[album['albumid']] = {'artist':album['artist'][0], 'title':album['title']}
      for key,value in albums.iteritems():
        print "[%s] - %s  %s"%(key, albums[key]['artist'], albums[key]['title'])
      
      try:
        albumid = int(raw_input('Select the album id: '))
      except:
        return False
      
      print "Selected : %s  %s"%(albums[albumid]['artist'], albums[albumid]['title'])
      self.register_album(tag,albumid)
      return True
    elif tag_type == 1: # addon:
      addons = {}
      index=0
      for addon in self.get_addons():
        if addon['type'] == 'xbmc.python.pluginsource':
          addons[index] = addon
          index += 1
      for index,addon in addons.iteritems():
        print "[%s] - %s ( %s )"%(index, addon['name'], addon['addonid'])
      
      addon_index = int(raw_input('Select the addon: '))
      print "selected %s"%(addons[addon_index]['name'])
      if addons[addon_index]['addonid'] == 'plugin.video.arteplussept':
        shows = []
        raw_shows =  self.kodi.Files.GetDirectory(directory='plugin://plugin.video.arteplussept/listing', properties=['title','genre'])
        
        for show in raw_shows["result"]['files']:
          if not show['title'] in shows:
            shows.append(show['title'])
        
        for index,show in enumerate(shows):
          print "[%s] - %s"%(index, shows[index])
        show_index = int(raw_input('Select the title: '))
        print "selected %s"%shows[show_index]
        q = 'insert into addons_tags (addonid, tag, parameters) values ("%s","%s","%s")'%(addons[addon_index]['addonid'], tag, shows[show_index])
        self.query(q)
        self.commit()
        return True
      elif addons[addon_index]['addonid'] == 'plugin.audio.radio_de':
        search = raw_raw_input('search for a radio ')
        raw_stations =  self.kodi.Files.GetDirectory(directory='plugin://plugin.audio.radio_de/stations/search/%s'%search)
        stations = []
        for station in raw_stations["result"]['files']:
          stations.append(station)
        for index,station in enumerate(stations):
          print "[%s] - %s"%(index, stations[index]['label'])
        station_index = int(raw_input('Select the title: '))
        print "selected %s"%stations[station_index]['label']
        q = 'insert into addons_tags (addonid, tag, parameters) values ("%s","%s","%s")'%(addons[addon_index]['addonid'], tag, stations[station_index]['file'])
        self.query(q)
        self.commit()
        return True
      elif addons[addon_index]['addonid'] == 'plugin.video.youtube':
        for i,t in enumerate(self.YOUTUBE_ACTIONS):
          print "- [%s] %s"%(i, t)
        action = 0
        try:
          action = int(raw_input('Select the action [0]: '))
        except:
          pass
        print "%s selected"%self.YOUTUBE_ACTIONS[action]
        
        itemid = raw_input('Select the id: ')
        
        if self.YOUTUBE_ACTIONS[action] == 'video':
          uri = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s'%itemid
        elif self.YOUTUBE_ACTIONS[action] == 'playlist':
          uri = 'plugin://plugin.video.youtube/play/?order=shuffle&playlist_id=%s'%itemid
        else:
          print 'Invalid action: %s'%action
          return False
        q = 'insert into addons_tags (addonid, tag, parameters) values ("plugin.video.youtube", "%s","%s")'%(tag, uri)
        self.query(q)
        self.commit()
        return True
      else:
        print "unmanaged plugin %s"%addons[addon_index]['addonid']
        return False
    elif tag_type == 2: # artist:
      artists = {}
      for artist in self.get_availables_artists():
        artists[artist['artistid']] = artist
      for key,value in artists.iteritems():
        print "[%s] - %s"%(key, artists[key]['artist'])
      
      artist_index = int(raw_input('Select the artist: '))
      print "selected %s"%artists[artist_index]['artist']
      self.register_artist(tag, artists[artist_index]['artistid'])
      return True
    elif tag_type == 4: # url:
      print "exemple uri: plugin://plugin.video.youtube/?action=play_video&videoid=7bMYhJ_UqnE, file://tmp/music.mp3"
      url = raw_input('please enter an uri to play: ')
      self.register_url(tag, url)
      return True
    elif tag_type == 5: # action:
      for i,t in enumerate(self.ACTIONS):
        print "- [%s] %s"%(i, t)
      action = 0
      try:
        action = int(raw_input('Select the action [0]: '))
      except:
        pass
      print "%s selected"%self.ACTIONS[action]
      self.register_action(self.ACTIONS[action])
      return True
    elif tag_type == 6: # command:
      cmd = raw_input('Enter the full command line: ')
      self.register_command(tag, cmd)
    else:
      print "unmanaged type %s"%self.TYPES[tag_type]
      
      
    return False

def main(args):
  if args.port is None:
   args.port = 4444
  else:
   args.port = int(args.port)
  
  if args.kodiurl is None:
    args.kodiurl = default_baseurl
  if args.database is None:
    args.database = default_database

  server = kodiRFIDServer(args)
  
  httpd = WebuiHTTPServer(("", 8889),server, WebuiHTTPHandler)
  httpd.start()
  
  server.listen()

main(parse_args())