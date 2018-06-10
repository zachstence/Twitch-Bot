import re
import cfg
import user_commands
from inspect import signature
from inspect import Parameter



###################################### MEMBERSHIP ######################################
def JOIN(socket, response):
  # chat(socket, "Bot connected!")
  print("Bot connected!")

def PART(socket, response):
  # chat(socket, "Bot disconnected!")
  print("Bot disconnected!")



###################################### TAGS ######################################
def CLEARCHAT(socket, response):
  print('CLEARCHAT')

def GLOBALUSERSTATE(socket, response):
  print('GLOBALUSERSTATE')

# @badges=<badges>;color=<color>;display-name=<display-name>;emotes=<emotes>;id=<id-of-msg>;mod=<mod>;room-id=<room-id>;subscriber=<subscriber>;tmi-sent-ts=<timestamp>;turbo=<turbo>;user-id=<user-id>;user-type=<user-type> :<user>!<user>@<user>.tmi.twitch.tv PRIVMSG #<channel> :<message>
def PRIVMSG(socket, response):
  try:
    username = get_field(response, 'username')
    # channel = get_field(response, 'channel')
    message = get_field(response, 'message')
  
    print(username + ": " + message)
  
    for pattern in cfg.BANNED:
      if re.match(pattern, message):
        ban(socket, username)
        break
    for pattern, duration in cfg.TIMEOUT.items():
      if re.match(pattern, message):
        timeout(socket, username, duration)
        break
    if message[0] == "!":
      chat(socket, run_command(username, message))
  except Exception as e:
    print(e)
    print("ERROR PARSING PRIVMSG")
    with open('errors.txt', 'w') as f:
      f.write(response)
      f.write(str(e) + '\n')
  
def ROOMSTATE(socket, response):
  print('ROOMSTATE')

# @badges=<badges>;color=<color>;display-name=<display-name>;emotes=<emotes>;id=<id-of-msg>;login=<user>;mod=<mod>;msg-id=<msg-id>;room-id=<room-id>;subscriber=<subscriber>;system-msg=<system-msg>;tmi-sent-ts=<timestamp>;turbo=<turbo>;user-id=<user-id>;user-type=<user-type> :tmi.twitch.tv USERNOTICE #<channel> :<message>
def USERNOTICE(socket, response):
  notice_type = get_field(response, 'msg-id')
  if notice_type in ['sub', 'resub']:
    username = get_field(response, 'login')
    months = get_field(response, 'msg-param-months')
    print(username + " subscribed for " + months + " months")
  elif notice_type == 'subgift':
    username = get_field(response, 'login')
    recipient = get_field(response, 'msg-param-recipient-display-name')
    print(username + " gifted a sub to " + recipient)

def USERSTATE(socket, response):
  print('USERSTATE')



###################################### COMMANDS ######################################
def HOSTTARGET(socket, response):
  print('HOSTTARGET')

def NOTICE(socket, response):
  print('NOTICE')

def RECONNECT(socket, response):
  print('RECONNECT')



###################################### util functions ######################################
def get_field(response, field):
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


def chat(sock, msg):
  s = "PRIVMSG #{} :{}\r\n".format(cfg.CHAN, msg)
  sock.send(s.encode('utf-8'))


def ban(sock, user):
  chat(sock, ".ban {}\r\n".format(user))


def timeout(sock, user, secs):
  if secs == None:
    secs = cfg.DEFAULT_TIMEOUT
  chat(sock, ".timeout {} {}\r\n".format(user, secs))


def run_command(user, message):
  line = re.findall(r"\w+", message)
  c = line[0]
  line.insert(1, user)
  params = line[1:]
  try:
    func = getattr(user_commands, c)
    if not callable(func):
      raise TypeError
  except (AttributeError, TypeError):
    return 'Invalid command. Type "!commands" for a list of commands.'
  else:
    sig = signature(func)
    required_params = []
    optional_params = []
    for key, value in sig.parameters.items():
      if value.default is Parameter.empty:
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
