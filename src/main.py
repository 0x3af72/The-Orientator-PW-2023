# non-essential
import sys
import time
import timeit

start = timeit.default_timer()

# discord bot wrapper
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands.context import Context

# others
import query_response
import json

# create bot
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

# !query command
@bot.command(name="query")
async def query_command(ctx: Context):
    # start timer
    start = timeit.default_timer()
    query = ctx.message.content[2 + len("query"):]
    await ctx.send(query_response.query_response(query, str(ctx.author.id)))

    # end timer
    end = timeit.default_timer()
    await ctx.send(f"Program took `{round(end-start, 6)}s`")

# non-essential
@bot.command(name="quit")
async def quit_command(ctx: Context):
    await ctx.send(f"Exiting at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    await bot.close()

# login confirmation
@bot.event
async def on_ready():
    global start
    channel = bot.get_channel(1094132670394548294)
    await channel.send(f"Logged in at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    end = timeit.default_timer()
    await channel.send(f"Program start took `{round(end-start, 6)}s`")

if __name__ == "__main__":
    # load bot data 
    with open("bot.json", "r") as r:
        bot_data = json.load(r)

    # start bot
    bot.run(bot_data["token"])
