import cfg

def commands(user):
  s = "Commands are: "
  commands = list(cfg.COMMANDS.keys())
  s += commands[0]
  for c in commands[1:]:
    s += ", " + c
  return s

from random import randint
def random(user, min, max):
  return randint(int(min), int(max))

####################################### API FUNCTIONS #####################################
import helix

def followage(user):
  return helix.get_follow_age(user, cfg.CHAN)




def subcount(user, channel):
  return "ERROR: not implemented yet"

def followcount(user, channel):
  return "ERROR: not implemented yet"

def uptime(user, channel):
  return "ERROR: not implemented yet"

from datetime import datetime
def localtime(user, channel):
  now = datetime.now()
  return now.strftime("%I:%M %p")