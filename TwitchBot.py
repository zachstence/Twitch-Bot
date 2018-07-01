import sys
import time
import socket
import json
import re
from multiprocessing.pool import ThreadPool
from inspect import signature, Parameter, getmembers, isfunction

from random import randint
from datetime import datetime

import user_commands

class TwitchBot:
  _host = 'irc.twitch.tv'
  _port = 6667

  

  def __init__(self, bot_username, oauth, channel, rate=20/30, banned_words=[], timeout_words=[], verbose=2, cl_chat=0, timeout=600):
    self._bot_username = bot_username
    self._oauth = oauth
    self._channel = channel
    self._rate = rate

    self._banned_words = banned_words
    self._timeout_words = timeout_words

    # verbose 0 = no output
    # verbose 1 = print notices (subs, raids, hosts, etc)
    # verbose 2 = additionally print all chat messages
    # verbose 3 = additionally print raw server response
    self._verbose = verbose

    # cl_chat 0 = not able to chat from command line
    # cl_chat 1 = able to chat form command line
    self._cl_chat = cl_chat

    # timeout = default length for a timeout in seconds
    self._timeout = timeout


  ### CONNECT AND LOOP
  def connect(self):
    self._socket = socket.socket()
    self._socket.connect((self._host, self._port))
    self._socket.send("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
    self._socket.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))
    self._socket.send("CAP REQ :twitch.tv/commands\r\n".encode('utf-8'))

    self._socket.send("PASS {}\r\n".format(self._oauth).encode("utf-8"))
    self._socket.send("NICK {}\r\n".format(self._bot_username).encode("utf-8"))
    self._socket.send("JOIN #{}\r\n".format(self._channel).encode("utf-8")) 

    self._pool = ThreadPool(processes=1)

  def loop(self):
    while True:
      command_sent = False
      response = self._socket.recv(1024).decode("utf-8")

      # Output verbose if response enabled
      if self._verbose >= 3:
        print(response)

      # Async command line chat if enabled
      if self._cl_chat:
        self._pool.apply_async(self.__commandline_chat)

      if response == "PING :tmi.twitch.tv\r\n":
        self._socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
      
      else:
        m = re.search(r"tmi\.twitch\.tv (\w+) #", response)
        if m != None:
          response_type = m.group(1)
          command_sent = getattr(self, '_TwitchBot__' + response_type)(response)

      if command_sent:
        time.sleep(self._rate)


  ########## RESPONSE PROCESSING ##########
  # OTHER FUNCTIONS #
  @staticmethod
  def __get_field(response, field):
    if field == "username" or field == "channel" or field == "message":
      m = re.search(r" :(.*?)!.*?@.*?\.tmi\.twitch\.tv \w+ #(.*?) :(.*)$", response)
      if m != None:
        if field == "username":
          return m.group(1)
        elif field == "channel":
          return m.group(2)
        elif field == "message":
          return m.group(3)
      else:
        return None
    else:
      regex = re.escape(field) + r"=(.*?);"
      m = re.search(regex, response)

      if m != None:
        return m.group(1)
      else:
        return None

  @staticmethod
  def __run_command(user, channel, message):
    
    line = re.findall(r"\w+", message)
    c = line[0]
    args = line[1:]

    # check for custom channel commands first
    with open(channel + '_commands.json', 'r') as f:
      channel_commands = json.load(f)
    if c in channel_commands.keys():
      return channel_commands[c]

    # then check for bot commands
    commands = getmembers(user_commands, predicate=isfunction)
    commands = dict((name, func) for name, func in commands)
    try:
      func = commands[c]
      return func(user, channel, *tuple(args))
    except KeyError as ke:
      return '{} is not a valid command'.format(ke)
    except TypeError as te:
      return te

  def __commandline_chat(self):
    self.__chat(input())

  def __chat(self, msg):
    s = "PRIVMSG #{} :{}\r\n".format(self._channel, msg)
    self._socket.send(s.encode('utf-8'))

  def __ban(self, user):
    self.__chat(".ban {}\r\n".format(user))

  def __timeout(self, user):
    self.__chat(".timeout {} {}\r\n".format(user, self._timeout))


  # MEMBERSHIP #
  def __JOIN(self, response):
    # chat(socket, "Bot connected!")
    print("Bot connected!")

  def __PART(self, response):
    # chat(socket, "Bot disconnected!")
    print("Bot disconnected!")


  # TAGS #
  def __CLEARCHAT(self, response):
    print('CLEARCHAT')

  def __GLOBALUSERSTATE(self, response):
    print('GLOBALUSERSTATE')

  def __PRIVMSG(self, response):
    try:
      username = TwitchBot.__get_field(response, 'username')
      channel = TwitchBot.__get_field(response, 'channel')
      message = TwitchBot.__get_field(response, 'message')
    
      if self._verbose >= 2:
        print(username + ": " + message)
    
      for bw in self._banned_words:
        if re.match(bw, message):
          self.__ban(username)
          return True
      for tw in self._timeout_words:
        if re.match(tw, message):
          self.__timeout(username)
          return True

      if message[0] == "!":
        self.__chat(TwitchBot.__run_command(username, channel, message))
        return True

    except Exception as e:
      raise
      print(e)
      print("ERROR PARSING PRIVMSG")
      with open('errors.txt', 'a+') as f:
        f.write(response)
        f.write(str(e) + '\n')

  def __ROOMSTATE(self, response):
    print('ROOMSTATE')

  def __USERNOTICE(self, response):
    notice_type = TwitchBot.__get_field(response, 'msg-id')
    if notice_type in ['sub', 'resub']:
      username = TwitchBot.__get_field(response, 'login')
      months = TwitchBot.__get_field(response, 'msg-param-months')
      print('*** ' + username + ' subscribed for ' + months + ' months ***')

    elif notice_type == 'subgift':
      username = TwitchBot.__get_field(response, 'login')
      recipient = TwitchBot.__get_field(response, 'msg-param-recipient-display-name')
      print('*** ' + username + ' gifted a sub to ' + recipient + ' ***')

  def __USERSTATE(self, response):
    print('USERSTATE')


  # TWITCH COMMANDS #
  def __HOSTTARGET(self, response):
    print('HOSTTARGET')

  def __NOTICE(self, response):
    print('NOTICE')

  def __RECONNECT(self, response):
    print('RECONNECT')




#############################################################################################


user = sys.argv[1]
channel = sys.argv[2]

with open('oauths.json') as f:
  oauths = json.load(f)

tb = TwitchBot(user, oauths[user], channel, cl_chat=True, banned_words=['ban'], timeout_words=['timeout'])
tb.connect()
tb.loop()