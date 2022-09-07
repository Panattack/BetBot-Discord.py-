import http.client
import json
import datetime
import discord

football_image = "https://img.olympicchannel.com/images/image/private/t_social_share_thumb/f_auto/primary/qjxgsf7pqdmyqzsptxju"
basketball_image = "https://res.cloudinary.com/grohealth/image/upload/f_auto,fl_lossy,q_auto/v1581678662/DCUK/Content/iStock-959080376.jpg"
tennis_image = "https://photoresources.wtatennis.com/photo-resources/2019/08/15/dbb59626-9254-4426-915e-57397b6d6635/tennis-origins-e1444901660593.jpg?width=1200&height=630"
table_tennis_image = "https://media.istockphoto.com/photos/table-tennis-equipment-picture-id1192307192?k=20&m=1192307192&s=170667a&w=0&h=7OyzFcAo0AkMLdqjT-0WIYigvakYL8eHWJmGgtOZBtQ="
basketball_image = "https://thumbs.dreamstime.com/b/baseball-player-hitting-ball-bat-close-up-158391871.jpg"

bet_info = {}
"""
Example:
{1005051597040128091:[2,football,Manchester United]}
"""

year = datetime.datetime.today().year
day = datetime.datetime.today().day
month = datetime.datetime.today().month

if month < 10:
    month = '0' + str(month) 
if day < 10:
    day = '0' + str(day)

today = str(year) + '-' + str(month) + '-' + str(day)

conn = http.client.HTTPSConnection("api.sofascore.com")

payload = ""

headers = {
    'authority': "api.sofascore.com",
    'accept': "*/*",
    'accept-language': "el-GR,el;q=0.9",
    'cache-control': "max-age=0",
    'if-none-match': "W/^\^bce183a1e7^^",
    'origin': "https://www.sofascore.com",
    'referer': "https://www.sofascore.com/",
    'sec-ch-ua': "^\^Chromium^^;v=^\^104^^, ^\^"
    }
    
def extract_sport_data(sport,status):
    #print(status)
    conn.request("GET", "/api/v1/sport/"+ sport +"/scheduled-events/" + today, payload, headers)
    sport_data,league_list,hometeam_list,awayteam_list,score_home,score_away = [],[],[],[],[],[]
    res = conn.getresponse()
    data = res.read()

    jsondata = json.loads(data.decode("utf-8"))
    if jsondata['events'] == []:
        print(True)
    for game in jsondata['events']:
        league = game['tournament']['name']
        hometeam = game['homeTeam']['name']
        awayteam = game['awayTeam']['name']
        time = game['status']['description']
        if time == status:
            sport_data.append(league + "|" + hometeam + " versus " + awayteam)
            league_list.append(league)
            hometeam_list.append(hometeam)
            awayteam_list.append(awayteam)
        if time == "Ended":
            print(league," | ",hometeam, " vs ", awayteam, " -> ",time, sport)
            homescore = game['homeScore']['current']
            awayscore = game['awayScore']['current']
            score_home.append(homescore)
            score_away.append(awayscore)
    if status == 'Ended':
        return sport_data,score_home,score_away
    else:
        return sport_data

def colour_sport(sport):
    if sport == "football":
        farbe = discord.Colour.green()
    elif sport == "baseball":
        farbe = discord.Colour.red()
    elif sport == "tennis":
        farbe = discord.Colour.blue()
    elif sport == "table-tennis":
        farbe = discord.Colour.gold()
    else:
        farbe = discord.Colour.orange()
    return farbe

def get_sport_image(sport):
    if sport == "football":
        return football_image
    elif sport == "basketball":
        return basketball_image
    elif sport == "basketball":
        return basketball_image
    elif sport == "tennis":
        return tennis_image
    else:
        return table_tennis_image

"""It will help us see the roles of the player"""
def get_player_roles(ctx):
    roles_id,roles_char = [],[]
    for role in ctx.author.roles:
        roles_id.append(role.id)
        roles_char.append(role.name)
    return roles_char

class Data_Manager:
    def __init__(self):
        self.sports = ["football","basketball","tennis","baseball","ping-pong"]
        #ping-pong also references to table tennis,so we have to be careful
        self.football_data = []
        self.baseball_data = []
        self.basketball_data = []
        self.tennis_data = []
        self.table_tennis_data = []
    
    def get_data(self,sport):
        if sport == "football":
            return self.football_data
        elif sport == "basketball":
            return self.basketball_data
        elif sport == "baseball":
            return self.baseball_data
        elif sport == "tennis":
            return self.tennis_data
        else:
            return self.table_tennis_data
    
    def update_data(self,sport,ls,id):
        self.get_data(sport).append([id,ls])

    def Api_requests(self):
        for sp in self.sports:
            ended_matches,score_home,score_away = extract_sport_data(sp,'Ended')
            for member in bet_info:#for every player
                for bet in bet_info[member]:#for every bet
                    if bet is not []:
                        if bet[1] == sp:
                            for i in range(len(ended_matches)):
                                data = ended_matches[i].split(" versus ")
                                data_2 = data.split("|")
                                home = data_2[1]
                                away = data[1]
                                if (bet[2] in [home,away]) and (bet[3] in [home,away]):
                                    if score_home[i] == score_away[i]:
                                        #result == tie
                                        if bet[4] == 'tie':
                                            print('Tie')
                                            print('Gain 2x coins when you made the bet!!!')
                                    elif score_home[i] > score_away[i]:
                                        if home == bet[2]:
                                            print('You found the winner - home,take 4x the amount of coins that you have betted')
                                    else:
                                        if away == bet[2]:
                                            print('You found the winner - away,take 4x the amount of coins that you have betted')
                        #Must chech the bet info with the matches that have ended
        for sp in self.sports:
            n_id = 0
            self.get_data(sport=sp).clear()
            sport_ls = extract_sport_data(sp,'Not started')
            for new_data in sport_ls:
                self.update_data(sport=sp,ls=new_data,id=n_id)
                n_id += 1
        print(bet_info)