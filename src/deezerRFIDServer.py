#!/usr/bin/env python

import os
import imp
import subprocess


from baseRFIDServer import *

from deezer.deezer_player import *

class deezerRFIDServer(baseRFIDServer):
  TYPES = ['album', 'addon', 'artist', 'url', 'action', 'command']
  ACTIONS = ['play_pause', 'mute','party_mode']
  ADDONS = []
  
  def __init__(self, args):
    baseRFIDServer.__init__(self,args)
    
    self.user_access_token = u"fr49mph7tV4KY3ukISkFHQysRpdCEbzb958dB320pM15OpFsQs"  # SET your user access token
    self.your_application_id = u"190262"  # SET your application id
    self.your_application_name = u"PythonSampleApp"  # SET your application name
    self.your_application_version = u"00001"  # SET your application version
    if platform.system() == u'Windows':
      self.user_cache_path = u"c:\\dzr\\dzrcache_NDK_SAMPLE"  # SET the user cache path, the path must exist
    else:
      self.user_cache_path = u"/tmp"  # SET the user cache path, the path must exist
    self.connection = Connection(self, self.your_application_id, self.your_application_name,
                                     self.your_application_version, self.user_cache_path,
                                     self.connection_event_callback, 0, 0)
  
  
  # We set the connection callback to launch the player after connection is established
  @staticmethod
  def connection_event_callback(handle, event, userdata):
    """Listen to events and call the appropriate functions
    :param handle: The connect handle.
    :type: p_type
    :param event: The corresponding event.
        Must be converted using Connection.get_event
    :type: dz_connect_event_t
    :param userdata: Any data you want to be passed and used here
    :type: ctypes.py_object
    :return: int
    """
    # We retrieve our deezerApp
    #app = cast(userdata, py_object).value
    event_type = Connection.get_event(event)
    print(u"++++ CONNECT_EVENT ++++ {0}".format(ConnectionEvent.event_name(event_type)))
    # After User is authenticated we can start the player
    #if event_type == ConnectionEvent.USER_LOGIN_OK:
        #app.player.load(app.context.dz_content_url)
    #if event_type == ConnectionEvent.USER_LOGIN_FAIL_USER_INFO:
        #app.shutdown()
    return 0
  
  
  def play_radio(self, item):
    self.kodi.Player.Open(item={'file':item})
  
  def play_pause(self):
    for p in self.get_active_player():
      self.kodi.Player.PlayPause(playerid=p['playerid'])
  
  def delete_tag(self, tag):
    for t in ['albums_tags', 'addons_tags', 'artists_tags', 'actions_tags', 'urls_tags', 'commands_tags']:
      q = 'delete from %s where tag = "%s"'%(t, tag)
      self.query(q)
    self.commit()
  
  def on_tag_received(self, tag):
      self.last_tag = tag
      if self.args.edit:
        self.delete_tag(tag)
        return self.register_tag(tag)
      print "==="

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
  
  def clear_playlist(self,pid):
    pass
    #self.party_mode(False)
    #self.kodi.Playlist.Clear(playlistid=pid)
    
  def play_artist(self, artistid, pid):
    pass
    #self.clear_playlist(pid)
    #self.kodi.Playlist.Add(playlistid=pid, item={'artistid':artistid})
    #self.kodi.Player.Open(item={'playlistid':pid, 'position':0}, options={"shuffled":self.args.shuffle})
  
  def play_album(self, albumid, pid):
    pass
    #self.clear_playlist(pid)
    #self.kodi.Playlist.Add(playlistid=pid, item={'albumid':albumid})
    #self.kodi.Player.Open(item={'playlistid':pid, 'position':0}, options={"shuffled":self.args.shuffle})
    
  def get_availables_albums(self):
      return self.kodi.AudioLibrary.GetAlbums(properties=['artist', 'title', 'thumbnail'])["result"]["albums"]
 
  def get_availables_artists(self):
      return self.kodi.AudioLibrary.GetArtists(properties=['thumbnail'])["result"]["artists"]


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
  
      
      
    return False