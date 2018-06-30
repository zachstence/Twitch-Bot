import sys
import inspect
import types
from datetime import datetime
from random import randint

import helix

######################################################################
# All commands must have first two parameters user and channel
# Whatever is returned is converted to a string and displayed in chat
# Other than that, no restrictions on what commands can be!
######################################################################

################################## REGULAR COMMANDS ######################################
def commands(user, channel):
  funcs = inspect.getmembers(sys.modules[__name__], predicate=inspect.isfunction)
  funcs = [f[0] for f in funcs]
  s = "Commands: !" + funcs[0]
  for f in funcs[1:]:
    s += ", !" + f
  return s

def random(user, channel, min, max):
  return randint(int(min), int(max))

def localtime(user, channel):
  now = datetime.now()
  return now.strftime("%I:%M %p")



####################################### API COMMANDS #####################################
def followage(user, channel):
  return helix.get_follow_age(user, channel)

def followcount(user, channel):
  return helix.get_num_followers(channel)

def subcount(user, channel):
  return "Subcount is not available on this channel"

def uptime(user, channel):
  return "Uptime has not been implemented yet"
