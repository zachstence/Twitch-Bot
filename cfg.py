# cfg.py
HOST = "irc.twitch.tv"                        # the Twitch IRC server
PORT = 6667                                   # always use port 6667!
NICK = "zachbot_08"                           # your Twitch username, lowercase
#PASS = "oauth:cx870jnlihu9vq3cczvnxogmm27lng" # your Twitch OAuth token (zach_08_bot)
PASS = "oauth:ejz0ktdncdrz79tbduejlro7d838ye" # your Twitch OAuth token (zachbot_08)
CHAN = "zach_08"                             # the channel you want to join
# CHAN = input("Enter channel to connect to: ")

RATE = float(20)/30                           # messages per second

BANNED = [
  "banned"
]

DEFAULT_TIMEOUT = 600
TIMEOUT = {
  "time me out" : 10
}