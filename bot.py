import socket
import re
import time
from inspect import signature

import cfg
import user_commands
import process_response
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

import inspect
def run_command(user, message):
  line = re.findall(r"\w+", message)
  c = line[0]
  line.insert(1, user)
  params = line[1:]
  try:
    func = getattr(commands, c)
    if not callable(func):
      raise TypeError
  except (AttributeError, TypeError):
    return 'Invalid command. Type "!commands" for a list of commands.'
  else:
    sig = signature(func)
    required_params = []
    optional_params = []
    for key, value in sig.parameters.items():
      if value.default is inspect.Parameter.empty:
        required_params.append(key)
      else:
        optional_params.append(key)
  
    args = ()
    try:
      for p in range(len(required_params)):
        args += (params[p],)
    except:
      # missing required params
      params = " "
      for param in list(sig.parameters)[1:]:
        params += "<" + param + "> "
      return 'Invalid command, try !' + c + params
    else:
      del params[:len(required_params)]
  
    try:
      for p in range(len(optional_params)):
        args += (params[p],)
    except:
      # missing optional params, ok
      pass

    return func(*args)

#############################################################################################################
# subscription command         <tags>:tmi.twitch.tv USERNOTICE #<channel> :<message>
# private message command      <tags>:<user>!<user>@<user>.tmi.twitch.tv PRIVMSG #<channel> :<message>
# in general                   tmi.twitch.tv <COMMAND> #<channel>



try:

  s = socket.socket()
  s.connect((cfg.HOST, cfg.PORT))
  s.send("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
  s.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))
  s.send("CAP REQ :twitch.tv/commands\r\n".encode('utf-8'))

  s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
  s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
  s.send("JOIN #{}\r\n".format(cfg.CHAN).encode("utf-8"))
  
  # chat(s, "Bot connected!")
  
  # compile server response format into RegEx object
  CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
  
  # loop to talk to server
  while True:
    # get server response
    response = s.recv(1024).decode("utf-8")
    
  
    # else server pings us, pong back to let it know we're still connected
    if response == "PING :tmi.twitch.tv\r\n":
      s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
  
    else:
      print(response)
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

        # call appropriate function to process response
        response_types[reponse_type]()



#     # else reponse is a chat message
#     else:
#       # get username from response
#       username = re.search(r"\w+", response).group(0)
#   
#       # subtract unnecessary information from response, leaving just chat message
#       message = CHAT_MSG.sub("", response)
#   
#       # print chat message to console
#       print(username + ": " + message)
#   
#       for pattern in cfg.BANNED:
#         if re.match(pattern, message):
#           ban(s, username)
#           break
#   
#       for pattern, duration in cfg.TIMEOUT.items():
#         if re.match(pattern, message):
#           timeout(s, username, duration)
#           break
#   
#       if message[0] == "!":
#         chat(s, run_command(username, message))
#   
#     time.sleep(1 / cfg.RATE)
#   
except KeyboardInterrupt as e:
  print("\nBot disconnected!")
  # chat(s, "Bot disconnected!")