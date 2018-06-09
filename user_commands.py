import cfg

##############################################################################
# user must be the first argument to every function
# optional (default) arguments must come after required arguments
##############################################################################



################################## REGULAR FUNCTIONS ######################################
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


####################################### API FUNCTIONS #####################################
import helix

def followage(user, channel=cfg.CHAN):
  return helix.get_follow_age(user, channel)

def followcount(user, channel=cfg.CHAN):
  return helix.get_num_followers(channel)





def subcount(user, channel):
  return "ERROR: not implemented yet"

def uptime(user, channel):
  return "ERROR: not implemented yet"

from datetime import datetime
def localtime(user, channel):
  now = datetime.now()
  return now.strftime("%I:%M %p")