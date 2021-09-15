# Name: Natsuki Bot
# Author: RIVXIA (Dylan Verallo)
# Date Created: 2021/5/21

botColor = 0xFFD7DC

import discord
import os
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands.core import command
from discord.ext.commands.errors import BadArgument
from saucenao_api import SauceNao
from saucenao_api.params import DB, Hide
from datetime import datetime
from dotenv import load_dotenv

client = commands.Bot(command_prefix='.', case_insensitive=True)
client.remove_command('help')
now = datetime.now()


# CLASS TO STORE THE DATABASE AND IT'S INDEX
class ImgDatabase:
    def __init__(self, name, index):
        self.name = name
        self.index = index

# FUNCTION TO LOG WHATEVER COMMAND WAS USED
def log(commandName, author):
    print ('[{}] ({}) .{}'.format(now, author, commandName))

# LIST OF AVAILABLE DATABASES
databaseList = []
databaseList.append(ImgDatabase('',DB.ALL))
databaseList.append(ImgDatabase('all',DB.ALL))
databaseList.append(ImgDatabase('pixiv',5))
databaseList.append(ImgDatabase('danbooru',9))
databaseList.append(ImgDatabase('deviantart',34))
databaseList.append(ImgDatabase('artstation',39))
databaseList.append(ImgDatabase('twitter',41))
#databaseList.append(ImgDatabase('test',0))

#ON STARTUP
@client.event
async def on_ready():
    log('Online',client.user)
    #channel = client.get_channel(845386597419188234)
    #await channel.send('Natsuki Online')

# HELP COMMANDS
@client.group(invoke_without_command=True)
async def help(ctx):
    log(ctx.command, ctx.author)
    menu = discord.Embed(title='Help',description='The help menu\nGet info about a specific command by typying .help <command>',color=botColor)
    menu.set_thumbnail(url=client.user.avatar_url)

    commandList = ''
    for command in client.commands:
        commandList+=str(command)
        commandList+='\n'

    menu.add_field(name='Commands',value=commandList)
    
    
    await ctx.send(embed=menu)

@help.command()
async def daisuki(ctx):
    log(ctx.command, ctx.author)
    menu = discord.Embed(title='Daisuki',description='Makes Natsuki say "baka"',color=botColor)
    menu.set_thumbnail(url=client.user.avatar_url)
    menu.add_field(name='Syntax',value='.daisuki')

    await ctx.send(embed=menu)

@help.command()
async def info(ctx):
    log(ctx.command, ctx.author)
    menu = discord.Embed(title='Info',description='Bring\'s up Info on Natsuki Bot,',color=botColor)
    menu.set_thumbnail(url=client.user.avatar_url)
    menu.add_field(name='Syntax',value='.info')

    await ctx.send(embed=menu)

@help.command()
async def userinfo(ctx):
    log(ctx.command, ctx.author)
    menu = discord.Embed(title='User Info',description='Brings up the username and UID of either yourself or another user',color=botColor)
    menu.set_thumbnail(url=client.user.avatar_url)
    menu.add_field(name='Syntax',value='.userinfo [@another user]')

    await ctx.send(embed=menu)

@help.command()
async def sauce(ctx):
    log(ctx.command, ctx.author)
    menu = discord.Embed(title='Sauce (**WIP**)',description='Finds the sauce of an image using the SauceNAO Api',color=botColor)
    menu.set_thumbnail(url=client.user.avatar_url)
    
    databases = ''
    for x in range(0,len(databaseList)):
        databases += databaseList[x].name
        databases += '\n'

    menu.add_field(name='Available Databases',value=databases,inline=False)
    menu.add_field(name='Syntax',value='.sauce <IMAGE> [database] [No. of results]',inline=False)
    menu.set_footer(text='Example: .sauce ALL 5 (image inserted as attachment)')
    

    await ctx.send(embed=menu)

# COMMANDS
@client.command()
async def daisuki(ctx):
    log(ctx.command, ctx.author)
    print ('[{}] ({}) .daisuki'.format(now,ctx.author))
    await ctx.send('Baka 😣')

@client.command()
async def info(ctx):
    log(ctx.command, ctx.author)
    menu = discord.Embed(color=botColor, title='Natsuki Bot', description='Bot set up for fun and for reverse image searching')
    menu.set_image(url=client.user.avatar_url)
    menu.add_field(name='Author',value='Dylan Verallo')
    menu.add_field(name='Date Created',value='2021/05/21')
    menu.set_footer(text='Pfp Source: https://www.pixiv.net/en/users/21010372')

    await ctx.send(embed=menu)

@client.command()
async def userinfo(ctx, member:discord.Member=None):
    log(ctx.command, ctx.author)
    if member == None:
        member = ctx.author
    menu = discord.Embed(color=botColor,title='User Info',description='{}\n{}'.format(member, member.id))
    menu.set_image(url=member.avatar_url)

    await ctx.send(embed=menu)

@client.command()
async def sauce(ctx, arg='', numberOfResults:int=1):
    log(ctx.command, ctx.author)
    if numberOfResults < 1 or numberOfResults > 6:
        await ctx.send('Invalid number of results. Please input a number between 1-6')
    else:
        if not ctx.message.attachments:
            await ctx.send('Please send an Image. Links do not work')       

        else:
            chosenDatabase = 1  # 1 is an invalid number. If arg was a valid database then chosenDatabase would be an ImgDatabase class instead
            for x in range(0,len(databaseList)):
                if arg.lower() == databaseList[x].name:
                    chosenDatabase = databaseList[x]
            
            if chosenDatabase == 1:
                await ctx.send('Database not supported. do ".help sauce" for list of available databases')
            else:
                database = chosenDatabase.index            
                sauceAPI = SauceNao(api_key='ba4f4eff1061317b31b80cabe55ab6181fcdda5a',hide=Hide.NONE,db=database)
                result = sauceAPI.from_url(ctx.message.attachments[0].url)

                for x in range(0,numberOfResults):
                    if not result[x].urls:
                        menu = discord.Embed(color=botColor,title='Link Broken',description='Please try another image or increasing the number of results')

                        await ctx.send(embed=menu)
                    else:
                        menu = discord.Embed(color=botColor,title=result[x].title,url=result[x].urls[0],description=result[x].urls[0])
                        menu.add_field(name='Author',value=result[x].author)
                        menu.add_field(name='Similarity',value='{}%'.format(result[x].similarity))
                        menu.set_thumbnail(url=result[x].thumbnail)

                        await ctx.send(embed=menu)

# ERROR HANDLING
@client.event
async def CommandDoesNotExistError(ctx,error):
    if isinstance(error, commands.CommandNotFound):
        log(ctx.command, ctx.author)
        await ctx.send('That Command Does Not Exist! Do .help for the list of commands')

@userinfo.error
async def UserinfoError(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send('User is not in this server / does not exist')

@sauce.error
async def WeirdSyntax(ctx,error):
    if isinstance(error,commands.BadArgument):
        await ctx.send('Invalid Syntax. Do ".help sauce" for help')

# ON MESSAGE
@client.event
async def on_message(message):
    if client.user == message.author:
        return

    if 'goku' in message.content.lower():
        log('goku', message.author)
        #await message.channel.send(file=discord.File('goku.png'))
        await message.channel.send('https://cdn.discordapp.com/attachments/845386597419188234/847268984268128316/goku.png') #Link to Goku.png

    await client.process_commands(message)

load_dotenv()
TOKEN = os.getenv("TOKEN")
client.run(TOKEN)
