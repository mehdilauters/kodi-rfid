import imp
rfid = imp.load_source('RFIDServer', './esp8266-rfid/tools/RFIDServer.py')

from xbmcjson import XBMC, PLAYER_VIDEO
import json
import urllib
baseurl='http://localhost'

class kodiRFIDServer(rfid.RFIDServer):
  def __init__(self, host, port):
    rfid.RFIDServer.__init__(self,host, port)
    
  def on_tag_received(self, tag):
      print "tag %s received"%tag


xbmc = XBMC("%s/jsonrpc"%baseurl)


port_num = 6677
kodiRFIDServer('0.0.0.0',port_num).listen()