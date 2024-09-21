import datetime
import discord
from discord.ext import commands
from db import get_db_connection
from config import PHAT_LOOTS_CHANNEL_ID, CLAN_SCRAPBOOK_CHANNEL_ID

GAZ_EMOJI = "gaz" 
MODERATOR_ROLE_NAME = "Moderator"

def update_points_for_user(user_id, message_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Check if the message has already been processed
        cursor.execute("SELECT 1 FROM processed_discord_reactions WHERE message_id = %s", (message_id,))
        if cursor.fetchone():
            return False  # Message has already been processed

        current_month = datetime.datetime.now().strftime('%Y%m')

        # Get the WOM ID from main_rsn_map for the given discord_id
        cursor.execute("""
            SELECT WOM_ID FROM main_rsn_map WHERE DISCORD_ID = %s
        """, (user_id,))
        wom_id_result = cursor.fetchone()

        if not wom_id_result:
            return False  # No WOM ID found, so no update is done

        wom_id = wom_id_result[0]

        # Update the split points for the user with the retrieved WOM ID
        cursor.execute("""
            UPDATE member_points m
            SET m.split_points = m.split_points + 1 
            WHERE m.month = %s
            AND m.WOM_ID = %s
        """, (current_month, wom_id))
        db.commit()

        # Record that this message has been processed
        cursor.execute("INSERT INTO processed_discord_reactions (message_id) VALUES (%s)", (message_id,))
        db.commit()

        return True  # Points successfully updated
    finally:
        cursor.close()
        db.close()

async def monitor_splits(bot):
    @bot.event
    async def on_raw_reaction_add(payload):
        # Check if the reaction is in the monitored channels
        if payload.channel_id not in [PHAT_LOOTS_CHANNEL_ID, CLAN_SCRAPBOOK_CHANNEL_ID]:
            return
        
        # Fetch the guild and channel
        guild = bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = guild.get_member(payload.user_id)

        # Check if the reacting user is a moderator
        if MODERATOR_ROLE_NAME not in [role.name for role in user.roles]:
            return
        
        # Check if the emoji is the one we care about
        if str(payload.emoji.name) != GAZ_EMOJI:
            return
        # Check if the message contains the word "split"
        if "split" in message.content.lower():
            # Update the points for the author of the message
            if update_points_for_user(message.author.id, message.id):
                await message.add_reaction("✅")
