import os
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Create a new Discord client with necessary intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """Event that runs when the bot is ready and connected to Discord"""
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    """Event that runs when a message is sent in a channel the bot can see"""
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message starts with !ping
    if message.content.startswith("!ping"):
        await message.channel.send("Pong!")


# Run the bot with the token from the .env file
if __name__ == "__main__":
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please make sure your .env file contains a valid DISCORD_TOKEN.")
