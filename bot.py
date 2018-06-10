import socket
import re
import time

import cfg
import process_response

try:

  s = socket.socket()
  s.connect((cfg.HOST, cfg.PORT))
  s.send("CAP REQ :twitch.tv/membership\r\n".encode('utf-8'))
  s.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))
  s.send("CAP REQ :twitch.tv/commands\r\n".encode('utf-8'))

  s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
  s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
  s.send("JOIN #{}\r\n".format(cfg.CHAN).encode("utf-8")) 
  
  # loop to talk to server
  while True:
    # get server response
    response = s.recv(1024).decode("utf-8")

    # print response for debugging
    # print(response)
    
    # else server pings us, pong back to let it know we're still connected
    if response == "PING :tmi.twitch.tv\r\n":
      s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
  
    else:
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
        response_types[reponse_type](s, response)

    # time.sleep(1 / cfg.RATE)
  
except KeyboardInterrupt as e:
  print("\nBot disconnected!")
  # chat(s, "Bot disconnected!")