import requests
import logging
import discord
from discord.ext import tasks
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET  

# List of (twitch_name, discord_id) pairs.
TWITCH_DISCORD_PAIRS = [
    ("etcetcetc", "228168159461376010")
    #("twitch_username2", "234567890123456789"),
]

# The name of the Discord role to give when the Twitch user is live
STREAMING_ROLE_NAME = "Streaming"

def get_oauth_token(client_id: str, client_secret: str) -> str:
    """
    Gets an OAuth token from Twitch using the Client Credentials flow.
    """
    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    response = requests.post(token_url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("access_token")

async def update_streaming_roles(bot: discord.Client):
    """
    For each Twitch/Discord pair, check if the Twitch user is live.
    If so, add the "Streaming" role to the corresponding Discord member (if not already present).
    If not live, remove the role if they have it.
    """
    try:
        # Get a valid access token.
        token = get_oauth_token(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    except Exception as e:
        logging.error(f"Error obtaining Twitch OAuth token: {e}")
        return

    # Make sure there is at least one guild.
    if not bot.guilds:
        logging.error("Bot is not in any guilds.")
        return

    # If your bot works in only one guild, grab that guild.
    guild = bot.guilds[0]
    streaming_role = discord.utils.get(guild.roles, name=STREAMING_ROLE_NAME)
    if streaming_role is None:
        logging.warning(f"Streaming role '{STREAMING_ROLE_NAME}' was not found in guild '{guild.name}'.")
        return

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    for twitch_name, discord_id in TWITCH_DISCORD_PAIRS:
        params = {"user_login": twitch_name}
        try:
            response = requests.get("https://api.twitch.tv/helix/streams", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logging.error(f"Error checking stream status for {twitch_name}: {e}")
            continue

        # If the 'data' array is not empty, the user is live.
        is_live = bool(data.get("data"))
        member = guild.get_member(int(discord_id))
        if member is None:
            logging.warning(f"Member with discord id {discord_id} not found in guild '{guild.name}'.")
            continue

        has_role = streaming_role in member.roles

        # If the Twitch user is live and the member does not have the role, add it.
        if is_live and not has_role:
            try:
                await member.add_roles(streaming_role, reason="User is live on Twitch")
                logging.info(f"Added '{STREAMING_ROLE_NAME}' role to {member.display_name}.")
            except Exception as e:
                logging.error(f"Failed to add role for {member.display_name}: {e}")

        # If the user is not live but has the role, remove it.
        elif not is_live and has_role:
            try:
                await member.remove_roles(streaming_role, reason="User is not live on Twitch")
                logging.info(f"Removed '{STREAMING_ROLE_NAME}' role from {member.display_name}.")
            except Exception as e:
                logging.error(f"Failed to remove role for {member.display_name}: {e}")

@tasks.loop(minutes=10)
async def twitch_role_monitor(bot: discord.Client):
    """
    Task that checks all Twitch channels every 10 minutes
    and updates Discord roles accordingly.
    """
    await update_streaming_roles(bot)

def start_twitch_monitoring(bot: discord.Client):
    """
    Starts the Twitch monitoring task.
    """
    twitch_role_monitor.start(bot)
