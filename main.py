from discord.ext.commands import Bot
from dotenv import load_dotenv
from os import getenv

players = {}


load_dotenv()
token = getenv('DISCORD_TOKEN')

bot = Bot(command_prefix=['QS ', 'qs ', 'quizscore ', 'q ', 'Q'])

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='start', help='Starts a counter', aliases=['init', 'Start', 'i'])
async def start(ctx):
    if ctx.channel.id in players:
        await ctx.send('A Counter has already started in this channel')
    else:
        players[ctx.channel.id] = {}
        await ctx.send('Starting a counter')

@bot.command(name='add', help='Adds score to a player, If a player doesn\'t exists, it creates them', alisases=['a'])
async def add(ctx):
    if not ctx.channel.id in players:
        await ctx.send('You need to start a counter before running this command')
    else:
        playerName = ctx.message.content.split()[2]
        pts = ctx.message.content.split()[3]
        if not pts.isdigit():
                ctx.send('You are using this command wrong')
        else:
            pts = int(pts)
            if playerName in players[ctx.channel.id]:
                players[ctx.channel.id][playerName] += pts
            else:
                players[ctx.channel.id][playerName] = pts
            await ctx.send(f'{playerName} has been given {pts} points, and now has {players[ctx.channel.id][playerName]} points in total')

@bot.command(name='subtract', help='Subtracts score to a player, If a player doesn\'t exists, it creates them', aliases=['s', 'sub'])
async def subtract(ctx):
    if not ctx.channel.id in players:
        await ctx.send('You need to start a counter before running this command')
    else:
        playerName = ctx.message.content.split()[2]
        pts = ctx.message.content.split()[3]
        if not pts.isdigit():
            await ctx.send('You are using this command wrong')
        else:
            pts = int(pts)
            if playerName in players[ctx.channel.id]:
                players[ctx.channel.id][playerName] -= pts
            else:
                players[ctx.channel.id][playerName] = -1*pts
        await ctx.send(f'{pts} points have been taken from {playerName}, and {playerName} now has {players[ctx.channel.id][playerName]} points in total')

@bot.command(name='show', help='Shows scoreboard', aliases=['disp', 'display', 'd', 'lb'])
async def show(ctx):
    if not ctx.channel.id in players:
        await ctx.send('You need to start a counter before running this command')
    else:
        lb = [[v,k] for k, v in sorted(players[ctx.channel.id].items(), key=lambda item: item[1])]
        lb.reverse()
        ''' Slower
        await ctx.send('Leaderboard')
        for pos, item in enumerate(lb):
            await ctx.send(f'({pos+1}){item[1]} - {item[0]}pts')
        '''
        lbText = 'Leaderboard\n'
        for pos, item in enumerate(lb):
            lbText += f'({pos+1}){item[1]} - {item[0]}pts\n'
        await ctx.send(lbText[:-1])

@bot.command(name='clear', help='Starts a counter', aliases=['end', 'c', 'e'])
async def clear(ctx):
    if not ctx.channel.id in players:
        await ctx.send('There is no counter in this channel')
    else:
        players[ctx.channel.id] = dict.fromkeys(players[ctx.channel.id], 0)
        await ctx.send('Cleared the counter')

@bot.command(name='fullclear', help='Starts a counter', aliases=['fc', 'fullc', 'fclear'])
async def fclear(ctx):
    if not ctx.channel.id in players:
        await ctx.send('There is no counter in this channel')
    else:
        players[ctx.channel.id] = {}

bot.run(token)