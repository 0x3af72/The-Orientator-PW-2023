'''
This is the backend for the discord bot.
'''

import nextcord
from nextcord.ext import commands

import query_response

import json

# create bot
bot = commands.Bot(command_prefix="@", intents=nextcord.Intents.all())

# QUERY command
@bot.command(name="query")
async def query_command(ctx):

    # get the query
    query = ctx.message.content[2 + len("query"):]

    # reply
    await ctx.reply(query_response.response(query))

# login confirmation
@bot.event
async def on_ready():
    print(f"LOGGED IN AS: {bot.user.name}")

if __name__ == "__main__":

    # load bot data
    with open("bot.json", "r") as r:
        bot_data = json.load(r)

    # start bot
    bot.run(bot_data["token"])