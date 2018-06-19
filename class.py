import socket
from multiprocessing.pool import ThreadPool
import time
import re
import process_response


class Bot:
  _host = 'irc.twitch.tv'
  _port = 6667
  _rate = float(20)/30

  def __init__(self, bot_username, oauth, channel):
    self._bot_username = bot_username
    self._oauth = oauth
    self._channel = channel

  def setup(self):
    self._socket = socket.socket()
    self._socket.connect((self._host, self._port))
    self._socket.send("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
    self._socket.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))
    self._socket.send("CAP REQ :twitch.tv/commands\r\n".encode('utf-8'))

    self._socket.send("PASS {}\r\n".format(self._oauth).encode("utf-8"))
    self._socket.send("NICK {}\r\n".format(self._bot_username).encode("utf-8"))
    self._socket.send("JOIN #{}\r\n".format(self._channel).encode("utf-8")) 

    self._pool = ThreadPool(processes=1)

  def chat_from_commandline(self):
    self.chat(input())

  def loop(self):
    while True:
      async_result = self._pool.apply_async(self.chat_from_commandline)

      response = self._socket.recv(1024).decode("utf-8")

      if response == "PING :tmi.twitch.tv\r\n":
        self._socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
      
      else:
        m = re.search(r"tmi\.twitch\.tv (\w+) #", response)
        if m != None:
          reponse_type = m.group(1)

          response_types = {
            'JOIN'            : process_response.JOIN,
            'PART'            : process_response.PART,
  
            'CLEARCHAT'       : process_response.CLEARCHAT,
            'GLOBALUSERSTATE' : process_response.GLOBALUSERSTATE,
            'PRIVMSG'         : process_response.PRIVMSG,
            'ROOMSTATE'       : process_response.ROOMSTATE,
            'USERNOTICE'      : process_response.USERNOTICE,
            'USERSTATE'       : process_response.USERSTATE,
  
            'HOSTTARGET'      : process_response.HOSTTARGET,
            'NOTICE'          : process_response.NOTICE,
            'RECONNECT'       : process_response.RECONNECT
          }

          response_types[reponse_type](self._socket, response)

      time.sleep(self._rate)

  def chat(self, msg):
    s = "PRIVMSG #{} :{}\r\n".format(self._channel, msg)
    self._socket.send(s.encode('utf-8'))






oauths = {
  'zach_08'     : 'oauth:xws48cnw2mtfdgh37rw1m36dfhb2up',
  'zachbot_08'  : 'oauth:ejz0ktdncdrz79tbduejlro7d838ye',
  'zach_08_bot' : 'oauth:cx870jnlihu9vq3cczvnxogmm27lng'
}

user = 'zach_08'
channel = 'giantwaffle'

b = Bot(user, oauths[user], channel)
b.setup()
b.loop()