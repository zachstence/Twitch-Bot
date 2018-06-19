import cfg

##############################################################################
# user must be the first argument to every function
# optional (default) arguments must come after required arguments
##############################################################################



################################## REGULAR COMMANDS ######################################
import sys
import inspect
import types
def is_function_local(object):
    return isinstance(object, types.FunctionType) and object.__module__ == __name__
def commands(user):
  this = sys.modules[__name__]
  funcs = inspect.getmembers(sys.modules[__name__], predicate=is_function_local)
  funcs = [f[0] for f in funcs]
  funcs.remove('is_function_local')
  s = "Commands: !"
  s += funcs[0]
  for f in funcs[1:]:
    s += ", !" + f
  return s


from random import randint
def random(user, min, max):
  return randint(int(min), int(max))


# import requests
# def strawpoll(user, title, option1, option2, more_options=None):

  


####################################### API COMMANDS #####################################
import helix

def followage(user, channel=cfg.CHAN):
  return helix.get_follow_age(user, channel)

def followcount(user, channel=cfg.CHAN):
  return helix.get_num_followers(channel)

from datetime import datetime
def localtime(user):
  now = datetime.now()
  return now.strftime("%I:%M %p")






def subcount(user, channel=cfg.CHAN):
  return "Subcount is not available on this channel"

def uptime(user, channel=cfg.CHAN):
  return "Uptime has not been implemented yet"
