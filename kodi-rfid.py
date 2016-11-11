#!/usr/bin/env python

import os
import argparse
import imp
import subprocess

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
  
  def __init__(self, args):
    self.args = args
    rfid.RFIDServer.__init__(self,'0.0.0.0', args.port)
    self.kodi = XBMC("%s/jsonrpc"%args.kodiurl)
    self.db = sqlite3.connect(args.database, check_same_thread=False)
    self.query_db = self.db.cursor()
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
    for t in ['albums_tags', 'addons_tags', 'artists_tags', 'actions_tags', 'urls_tags']:
      q = 'delete from %s where tag = "%s"'%(t, tag)
      self.query(q)
    self.commit()
  
  def play_youtube(self, uri):
    self.kodi.Player.Open(item={'file':uri})
    if 'playlist_id' in uri:
      self.kodi.Player.Open(item={'playlistid':1, 'position':0})
  
  def on_tag_received(self, tag):
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

  def fetchone(self, query):
    self.query_db.execute(query)
    return self.query_db.fetchone()

  def get_artist(self, tag):
    q = 'select * from artists_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None

  def get_album(self, tag):
    q = 'select * from albums_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
  def get_addon(self, tag):
    q = 'select * from addons_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res
    return None
  
  def get_action(self, tag):
    q = 'select * from actions_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
  def get_url(self, tag):
    q = 'select * from urls_tags where tag = "%s"'%tag
    res = self.fetchone(q)
    if res is not None:
      return res[0]
    return None
  
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
      albums_raw = self.kodi.AudioLibrary.GetAlbums(properties=['artist', 'title'])
      for album in albums_raw["result"]["albums"]:
        albums[album['albumid']] = {'artist':album['artist'][0], 'title':album['title']}
      for key,value in albums.iteritems():
        print "[%s] - %s  %s"%(key, albums[key]['artist'], albums[key]['title'])
      
      try:
        albumid = int(raw_input('Select the album id: '))
      except:
        return False
      
      print "Selected : %s  %s"%(albums[albumid]['artist'], albums[albumid]['title'])
      q = 'insert into albums_tags (albumid, tag) values (%s,"%s")'%(albumid, tag)
      self.query(q)
      self.commit()
      return True
    elif tag_type == 1: # addon:
      addons = {}
      addons_raw = self.kodi.Addons.GetAddons(properties=['name'])
      index=0
      for addon in addons_raw["result"]["addons"]:
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
      artists_raw = self.kodi.AudioLibrary.GetArtists()
      for artist in artists_raw["result"]["artists"]:
        artists[artist['artistid']] = artist
      for key,value in artists.iteritems():
        print "[%s] - %s"%(key, artists[key]['artist'])
      
      artist_index = int(raw_input('Select the artist: '))
      print "selected %s"%artists[artist_index]['artist']
      q = 'insert into artists_tags (artistid, tag) values ("%s","%s")'%(artists[artist_index]['artistid'], tag)
      self.query(q)
      self.commit()
      return True
    elif tag_type == 4: # url:
      print "exemple uri: plugin://plugin.video.youtube/?action=play_video&videoid=7bMYhJ_UqnE, file://tmp/music.mp3"
      url = raw_input('please enter an uri to play: ')
      q = 'insert into urls_tags (url, tag) values ("%s","%s")'%(url, tag)
      self.query(q)
      self.commit()
    elif tag_type == 5: # action:
      for i,t in enumerate(self.ACTIONS):
        print "- [%s] %s"%(i, t)
      action = 0
      try:
        action = int(raw_input('Select the action [0]: '))
      except:
        pass
      print "%s selected"%self.ACTIONS[action]
      if action == 0: # play_pause
        q = 'insert into actions_tags (action, tag) values ("%s","%s")'%(self.ACTIONS[action], tag)
        self.query(q)
        self.commit()
      elif action == 2: # party_mode
        q = 'insert into actions_tags (action, tag) values ("%s","%s")'%(self.ACTIONS[action], tag)
        self.query(q)
        self.commit()
      else:
        print "unmanaged action %s"%self.ACTIONS[action]
        return False
    elif tag_type == 6: # command:
      cmd = raw_input('Enter the full command line: ')
      q = 'insert into commands_tags (command, tag) values ("%s","%s")'%(cmd, tag)
      self.query(q)
      self.commit()
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

  kodiRFIDServer(args).listen()

main(parse_args())