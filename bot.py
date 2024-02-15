'''
truefinalsBot

Based on Nathan's work here: https://github.com/NRS048/Discord-TrueFinals-Webhook

This script integrates truefinals.com, discord and an OBS stream overlay.
The true finals API is polled for called, active and compelted matches.
A discord channel is notified via a webhook.
Data is witten to a json file for use in robot.html as a stream overlay.

TODO
- Get clock info from the arena timer.

KNOWN ISSUES
- This script is designed for only one match to be active at a time. There are issues with multiple matches being active at once.
'''

import requests
import json
import time
# import serial

# true finals API info
headers = {
    "x-api-user-id": "ENTER HERE",
    "x-api-key": "ENTER HERE"
}

# bot name displayed in discord
botName = "EventBot"

# discord webhook URL
url = "https://discord.com/api/webhooks/ENTERHERE"

# ids of your truefinals brackets (will be found inside the actual page url
# EX. https://truefinals.com/tournament/12345678abcdefgh
ids = ["bf2a4479166448fc", "555be80d228b4daf"]

def getPlayer(playerId, playerData):
    for q in playerData:
        if playerId == q['id']:
            return q


def getWinner(matchId, matchData):
    for w in matchData[matchId]["slots"]:
        if w["slotState"] == "winner" or w["slotState"] == "winner_by_default":
            return w["playerID"]


states = {}
oldStates = {}

for ID in ids:
    i = 0
    req = requests.get("https://truefinals.com/api/v1/tournaments/" + ID, headers=headers)
    tourney = json.loads(req.text)
    # print(tourney)
    req.close()
    games = tourney['games']

    states[ID] = []
    oldStates[ID] = []
    while i < len(games):
        states[ID].append(games[i]["state"])
        i += 1
        time.sleep(1)

jsonData = {
  "p1name": "Player1 (0-0)",
  "p1icon": "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",
  "p2name": "Player2 (0-0)",
  "p2icon": "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",
  "timer": "",
  "winner": "Player1",
  "scroller": "",
  "showPlayers": False,
  "showWinner": False,
  "showScroller": True,
  "p1shortName": "Player1",
  "p2shortName": "Player2",
}

stopShow = 0
time.sleep(1)
scroller = ["", "", ""]

# ser = serial.Serial('COM5', 115200, timeout=1)

while True: #forever loop, until match is over...
    print("loop")

    try:
        # ser.write(b'1')
        # print(ser.readline())
        # jsonData['timer'] = ""

        for ID in ids:
            req = requests.get("https://truefinals.com/api/v1/tournaments/" + ID, headers=headers)
            tourney = {}
            tourney = json.loads(req.text)
            # print(tourney)
            req.close()

            players = {}
            players = tourney['players']
            games = tourney['games']

            oldStates[ID].clear()
            i = 0
            data = {
                "username": botName
            }
            while i < len(games):
                oldStates[ID].append("d")
                oldStates[ID][i] = games[i]["state"]
                p1Id = games[i]["slots"][0]["playerID"]
                p2Id = games[i]["slots"][1]["playerID"]
                if i == len(oldStates[ID]) or i == len(states[ID]):
                    oldStates[ID].append("d")
                    states[ID].append("d")
                if not oldStates[ID][i] == states[ID][i]:
                    match oldStates[ID][i]:
                        case "called":
                            data["embeds"] = [
                                {
                                    "type": "rich",
                                    "title": tourney['title'] + " - Match " + games[i]['name'] + " - On Deck!",
                                    "description": "",
                                    "color": 0xF4B400,
                                    "url": "https://truefinals.com/api/v1/tournaments/" + ID,
                                    "fields": [
                                        {'name': getPlayer(p1Id, players)['name'] + " (" + str(getPlayer(p1Id, players)['wins']) + "-" + str(getPlayer(p1Id, players)['losses']) + ") vs "
                                                 + getPlayer(p2Id, players)['name'] + " (" + str(getPlayer(p2Id, players)['wins']) + "-" + str(getPlayer(p2Id, players)['losses']) + ")", "value": ""}
                                    ]
                                }
                            ]
                            result = requests.post(url, json=data)
                        case "active":
                            data["embeds"] = [
                                {
                                    "type": "rich",
                                    "title": tourney['title'] + " - Match " + games[i]['name'] + " - Starting Now!",
                                    "description": "",
                                    "color": 0xff0000,
                                    "url": "https://truefinals.com/api/v1/tournaments/" + ID,
                                    "fields": [
                                        {'name': getPlayer(p1Id, players)['name'] + " (" + str(getPlayer(p1Id, players)['wins']) + "-" + str(getPlayer(p1Id, players)['losses']) + ") vs "
                                                 + getPlayer(p2Id, players)['name'] + " (" + str(getPlayer(p2Id, players)['wins']) + "-" + str(getPlayer(p2Id, players)['losses']) + ")", "value": ""}
                                    ]
                                }
                            ]
                            result = requests.post(url, json=data)
                            jsonData["showPlayers"] = True
                            jsonData["showWinner"] = False
                            jsonData['p1name'] = getPlayer(p1Id, players)['name'] + " (" + str(getPlayer(p1Id, players)['wins']) + "-" + str(getPlayer(p1Id, players)['losses']) + ")"
                            jsonData["p1icon"] = getPlayer(p1Id, players)['photoUrl']
                            jsonData['p1shortName'] = getPlayer(p1Id, players)['name']
                            jsonData["p2name"] = getPlayer(p2Id, players)['name'] + " (" + str(getPlayer(p2Id, players)['wins']) + "-" + str(getPlayer(p2Id, players)['losses']) + ")"
                            jsonData["p2icon"] = getPlayer(p2Id, players)['photoUrl']
                            jsonData["p2shortName"] = getPlayer(p2Id, players)['name']
                            stopShow = 0
                        case "done":
                            #print(games)
                            wid = getWinner(i, games)
                            data["embeds"] = [
                                {
                                    "type": "rich",
                                    "title": tourney['title'] + " - Match " + games[i]['name'] + " - Complete!",
                                    "description": "",
                                    "color": 0x1ba300,
                                    "url": "https://truefinals.com/api/v1/tournaments/" + ID,
                                    "fields": [
                                        {'name': getPlayer(p1Id, players)['name'] + " (" + str(getPlayer(p1Id, players)['wins']) + "-" + str(getPlayer(p1Id, players)['losses']) + ") vs "
                                                 + getPlayer(p2Id, players)['name'] + " (" + str(getPlayer(p2Id, players)['wins']) + "-" + str(getPlayer(p2Id, players)['losses']) + ")", "value": ""},
                                        {'name': getPlayer(wid, players)['name'] + " WINS!", "value": ""}
                                    ]
                                }
                            ]
                            result = requests.post(url, json=data)
                            if jsonData["p1shortName"] == getPlayer(p1Id, players)['name'] and jsonData["p2shortName"] == getPlayer(p2Id, players)['name']:
                                jsonData["showWinner"] = True
                                jsonData["winner"] = getPlayer(wid, players)['name']
                                stopShow = 5
                            scroller.pop(0)
                            scroller.append(getPlayer(p1Id, players)['name'] + " vs " + getPlayer(p2Id, players)['name'] + " = " + getPlayer(wid, players)['name'] + " WINS!")
                            jsonData["scroller"] = "Recent Matches: " + scroller[0] + " | " + scroller[1] + " | " + scroller[2]
                        case _:
                            pass
                    states[ID][i] = oldStates[ID][i]
                i += 1

        #print(stopShow)
        if stopShow == 1:
            jsonData["showPlayers"] = False
            jsonData["showWinner"] = False
            stopShow -= 1
        elif stopShow > 0:
            stopShow -= 1

        f = open("data.json", "w")
        f.write(json.dumps(jsonData))
        f.close()

        winners = [0,0,0]
        if not tourney['endTime'] is None: #tourney is complete
            print("tournament complete!")
            print(players)
            for pl in players:
                place = getPlayer(pl['id'], players)['placement']
                if place is not None and place == 1:
                    winners[0] = pl['id']
                if place is not None and place == 2:
                    winners[1] = pl['id']
                if place is not None and place == 3:
                    winners[2] = pl['id']

            data["embeds"] = [
                {
                    "type": "rich",
                    "title": tourney['title'] + " Tournament Complete!",
                    "description": "",
                    "color": 0xffc0cb,
                    "url": "https://truefinals.com/api/v1/tournaments/" + ID,
                    "fields": [
                        {
                            'name': "First Place:",
                            'value': getPlayer(winners[0], players)['name'] + " (" + str(getPlayer(winners[0], players)['wins']) + "-" + str(getPlayer(winners[0], players)['losses']) + ") "
                        },
                        {
                            'name': "Second Place:",
                            'value': getPlayer(winners[1], players)['name'] + " (" + str(
                                getPlayer(winners[1], players)['wins']) + "-" + str(
                                getPlayer(winners[1], players)['losses']) + ") "
                        },
                        {
                            'name': "Third Place:",
                            'value': getPlayer(winners[2], players)['name'] + " (" + str(
                                getPlayer(winners[2], players)['wins']) + "-" + str(
                                getPlayer(winners[2], players)['losses']) + ") "
                        },
                    ]
                }
            ]
            result = requests.post(url, json=data)
            #print("exiting...")
            #break

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print('http request error: ')
        print(e)

    except ValueError as e:
        print('Decoding JSON has failed')
        print(req.text)

    time.sleep(2)
