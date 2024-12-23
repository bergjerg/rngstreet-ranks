import asyncio
import discord
from discord.ext import tasks
from db import get_db_connection
from member_interactions import bot
from datetime import datetime
from collections import defaultdict
import config

# Use MEMBER_CHANNEL_ID from config
MEMBER_CHANNEL_ID = config.MEMBER_CHANNEL_ID
clan_pb_post_ids = config.CLAN_PB_POST_IDS  # Store post IDs in memory


def format_time(seconds):
    """Formats time in HH:MM:SS or MM:SS depending on the duration."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"


def format_team_size(team_size):
    """Formats team size into human-readable form."""
    if team_size is None:
        return ""  # No mention for NULL
    if team_size == 1:
        return "Solo"
    if team_size == 2:
        return "Duo"
    if team_size == 3:
        return "Trio"
    return f"{team_size}-Man"

def get_color_code(color_name):
    """Maps color names to Discord-compatible ANSI escape codes."""
    color_map = {
        "Red": "\x1b[1;31m",  # Red
        "Green": "\x1b[1;32m",  # Green
        "Orange": "\x1b[1;33m",  # Orange
        "Blue": "\x1b[1;34m",  # Blue
        "Pink": "\x1b[1;35m",  # Pink
        "Teal": "\x1b[1;36m",  # Teal
        "White": "\x1b[1;37m",  # White
    }
    return color_map.get(color_name, "\x1b[1;37m")  # Default to white

async def post_or_update_clan_pb_hiscores(channel_id):
    global clan_pb_post_ids
    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Fetch boss category configurations
        cursor.execute(
            """
            SELECT boss_category, description, thumbnail FROM boss_category_cfg
            """
        )
        category_configs = {
            row[0]: {"description": row[1], "thumbnail": row[2]} for row in cursor.fetchall()
        }

        # Fetch boss configurations for name and color
        cursor.execute(
            """
            SELECT boss_name, category, color FROM boss_cfg where active=true
            """
        )
        boss_configs = {}
        for row in cursor.fetchall():
            boss_name, category, color = row
            if category not in boss_configs:
                boss_configs[category] = {}
            boss_configs[category][boss_name] = {"color": color}

        # Query to get the clan PB hiscores grouped by category
        cursor.execute(
            """
            SELECT category, boss_name, team_size, time_seconds, rsn, discord_id, unload_time, position
            FROM vw_clan_pb_hiscores
            ORDER BY category, boss_name, team_size, position
            """
        )
        rows = cursor.fetchall()

        categories = {}
        for row in rows:
            category = row[0]
            boss_name = row[1]
            team_size = row[2]
            if category not in categories:
                categories[category] = {}
            if boss_name not in categories[category]:
                categories[category][boss_name] = {}
            if team_size not in categories[category][boss_name]:
                categories[category][boss_name][team_size] = []
            categories[category][boss_name][team_size].append(row)

        # Ensure all bosses from boss_cfg are included in the correct categories
        for category, bosses in boss_configs.items():
            if category not in categories:
                categories[category] = {}
            for boss_name in sorted(bosses.keys()):  # Sort boss names alphabetically
                if boss_name not in categories[category]:
                    categories[category][boss_name] = {}

        # Create embeds for each category
        embeds = []
        for category, bosses in categories.items():
            config = category_configs.get(category, {})
            description = config.get("description", f"Updated: <t:{int(datetime.now().timestamp())}:R>")
            thumbnail = config.get("thumbnail", None)

            embed = discord.Embed(
                title=f"{category} Hiscores",
                description=description,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            if thumbnail:
                embed.set_thumbnail(url=thumbnail)

            for boss_name in sorted(bosses.keys()):  # Sort bosses alphabetically when iterating
                team_sizes = bosses[boss_name]
                # Fetch color for the boss
                boss_config = boss_configs.get(category, {}).get(boss_name, {})
                color_name = boss_config.get("color", "White")  # Default color
                color_code = get_color_code(color_name)

                colored_boss_name = f"\n```ansi\n{color_code}{boss_name}```"

                boss_section = f"{colored_boss_name}"
                team_entries = []

                if not team_sizes:  # Ensure bosses with no team sizes still display "1, 2, 3"
                    team_sizes[None] = []  # Use None to represent an empty team size

                for team_size, records in team_sizes.items():
                    team_display = f"**`{format_team_size(team_size)}`**" if team_size else ""
                    entries = []

                    # Ensure exactly 3 positions are displayed
                    for position in range(1, 4):
                        if position <= len(records):
                            _, _, _, time_seconds, rsn, discord_id, unload_time, _ = records[position - 1]
                            precise_time = format_time(time_seconds)
                            entry = f"`{position}. {rsn}`"
                            if discord_id:
                                entry += f" <@{discord_id}>"
                            entry += f" - **{precise_time}** <t:{int(unload_time.timestamp())}:R>"
                        else:
                            entry = f"`{position}.`"
                        entries.append(entry)

                    team_entries.append(f"**{team_display}**\n" + "\n".join(entries) if team_display else "\n".join(entries))

                embed.add_field(name="", value=boss_section + " \n\n".join(team_entries), inline=False)

            embeds.append(embed)

        # Post or update embeds
        channel = bot.get_channel(channel_id)

        if not clan_pb_post_ids:  # If no existing posts, create a new one
            for embed in embeds:
                new_message = await channel.send(embed=embed)
                clan_pb_post_ids.append(new_message.id)
        else:
            for i, embed in enumerate(embeds):
                if i < len(clan_pb_post_ids):  # Update existing posts
                    try:
                        message = await channel.fetch_message(clan_pb_post_ids[i])
                        await message.edit(embed=embed)
                        await asyncio.sleep(1) 
                    except discord.NotFound:
                        pass  # Do nothing if the message is not found

    except Exception as e:
        print(f"Error while fetching clan PB hiscores: {e}")
    finally:
        cursor.close()
        db.close()


# Task to periodically post clan PB hiscores
@tasks.loop(minutes=1)
async def post_clan_pb_hiscores():
    await post_or_update_clan_pb_hiscores(MEMBER_CHANNEL_ID)
