# non-essential
import time

global_start = time.time()

# discord bot wrapper
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands.context import Context

# others
import get_isp_events
import query_response
import json

import os
from dotenv import load_dotenv

load_dotenv()
PARENT_DIR = os.environ.get("PARENT_DIR")

# intro message
intro_message = """I am the Orientator.

My goal is to help new students navigate the complexities of Hwa Chong Institution.

Whether it's providing guidance on school culture and traditions or helping you keep track of important dates and weightages, I am here to assist you. My aim is to make your transition into Hwa Chong as smooth and successful as possible.

Click the button below to create a channel where you can interact with me privately. Just send a question in your private channel and I will answer it!
"""

# create bot
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

# button for creating ticket
channel_ids = set()
users_with_channels = set()
class TicketButton(nextcord.ui.View):
    def _init_(self):
        super().__init__()
    
    @nextcord.ui.button(label="Create Ticket", style=nextcord.ButtonStyle.green)
    async def create_ticket(self, button, interaction):
        # prevent duplicates
        if interaction.user.id in users_with_channels:
            return
        users_with_channels.add(interaction.user.id)
        
        self.value = True
        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True)
        }
        channel = await interaction.guild.create_text_channel(name=f"{interaction.user}'s Conversation", overwrites=overwrites)
        channel_ids.add(channel.id)

# formerly !query command
@bot.event
async def on_message(message):
    # ignore messages from bot
    if message.author == bot.user:
        return
    
    # get the event details
    if message.content.startswith("!date "):
        event_name = message.content.strip("!date ")
        if not event_name: 
            return
        data = get_isp_events.get_event(event_name)
        if not data:
            return await message.reply("No matches found for this event.")
        print(data)
        event_data = data[1]
        return await message.reply(f"Event Details '{data[0]}' is on the date {event_data['day']}/{event_data['month']} and it lasts for {event_data['num_days']} days.")

    # check if in valid channel
    if message.channel.id in channel_ids:
        query = message.content
        await message.channel.send(query_response.query_response(query, str(message.author.id)))    

# login confirmation
on_ready_ran = False
@bot.event
async def on_ready():
    # prevent accidental rerunning when bot randomly reconnects to discord i think
    global on_ready_ran
    if on_ready_ran: 
        return
    on_ready_ran = True
    print((f"Logged in at `{time.strftime('%Y-%m-%d %H:%M:%S')}`"))

    # send some info
    channel = bot.get_channel(1094132670394548294)
    await channel.send(f"Logged in at `{time.strftime('%Y-%m-%d %H:%M:%S')}`")

    # delete all existing conversation channels
    for channel in bot.get_guild(1090509423992131695).channels:
        if channel.name.endswith("-conversation"):
            await channel.delete()

    # clear create-ticket channel
    channel = bot.get_channel(1119512373582114937)
    await channel.purge(limit=100)

    # send message with button
    ticket_button = TicketButton()
    await channel.send(intro_message, view=ticket_button)

    global_end = time.time()
    await channel.send(f"Program start took `{round(global_end - global_start, 6)}s`", delete_after=5)

if __name__ == "__main__":
    # load bot data
    with open(PARENT_DIR + "bot.json", "r") as file:
        bot_data = json.load(file)

    # start bot
    bot.run(bot_data["token"])