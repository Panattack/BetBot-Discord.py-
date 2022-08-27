#-------------------NOTES-------------------#
#->This bot can be used only in one guild that has the nessecary roles.
#->Special Thanks to:
#.....https://docs.replit.com/tutorials/discord-role-bot
#.....https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
from audioop import add
from email import message
import os
from unicodedata import name
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
import re
import youtube_dl

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
"""
id:1005051597040128091 (ect) :
coins: 0(ect)
"""
dict_info = {}

"""
BetBot (ect) :
id: OEDNOEOCS?PNCA (ect)
"""

player_info = {}

@bot.event
async def on_ready():
    """It's a classic function that connects the bot with the user"""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'{GUILD} was found!')
    for guild in bot.guilds:
         if guild.name == GUILD:
             break
    members = ([str(member.id) for member in guild.members])
    names = ([str(member.name) for member in guild.members])
    i = 0
    for m in names:
        dict_info.update({m:0})
    for m in members:
        player_info.update({names[i]:m})
        i = i+1
    print(f'Guild Members:\n - {names}')
    print(f'Info {dict_info} - {player_info}')
    #guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)

@bot.command(name = '01',help = 'Responds with a random quote in !O1.Test command!')
async def zero_one(ctx):
    """test command"""
    zo = ['You are not zero','You are number one',('We are going from the bottom to the top')]
    response = random.choice(zo)
    await ctx.send(response)

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
#------ Livescore functions ------
@bot.command(name = 'lfootball')
async def live_football(ctx):
    guild = ctx.guild
    roles_id,roles_char = [],[]
    for role in ctx.author.roles:
        roles_id.append(role.id)
        roles_char.append(role.name)
    if "football" in roles_char:
        "show the live matches in football and the live score"
        await live("football",ctx)

@bot.command(name = 'ltennis')
async def live_tennis(ctx):
    guild = ctx.guild
    roles_id,roles_char = [],[]
    for role in ctx.author.roles:
        roles_id.append(role.id)
        roles_char.append(role.name)
    if "tennis" in roles_char:
        await live("tennis",ctx)

@bot.command(name = 'lbaseball')
async def live_baseball(ctx):
    guild = ctx.guild
    roles_id,roles_char = [],[]
    for role in ctx.author.roles:
        roles_id.append(role.id)
        roles_char.append(role.name)
    if "baseball" in roles_char:
        await live("baseball",ctx)

@bot.command(name = 'lbasketball')
async def live_basketball(ctx):
    guild = ctx.guild
    roles_id,roles_char = [],[]
    for role in ctx.author.roles:
        roles_id.append(role.id)
        roles_char.append(role.name)
    if "basketball" in roles_char:
        await live("basketball",ctx)

@bot.command(name = 'ltable-tennis')
async def live_table_tennis(ctx):
    guild = ctx.guild
    roles_id,roles_char = [],[]
    for role in ctx.author.roles:
        roles_id.append(role.id)
        roles_char.append(role.name)
    if "ping-pong" in roles_char:
        await live("table-tennis",ctx)

#--------Main livescore function--------#

async def live(sport,ctx):
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
        embed = discord.Embed(
        title = "Live "+ sport,
        description = "Watch every score from your favorite sport here live!",
        color = farbe
        )
        for game in jsondata['events']:
            league = game['tournament']['name']
            hometeam = game['homeTeam']['name']
            awayteam = game['awayTeam']['name']
            homescore = game['homeScore']['current']
            awayscore = game['awayScore']['current']
            time = game['status']['description']
            v = hometeam + " " + str(homescore) + " - " + awayteam + " " + str(awayscore)+" ("+time+")"
            embed.add_field(name=league,value=v,inline=False)
        await ctx.send(embed=embed)
        

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
    embed.add_field(name="See_Coins",value="This command helps you see your coins you have collected so far")
    embed.add_field(name="clear",value="This command is for the admin only.It clear a number of messages")
    embed.add_field(name=".roles",value="This is not a command,it shows the roles to somebody and helps them pick some of them")
    embed.set_footer(text = 'P.S.All commands start with !.Foe example !GN.')
    embed.set_thumbnail(url="https://climate-adapt.eea.europa.eu/repository/11284263.jpg") 
    embed.set_author(name='Panattack',icon_url="https://instagram.fath4-2.fna.fbcdn.net/v/t51.2885-19/236337950_130889542549797_3901830444066016746_n.jpg?stp=dst-jpg_s320x320&_nc_ht=instagram.fath4-2.fna.fbcdn.net&_nc_cat=109&_nc_ohc=c-ekV6c0QqIAX-V4Y6w&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AT93E6wTbhbFQYxt2m141D5wxc0AjrEfpYBshm72508sJA&oe=630D7DBA&_nc_sid=8fd12b")
    await ctx.send(embed=embed)

#Now the bot runs
bot.run(TOKEN)