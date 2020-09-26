
# Import libs we need
from discord.ext.commands import Bot, check, CheckFailure
from dotenv import load_dotenv
from os import getenv

# Player class 
class Player:

    # Dict to store players in each channel
    playersByChannel = {}

    # Init funciton, need the name of the player and the channel that they are playing in
    # to create an instance of this class
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
        self.reset()
        # Creates a key in the dict if this is the first player in the channel that maps to a list, 
        # otherwise appends the instance to the existing list in the dict
        if self.validChannel(channel):
            Player.playersByChannel[self.channel].append(self)
        else:
            self.playersByChannel[self.channel] = [self]
    
    # Function to check if a channel exists
    @classmethod
    def validChannel(cls, channel):
        return True if channel in cls.playersByChannel else False
    
    # Function to generate leaderboard string
    @classmethod
    def leaderboard(cls, channel):
        lb = 'LEADERBOARD\n'
        for pos, player in enumerate(sorted(cls.playersByChannel[channel], key=lambda x: x.score, reverse=True)):
            lb+=f'{f"({pos+1}) {player.name} - {player.score}pts":<30} {f"| Negs: {player.negs} ":<12}{f"| Bonuses: {player.bonus} ":<14}| Pow: {player.pow}\n'
        return lb[:-1]

    # Basically all this does is determine if the player exists, 
    # if they do it passes the existing object to the add function, 
    # otherwise it creates a new player instance and passes that to the add funciton
    @classmethod
    def update(cls, name, amount, channel):
        if channel in cls.playersByChannel and name in [player.name for player in cls.playersByChannel[channel]]:
            return [player for player in cls.playersByChannel[channel] if player.name == name][0].add(amount)
        return Player(name, channel).add(amount)

    # Sets everything to 0
    def reset(self):
        self.score, self.negs, self.pow, self.bonus = [0 for i in range(4)]
    
    # Add function, adds an amount to a player
    def add(self, amount):

        # Dict to hold special add vals which are n, b and p
        special = {
            'n':{'attr':'self.negs+=1', 'val':-5},
            'b':{'attr':'self.bonus+=1', 'val':10},
            'p':{'attr':'self.pow+=1', 'val':15}
        }

        # If the amount isn't a val, then its a special val
        if not amount.isdigit():
            # Add 1 to the corresponding attribute,
            # Theres a "better" way to do this but I couldn't
            # think of a shorter one and I don't think this is less pythonic
            exec(special[amount]['attr'])
            amount = special[amount]['val']

        # Add amount to score attr
        self.score += int(amount)
        
        # If amount neg, return this fstring, otherwise return the other 
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

# Function for custom check
def valid_channel(ctx):
    return Player.validChannel(ctx.channel.id)

# Add command on bot, takes 2 additional params, name and amount
@bot.command(name='a', help='Score changers, either type: \n a(misc score add - type player name after, and then a space and then value to add after that)\n n (neg - type player name after, subtracts 10 from this player)\n b(bonus - type player name after, adds 10 to this player)\n or p(pow - type player name after, adds 15 to this player)', aliases=['n', 'b', 'p'])
async def scoreChange(ctx, name, amount=None):
    # If amount is none then they called either n, p or b, find which easily with split()[0]
    if amount == None:
        amount = ctx.message.content.split()[1]
    return await ctx.send(Player.update(name, amount, ctx.channel.id))

# Command to show leaderboard
@bot.command(name='show', help='Shows scoreboard if there are players in the channel', aliases=['disp', 'display', 'd', 'lb'])
@check(valid_channel)   # <- this is where I used the function for custom validation
async def show(ctx):
    return await ctx.send(Player.leaderboard(ctx.channel.id))

@bot.command(name='clear', help='Sets all player scores to 0 in the counter if there are players in the channel, if you type a space and anything after, a fullclear is initiated (all players players in a channel get deleted)', aliases=['end', 'c', 'e'])
@check(valid_channel) # <- custom function again
async def clear(ctx, full):
    # If no other arg passed then its only a reset to 0
    if not full:
        for player in Player.playersByChannel[ctx.channel.id]:
            # Use the reset method in the class
            player.reset() 
        return await ctx.send('Cleared the counter')
    # If we reach this line then its a fullclear, 
    # just delete the array that corresponds with the dict val
    del Player.playersByChannel[ctx.channel.id]
    return await ctx.send('Fully cleared the counter')

# Catch error
@show.error
@clear.error
async def no_players(ctx, error):
    # This is run when someone tries to clear or show leaderboard without anyone playing in the channel
    if isinstance(error, CheckFailure):
        await ctx.send('There are no players in the channel!')

# Run the bot
bot.run(token)