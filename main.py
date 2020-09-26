from discord.ext.commands import Bot, check, CheckFailure
from dotenv import load_dotenv
from os import getenv
from functools import wraps

class Player:

    playersByChannel = {}

    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
        self.reset()
        if self.validChannel(channel):
            Player.playersByChannel[self.channel].append(self)
        else:
            self.playersByChannel[self.channel] = [self]
    
    @classmethod
    def validChannel(cls, channel):
        return True if channel in cls.playersByChannel else False
    
    @classmethod
    def leaderboard(cls, channel):
        lb = 'LEADERBOARD\n'
        for pos, player in enumerate(sorted(cls.playersByChannel[channel], key=lambda x: x.score, reverse=True)):
            lb+=f'{f"({pos+1}) {player.name} - {player.score}pts":<30} {f"| Negs: {player.negs} ":<12}{f"| Bonuses: {player.bonus} ":<14}| Pow: {player.pow}\n'
        return lb[:-1]

    @classmethod
    def update(cls, name, amount, channel):
        if channel in cls.playersByChannel and name in [player.name for player in cls.playersByChannel[channel]]:
            return [player for player in cls.playersByChannel[channel] if player.name == name][0].add(amount)
        return Player(name, channel).add(amount)

    def reset(self):
        self.score = 0
        self.negs = 0
        self.pow = 0
        self.bonus = 0
    
    def add(self, amount):

        special = {
            'n':{'attr':'self.negs+=1', 'val':-5},
            'b':{'attr':'self.bonus+=1', 'val':10},
            'p':{'attr':'self.pow+=1', 'val':15}
        }

        if not amount.isdigit():
            exec(special[amount]['attr'])
            amount = special[amount]['val']

        self.score += int(amount)
        
        if int(amount) > 0:
            return f'{self.name} has been given {amount} points, and now has {self.score} points in total'
        else:
            return f'{amount} points have been taken from {self.name}, and {self.name} now has {self.score} points in total'

# Get token
load_dotenv()
token = getenv('DISCORD_TOKEN')

# Create bot instance
bot = Bot(command_prefix=['QS ', 'qs ', 'quizscore ', 'q ', 'Q '])

# On Discord connect
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

def valid_channel(ctx):
    return Player.validChannel(ctx.channel.id)

@bot.command(name='a', help='Score changers, either type: \n a(misc score add - type player name after, and then a space and then value to add after that)\n n (neg - type player name after, subtracts 10 from this player)\n b(bonus - type player name after, adds 10 to this player)\n or p(pow - type player name after, adds 15 to this player)', aliases=['n', 'b', 'p'])
async def scoreChange(ctx, name, amount=None):
    if amount == None:
        amount = ctx.message.content.split()[1]
    return await ctx.send(Player.update(name, amount, ctx.channel.id))

@bot.command(name='show', help='Shows scoreboard if there are players in the channel', aliases=['disp', 'display', 'd', 'lb'])
@check(valid_channel)
async def show(ctx):
    return await ctx.send(Player.leaderboard(ctx.channel.id))

@bot.command(name='clear', help='Sets all player scores to 0 in the counter if there are players in the channel', aliases=['end', 'c', 'e'])
@check(valid_channel)
async def clear(ctx, full):
    if not full:
        for player in Player.playersByChannel[ctx.channel.id]:
            player.reset() 
        return await ctx.send('Cleared the counter')
    del Player.playersByChannel[ctx.channel.id]
    return await ctx.send('Fully cleared the counter')

@show.error
@clear.error
async def no_players(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send('There are no players in the channel!')

bot.run(token)