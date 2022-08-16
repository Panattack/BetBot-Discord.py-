#-------------------NOTES-------------------#
#->This bot can be used only in one guild that has the nessecary roles.
#->Special Thanks to:
#.....https://docs.replit.com/tutorials/discord-role-bot
#.....https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
from unicodedata import name
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import re
import youtube_dl

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
        print(server)
        roles = [discord.utils.get(server.roles,name=sport.lower()) for sport in sports]
        member = await server.fetch_member(msg.author.id) # that's how we take the member of the author
        try:
            #We unpack our sports set into separate arguments using the * operator,
            #and provide a string for the named argument reason.
            await member.add_roles(*roles,reason = "Roles assigned by BetBot")
        except Exception as e:
            print(e)
            await msg.channel.send("Error assigning roles")
        else:
            await msg.channel.send(f"""You've been assigned the following role{"s" if len(sports) > 1 else ""} on {server.name}: { ', '.join(sports) }.""")
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
        description = 'It shows all the commands of the bot.',
        colour = discord.Colour.blurple()
    )
    embed.set_footer(text = 'This is footer')
    embed.set_image(url='https://climate-adapt.eea.europa.eu/repository/11284263.jpg/image_view_fullscreen')
    embed.set_author(name='Panattack')
    await ctx.send(embed=embed)
bot.run(TOKEN)