#-------------------NOTES-------------------#
#->This bot can be used only in one guild that has the nessecary roles.
#->Special Thanks to:
#.....https://docs.replit.com/tutorials/discord-role-bot
#.....https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.utils import get
import re
from bet_scraper import colour_sport, Data_Manager, get_player_roles, get_sport_image, bet_info

# Json imports and Betting Scoresofa,also importing http.client for taking the nessecary info
import http.client
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SERVER_ID = os.getenv('SERVER_ID')
intents = discord.Intents.all()
intents.members = True
#Bot is a subclass from Discord.Client.Eventually you can do everything from Client
bot = commands.Bot(command_prefix='!',intents = intents,help_command=None)

#dictionary for storing info about members for the games and more

dict_info = {}
"""
Panos (ect) :
coins: 0(ect)
"""

player_info = {}
"""
BetBot (ect) :
id: OEDNOEOCS?PNCA (ect)
"""

@bot.event
async def on_ready():
    """It's a classic function that connects the bot with the user"""
    global d_m #This is the data_Manager object that is going to schedule the data update
    d_m = Data_Manager()
    print(f'{bot.user.name} has connected to Discord!')
    print(f'{GUILD} was found!')
    for guild in bot.guilds:
         if guild.name == GUILD:
             break
    members = ([str(member.id) for member in guild.members])
    names = ([str(member.name) for member in guild.members])
    i = 0
    for m in names:
        dict_info.update({m:5})
    for m in members:
        player_info.update({names[i]:m})
        bet_info[m] = []
        i = i+1
    print(f'Guild Members:\n - {names}')
    print(f'Info {dict_info} - {player_info}')
    print(f'Bet info {bet_info}')
    #guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)

@bot.command(name = "GN",help = 'Guess the number from a starting number to the limit of your preference!')
async def guess_number(ctx):
    """
    ->The classic Guess Number Game.
    Now the player has the privileges to define the left and right limit.
    The right limit must be bigger than the left and always numeric(the limits)  
    """
    """bet-test command"""
    await ctx.send(f"We play the game: Guess the number\n Tell me the left limit\n") 
    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and \
        msg.content.isnumeric()

    msg1 = await bot.wait_for("message", check=check)
    await ctx.send(f'Tell me the right limit')
    msg2 = await bot.wait_for("message", check=check)
    if int(msg1.content) > int(msg2.content):
        await ctx.send(f'2nd number is bigger than the 1st number')
    elif msg1.content == msg2.content:
        await ctx.send(f'Same number,the answer is obvious')
    else:
        n = random.randint(int(msg1.content),int(msg2.content))
        await ctx.send(f'Guess the number between {int(msg1.content)} - {int(msg2.content)}')
        msg = await bot.wait_for("message", check=check)
        if int(msg.content) == n:
            await ctx.send(f"{msg.author.mention} ,you guessed right!!!Congrants 🙂")
            dict_info.update({str(msg.author)[:-5]:int(dict_info.get(str(msg.author)[:-5])) + 5})
            print(dict_info.get(str(msg.author)))
        else:
            await ctx.send(f"{msg.author.mention} ,you guessed wrong 😔!!!The right answer is {n}")
    return

#------ Livescore functions ------
@bot.command(name = 'lfootball')
async def live_football(ctx):
    roles_char = get_player_roles(ctx)
    if "football" in roles_char:
        "show the live matches in football and the live score"
        await live("football",ctx)

@bot.command(name = 'ltennis')
async def live_tennis(ctx):
    roles_char = get_player_roles(ctx)
    if "tennis" in roles_char:
        await live("tennis",ctx)

@bot.command(name = 'lbaseball')
async def live_baseball(ctx):
    roles_char = get_player_roles(ctx)
    if "baseball" in roles_char:
        await live("baseball",ctx)

@bot.command(name = 'lbasketball')
async def live_basketball(ctx):
    roles_char = get_player_roles(ctx)
    if "basketball" in roles_char:
        await live("basketball",ctx)

@bot.command(name = 'ltable-tennis')
async def live_table_tennis(ctx):
    roles_char = get_player_roles(ctx)
    if "ping-pong" in roles_char:
        await live("table-tennis",ctx)

#--------Main livescore function--------#
async def live(sport,ctx):
    farbe = colour_sport(sport)
    
    conn = http.client.HTTPSConnection("api.sofascore.com")
    payload = ""

    headers = {
        'authority': "api.sofascore.com",
        'accept': "*/*",
        'accept-language': "el-GR,el;q=0.9",
        'cache-control': "max-age=0",
        'if-none-match': "W/^\^d8d050b312^^",
        'origin': "https://www.sofascore.com",
        'referer': "https://www.sofascore.com/",
        'sec-ch-ua': "^\^Chromium^^;v=^\^104^^, ^\^"
        }

    conn.request("GET", "/api/v1/sport/"+sport+"/events/live", payload, headers)

    res = conn.getresponse()
    data = res.read()

    jsondata = json.loads(data.decode("utf-8"))
    if jsondata['events']== []:
        await ctx.send(f'No {sport} match right now')
    else:
        live_data,leagues = [],[]
        for game in jsondata['events']:
                league = game['tournament']['name']
                hometeam = game['homeTeam']['name']
                awayteam = game['awayTeam']['name']
                homescore = game['homeScore']['current']
                awayscore = game['awayScore']['current']
                time = game['status']['description']
                v = hometeam + " " + str(homescore) + " - " + awayteam + " " + str(awayscore)+" ("+time+")"
                live_data.append(v)
                leagues.append(league)
        length = len(live_data)
        i = 0
        while True:
            embed = discord.Embed(
            title = "Live "+ sport,
            description = "Watch every score from your favorite sport here live!",
            color = farbe
            )
            for k in range(i,i+10):
                if k == length:
                    break
                embed.add_field(name=leagues[k],value=live_data[k],inline=False)
            embed.set_thumbnail(url=get_sport_image(sport=sport))
            await ctx.send(embed=embed)
            i = i + 10
            if (i >= length):
                break
    return

# Betting matches 
@bot.command(name= "Bet")
async def bet(ctx):
    roles = get_player_roles(ctx)
    def check(msg):
        return msg.content in d_m.sports 
    await ctx.send(f"What sport would you like to see today???\nChoose only one from the following sports: {', '.join([role for role in roles if role != '@everyone'])}")
    msg = await bot.wait_for("message")
    sport = msg.content
    if sport not in roles:
        await ctx.send(f"You must have the {sport} role.Please use the .roles command")
        return
    sport_data = d_m.get_data(sport)
    farbe = colour_sport(sport)
    i = 0
    length = len(sport_data)
    print(sport_data)
    while True:
        embed = discord.Embed(
            title = "Scheduled " + sport + " matches for today!!",
            description = "You can bet on them" if length != 0 else "No matches available for now!",
            color = farbe
        )
        for k in range(i,i+10):
            if k == length:
                break
            embed.add_field(name="Game id: " + str(sport_data[k][0]),value=sport_data[k][1],inline=False)
        await ctx.send(embed=embed)
        i = i + 10
        if i >= length:
            break
    if length > 0:
        await ctx.send(f"Which match do you want to bet!! Do not insert the score, only the id")
        #We get the sport that the player wants to bet
        msg1 = await bot.wait_for("message") 
        id = msg1.content
        print(msg1.content)
        looped_match = False
        for bet in bet_info[str(ctx.message.author.id)]:
            if bet[0] == id:
                looped_match = True
                break
        if not(looped_match):
            match_data = d_m.get_data(sport=sport)[int(id)][1].split(" versus ")
            match_data_2 = match_data[0].split("|")
            hometeam = match_data_2[1]
            awayteam = match_data[1]
            print(match_data,match_data_2)
            await ctx.send(f"Who do you think will win??\n-> {hometeam} or {awayteam} or tie\nGive the name below")
            def check_team(answer):
                return answer.content == hometeam or answer.content == awayteam or answer.content == 'tie'
            answer = await bot.wait_for("message",check=check_team) 
            if answer.content == 'tie':
                winner = hometeam
                loser = awayteam
                result = 'tie'
            else:
                winner = answer.content
                if awayteam == winner:
                    loser = hometeam
                else:
                    loser = awayteam
                result = 'won'
            await ctx.send(f"How many coins do you want to bet in {winner} ?")
            coins = await bot.wait_for("message")
            if dict_info[coins.author.name] > 0:
                while True:
                    #if there are enough coins to spent on the winner
                    if int(coins.content) <= dict_info[coins.author.name]:
                        await ctx.send(f"You have spent {coins.content} on your bet !!!")
                        bet_info[str(coins.author.id)].append([id,sport,winner,loser,result,int(coins.content)])
                        dict_info[coins.author.name] = dict_info[coins.author.name] - int(coins.content)
                        break
                    else:
                        await ctx.send(f"You don't have those coins.You only have {str(dict_info[coins.author.name])}.")
                        await ctx.send(f"How many coins do you want to bet in {winner} ?")
                        coins = await bot.wait_for("message")
            else:
                await ctx.send(f"Sorry, but you have 0 coins {coins.author.mention}")
                bet_info[str(ctx.message.author.id)].append([id,sport,winner,0])
    print(bet_info)
    return
    
# Data Updating Scheduling
@tasks.loop(minutes=30)
async def Update_Data_Base():
    d_m.Api_requests()

@Update_Data_Base.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished Waiting")

@bot.command(name="test")
async def Ptest(ctx):
    with open('read.txt','w') as f:
        sport_list = d_m.sports
        for s in sport_list:
            f.write(f"{s}\n")
            test_list = d_m.get_data(s)
            for i in test_list:
                f.write(f"{i}\n")

# Helpful info about the coins & more for every player
@bot.command(name = "See_Coins",help = "Helps you see your coins!")
async def see_coins(ctx):
    """A command that helps the player see the coins that he/she has collected so far"""
    await ctx.send(f'Tell me you want to see your coins???\n [y - n]')
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel 
    msg = await bot.wait_for("message",check=check)
    if msg.content.lower() == 'y':
        sum = int(dict_info[str(msg.author)[:-5]])
        message = 'Hello {0.author.mention} your coins are {1} in total!'.format(ctx.message,sum)
        await ctx.send(message)
    elif msg.content.lower() != 'n':
        await ctx.send("False answer")
    else:
        await ctx.send("You will not see your coins then 👍!!!")
    return
    
#Role assignment
"""We ask about the roles that he wants to take in the guild"""
async def dm_for_roles(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"""Hi {member.name}, welcome to {member.guild.name}! 
        
        Which of these sports do you wanna bet:
                
        * tennis 🎾
        * football ⚽️
        * basketball 🏀
        * ping-pong 🏓
        * baseball ⚾️
                
        Reply to this message with one or more of the language names or emojis above so I can assign you the right roles on our server.

        Reply with the name or emoji of a language you're currently using and want to stop and I'll remove that role for you.
        """
    )

async def role_assignment(msg):
    sports = set(re.findall("tennis|football|baseball|basketball|ping\-pong",msg.content,re.IGNORECASE))
    """sport emojis"""
    #tennis U+1F3BE
    #pino-pong U+1F3D3
    #baseball U+26BE
    #football U+26BD
    #basketball U+1F3C0
    sport_emojis = set(re.findall("\U0001F3BE|\U0001F3D3|\U000026BE|\U000026BD|\U0001F3C0", msg.content))
    for emoji in sport_emojis:# it's the same as the switch case
        {
            "\U0001F3BE": lambda: sports.add("tennis"),
            "\U0001F3D3": lambda: sports.add("ping-pong"),
            "\U000026BE": lambda: sports.add("baseball"),
            "\U000026BD": lambda: sports.add("football"),
            "\U0001F3C0": lambda: sports.add("basketball")
        }[emoji]()
    if sports:
        server = bot.get_guild(int(SERVER_ID))
        new_roles = set([discord.utils.get(server.roles,name=sport.lower()) for sport in sports])
        member = await server.fetch_member(msg.author.id) # that's how we take the member of the author
        current_roles = set(member.roles)
        adding_roles = new_roles.difference(current_roles)
        roles_to_remove = new_roles.intersection(current_roles)
        print(adding_roles)
        print(roles_to_remove)
        try:
            #We unpack our sports set into separate arguments using the * operator,
            #and provide a string for the named argument reason.
            await member.add_roles(*new_roles,reason = "Roles assigned by BetBot")
            await member.remove_roles(*roles_to_remove,reason = "Roles revoked by BetBot")
        except Exception as e:
            print(e)
            await msg.channel.send("Error assigning roles.")
        else:
            if adding_roles:
                await msg.channel.send(f"You have assigned the following role{'s' if len(adding_roles) > 1 else ''} on {server.name}: {', '.join([role.name for role in adding_roles]) }")
            if roles_to_remove:
                await msg.channel.send(f"You've lost the following role{'s' if len(roles_to_remove) > 1 else ''} on {server.name}: {', '.join([role.name for role in roles_to_remove])}")
    else:
        await msg.channel.send("No supported sports were found in your message")

#Message management
@bot.command(help='clear the amout of message.Ect: !clear 10 -> it clears the 10 previous meessages!')
async def clear(ctx, amount=1):
    """Writing !cls and the amount of message you want to delete"""
    await ctx.channel.purge(limit=amount)

@bot.event
async def on_message(message):
    #First prevent the message responding to it's self
    if message.author == bot.user:
        return
    #Respond to commands
    if isinstance(message.channel, discord.channel.DMChannel):
        await role_assignment(message)
        return
    """1st command !roles"""
    if message.content.startswith(".roles"):
        await dm_for_roles(message.author)
    elif message.content.startswith(".serverid"):
        await message.channel.send(message.channel.guild.id)
    #now to stop on_message from overriding the commands we use the code below
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    """Welcome the player that comes to server"""
    """First Update the data-(Dictionaries)"""
    #---dict_info -> coins
    dict_info.update({member.name:0})
    #---player_info -> id
    player_info.update({member.name:member.id})
    #---bet_info -> bet
    bet_info.update({member.id:5})
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to {GUILD}!')
    await member.dm_channel.send(f'Would you like to take one of the roles from our guild ???\n Please answer with y for YES or n for NO')
    msg = await bot.wait_for("message")
    if msg.content.lower() == 'y':
        dm_for_roles(member)
        if isinstance(msg.channel, discord.channel.DMChannel):
            await role_assignment(msg)
            return

#Custom Help command
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(
        title = 'Help',
        description = 'Find every useful command here!!!',
        colour = discord.Colour.blurple()
    )
    embed.add_field(name="GN",value="This command takes one left and right limit from the user and after that the user has to guess a number between them.\nThe reward is some coins,the quantity depends on the space (right<limit> - left<limit>)",inline=False)
    embed.add_field(name="lfootball",value="This command only shows the live score if you have the football role",inline=True)
    embed.add_field(name="lbasketball",value="This command only shows the live score if you have the basketball role",inline=True)
    embed.add_field(name="lbaseball",value="This command only shows the live score if you have the baseball role",inline=True)
    embed.add_field(name="ltennis",value="This command only shows the live score if you have the tennis role",inline=True)
    embed.add_field(name="ltable-tennis",value="This command only shows the live score if you have the ping-pong role")
    embed.add_field(name="See_Coins",value="This command helps you see your coins you have collected so far")
    embed.add_field(name="clear",value="This command is for the admin only.It clear a number of messages")
    embed.add_field(name=".roles",value="This is not a command,it shows the roles to somebody and helps them pick some of them")
    embed.set_footer(text = 'P.S.All commands start with !.Foe example !GN.')
    embed.set_thumbnail(url="https://climate-adapt.eea.europa.eu/repository/11284263.jpg") 
    embed.set_author(name='Panattack',icon_url="https://instagram.fath4-2.fna.fbcdn.net/v/t51.2885-19/236337950_130889542549797_3901830444066016746_n.jpg?stp=dst-jpg_s320x320&_nc_ht=instagram.fath4-2.fna.fbcdn.net&_nc_cat=109&_nc_ohc=c-ekV6c0QqIAX-V4Y6w&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AT93E6wTbhbFQYxt2m141D5wxc0AjrEfpYBshm72508sJA&oe=630D7DBA&_nc_sid=8fd12b")
    await ctx.send(embed=embed)

#Now to start the scheduling
Update_Data_Base.start()

#Now the bot runs
bot.run(TOKEN)