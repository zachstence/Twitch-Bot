import socket
import re
import time
from inspect import signature

import cfg
import commands
import helix

def chat(sock, msg):
  s = "PRIVMSG #{} :{}\r\n".format(cfg.CHAN, msg)
  sock.send(s.encode('utf-8'))

def ban(sock, user):
  chat(sock, ".ban {}\r\n".format(user))

def timeout(sock, user, secs):
  if secs == None:
    secs = cfg.DEFAULT_TIMEOUT
  chat(sock, ".timeout {} {}\r\n".format(user, secs))

def run_command(username, message):
  line = re.findall(r"\w+", message)
  c = line[0]
  line.insert(1, username)
  # try to call command function, if doesn't exist return 'Invalid command'
  try:
    func = getattr(commands, c)
  except AttributeError as e:
    return "Invalid command"
  else:
    sig = signature(func)
    num_args = len(sig.parameters)

    print(sig)

    # get additional parameters, if not enough given, return command suggestion
    args = ()
    try:
      for i in range(num_args):
        args += (line[i+1],)
    except IndexError as e:
      print("Error: " + str(e))
      params = " "
      for param in sig.parameters:
        params += "<" + param + "> "
      return 'Invalid command, try !' + c + params
    else:
      # call function with arguments
      return func(*args)


#############################################################################################################

try:

  s = socket.socket()
  s.connect((cfg.HOST, cfg.PORT))
  s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
  s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
  s.send("JOIN #{}\r\n".format(cfg.CHAN).encode("utf-8"))
  
  chat(s, "Bot connected!")
  
  # compile server response format into RegEx object
  CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
  
  # loop to talk to server
  while True:
    # get server response
    response = s.recv(1024).decode("utf-8")
  
    # else server pings us, pong back to let it know we're still connected
    if response == "PING :tmi.twitch.tv\r\n":
      s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
  
    # else reponse is a chat message
    else:
      # get username from response
      username = re.search(r"\w+", response).group(0)
  
      # subtract unnecessary information from response, leaving just chat message
      message = CHAT_MSG.sub("", response)
  
      # print chat message to console
      print(username + ": " + message)
  
      for pattern in cfg.BANNED:
        if re.match(pattern, message):
          ban(s, username)
          break
  
      for pattern, duration in cfg.TIMEOUT.items():
        if re.match(pattern, message):
          timeout(s, username, duration)
          break
  
      if message[0] == "!":
        chat(s, run_command(username, message))
  
    time.sleep(1 / cfg.RATE)
  
except KeyboardInterrupt as e:
  print("Bot disconnected!")
  chat(s, "Bot disconnected!")