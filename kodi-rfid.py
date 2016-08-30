import imp
rfid = imp.load_source('RFIDServer', './esp8266-rfid/tools/RFIDServer.py')

from xbmcjson import XBMC, PLAYER_VIDEO
import json
import urllib
import sqlite3

baseurl='http://localhost:8080'
database='./kodi-rfid.db'
playlist_id = 0

class kodiRFIDServer(rfid.RFIDServer):
  TYPES = ['album', 'addon', 'artist', 'video', 'url']
  
  def __init__(self, host, port):
    rfid.RFIDServer.__init__(self,host, port)
    self.kodi = XBMC("%s/jsonrpc"%baseurl)
    self.db = sqlite3.connect(database, check_same_thread=False)
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
  
  def play_radio(self, item):
    self.kodi.Player.Open(item={'file':item})
  
  def on_tag_received(self, tag):
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
        else:
          artistid = self.get_artist(tag)
          if artistid is not None:
            self.play_artist(artistid)
          else:
            self.register_tag(tag)

  def query(self, query):
    self.query_db.execute(query)

  def createDatabase(self):
    self.query('''CREATE TABLE albums_tags
      (albumid integer, tag text)''')
    self.query('''CREATE TABLE addons_tags
      (addonid text, tag text, parameters text)''')
    self.query('''CREATE TABLE artists_tags
      (artistid integer, tag text)''')

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
  
  def commit(self):
    self.db.commit()
  
  def clear_playlist(self,pid = playlist_id):
    self.kodi.Playlist.Clear(playlistid=pid)
    
  def play_artist(self, artistid, pid = playlist_id):
    self.clear_playlist(pid)
    self.kodi.Playlist.Add(playlistid=pid, item={'artistid':artistid})
    self.kodi.Player.Open(item={'playlistid':pid, 'position':0})
  
  def play_album(self, albumid, pid = playlist_id):
    self.clear_playlist(pid)
    self.kodi.Playlist.Add(playlistid=pid, item={'albumid':albumid})
    self.kodi.Player.Open(item={'playlistid':pid, 'position':0})
    

  def register_tag(self, tag):
    print "registering %s"%tag
    print "please select a type of item"
    for i,t in enumerate(self.TYPES):
      print "- [%s] %s"%(i, t)
    tag_type = 0
    try:
      tag_type = int(input('Select the type [0]: '))
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
        albumid = int(input('Select the album id: '))
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
      
      addon_index = int(input('Select the addon: '))
      print "selected %s"%(addons[addon_index]['name'])
      if addons[addon_index]['addonid'] == 'plugin.video.arteplussept':
        shows = []
        raw_shows =  self.kodi.Files.GetDirectory(directory='plugin://plugin.video.arteplussept/listing', properties=['title','genre'])
        
        for show in raw_shows["result"]['files']:
          if not show['title'] in shows:
            shows.append(show['title'])
        
        for index,show in enumerate(shows):
          print "[%s] - %s"%(index, shows[index])
        show_index = int(input('Select the title: '))
        print "selected %s"%shows[show_index]
        q = 'insert into addons_tags (addonid, tag, parameters) values ("%s","%s","%s")'%(addons[addon_index]['addonid'], tag, shows[show_index])
        self.query(q)
        self.commit()
        return True
      elif addons[addon_index]['addonid'] == 'plugin.audio.radio_de':
        search = raw_input('search for a radio ')
        raw_stations =  self.kodi.Files.GetDirectory(directory='plugin://plugin.audio.radio_de/stations/search/%s'%search)
        stations = []
        for station in raw_stations["result"]['files']:
          stations.append(station)
        for index,station in enumerate(stations):
          print "[%s] - %s"%(index, stations[index]['label'])
        station_index = int(input('Select the title: '))
        print "selected %s"%stations[station_index]['label']
        q = 'insert into addons_tags (addonid, tag, parameters) values ("%s","%s","%s")'%(addons[addon_index]['addonid'], tag, stations[station_index]['file'])
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
      
      artist_index = int(input('Select the artist: '))
      print "selected %s"%artists[artist_index]['artist']
      q = 'insert into artists_tags (artistid, tag) values ("%s","%s")'%(artists[artist_index]['artistid'], tag)
      self.query(q)
      self.commit()
      return True
    
    else:
      print "unmanaged type %s"%self.TYPES[tag_type]
      
      
    return False
      
port_num = 6677
kodiRFIDServer('0.0.0.0',port_num).listen()