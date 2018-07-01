import sys
import inspect
import types
import json
from datetime import datetime
from random import randint

import helix

######################################################################
# All commands must have first two parameters chatter and channel
# Whatever is returned is converted to a string and displayed in chat
# Other than that, no restrictions on what commands can be!
######################################################################


################################## REGULAR COMMANDS ######################################
def commands(chatter, channel):
  with open(channel + '_commands.json', 'r') as f:
    channel_commands = json.load(f)
  commands = list(channel_commands.keys())

  funcs = inspect.getmembers(sys.modules[__name__], predicate=inspect.isfunction)
  commands += [f[0] for f in funcs]
  
  s = "Commands: !" + commands[0]
  for f in commands[1:]:
    s += ", !" + f
  return s


def random(chatter, channel, *args):
  if len(args) >= 2:
    return randint(int(args[0]), int(args[1]))
  else:
    raise TypeError('Missing arguments, try \'!random <min> <max>\'')


def localtime(chatter, channel):
  now = datetime.now()
  return now.strftime("%I:%M %p")

# add custom command or overwrite if it already exists
def addcustom(chatter, channel, *args):
  try:
    name = args[0]
    out = " ".join(args[1:])
    
    # check to see if its a bot command already
    funcs = inspect.getmembers(sys.modules[__name__], predicate=inspect.isfunction)
    funcs = [f[0] for f in funcs]
    if name in funcs:
      return 'Command \'!{}\' already exists'.format(name)
  
    with open(channel + '_commands.json', 'r') as f:
      channel_commands = json.load(f)
    
    channel_commands[name] = out
    s = json.dumps(channel_commands, indent=2)
    
    with open(channel + '_commands.json', 'w') as f:
      f.write(s)
  
    return 'Added \'!{}\' : \'{}\''.format(name, out)
  except IndexError:
    return 'Specify a custom command and its description: !addcustom <name> <description>'


def removecustom(chatter, channel, *args):
  try:
    name = args[0]
    with open(channel + '_commands.json', 'r') as f:
      channel_commands = json.load(f)
    
    if name in channel_commands.keys():
      del channel_commands[name]
      s = json.dumps(channel_commands, indent=2)
      with open(channel + '_commands.json', 'w') as f:
        f.write(s)
      return '\'!{}\' command removed'.format(name)
    else:
      return '\'!{}\' is not a command'.format(name)
  except IndexError:
    return 'Specify a custom command to remove: !removecustom <name>'

####################################### API COMMANDS #####################################
def followage(chatter, channel, *args):
  try:
    # how long has chatter been following channel they're in
    if len(args) == 0:
      dur = helix.get_follow_age(chatter, channel)

    # how long has chatter been following channel argument
    elif len(args) == 1:
      dur = helix.get_follow_age(chatter, args[0])

    # how long has chatter argument been following channel argument, ignore additional args
    else:
      dur = helix.get_follow_age(args[0], args[1])

    return '{} has been following {} for {:,} days, {} hours and {} minutes'.format(dur[0], dur[1], dur[2], dur[3], dur[4])

  except FileNotFoundError as fnfe:
    return fnfe

def followcount(chatter, channel, *args):
  # follower count of current channel
  if len(args) == 0:
    info = helix.get_num_followers(channel)
  else:
  # follower count of channel argument
    info = helix.get_num_followers(args[0])
  return '{} has {:,} followers'.format(info[0], info[1])

def subcount(chatter, channel):
  return "Subcount has not been implemented yet"

def uptime(chatter, channel):
  return "Uptime has not been implemented yet"