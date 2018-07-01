import requests
import json
from datetime import datetime
import re

h = {'Client-ID':'vs31mew5ubdiem9rorz6fqhflii98i'}

def get_user_id(username):
  url = 'https://api.twitch.tv/helix/users?login=' + username
  r = requests.get(url, headers=h)

  user_info = json.loads(r.text)
  if len(user_info['data']) == 0:
    raise FileNotFoundError('\'{}\' is not a valid Twitch username'.format(username))

  return user_info['data'][0]['id']

def get_num_followers(user):
  url = 'https://api.twitch.tv/helix/users/follows?to_id=' + get_user_id(user)
  r = requests.get(url, headers=h)
  
  follow_info = json.loads(r.text)
  return (user, follow_info['total'])

def get_follow_age(user1, user2):
  url = 'https://api.twitch.tv/helix/users/follows?to_id=' + get_user_id(user2) + '&from_id=' + get_user_id(user1)
  r = requests.get(url, headers=h)

  follow_info = json.loads(r.text)

  if follow_info['total']:
    follow_date = follow_info['data'][0]['followed_at']
  
    ft = datetime.strptime(follow_date, '%Y-%m-%dT%H:%M:%SZ')
    now = datetime.now()
    duration = now - ft
  
    regex = re.search(r'(\d+) days, (\d+):(\d+):([\d+.])', str(duration))
    days = int(regex.group(1))
    hours = int(regex.group(2))
    mins = int(regex.group(3))
  
    # return days.lstrip('0') + " days, " + hours.lstrip('0') + " hours, " + mins.lstrip('0') + " minutes"
    return (user1, user2, days, hours, mins)
  else:
    return (user1, user2, 0, 0, 0)