import imp
import os
import sqlite3
from threading import Lock

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../esp8266-rfid/tools/RFIDServer.py')
rfid = imp.load_source('RFIDServer', path)

class baseRFIDServer(rfid.RFIDServer):
  def __init__(self, args):
    self.args = args
    rfid.RFIDServer.__init__(self,'0.0.0.0', args.port)
    self.db = sqlite3.connect(args.database, check_same_thread=False)
    self.query_db = self.db.cursor()
    self.lock = Lock()
    self.last_tag = {}
    
    try:
      self.query('''select * from version''')
    except:
      self.createDatabase()
