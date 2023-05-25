import nextcord
from nextcord.ext import commands
from nextcord.ext.commands.context import Context
import query_response
import json

import torch
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

# non-essential
import sys
import time

# create bot
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

# !query command
@bot.command(name="query")
async def query_command(ctx:Context):
    # get the query
    query = ctx.message.content[2 + len("query"):]
    # reply
    await ctx.send(query_response.query_response(query, generator=generator))

# non-essential
@bot.command(name="quit")
async def quit_command(ctx:Context):
    # global tokenizer # this isnt even defined?
    await ctx.send(f"Exiting at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    # tokenizer.save_pretrained("./model/")
    await bot.close()

# login confirmation
@bot.event
async def on_ready():
    print(f"Logged in at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # load bot data
    with open("bot.json", "r") as r:
        bot_data = json.load(r)

    # start bot
    bot.run(bot_data["token"])
