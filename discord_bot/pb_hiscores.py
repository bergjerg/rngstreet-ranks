import asyncio
import discord    
from discord.ui import Button, View, Select
from collections import defaultdict
from discord.ext import tasks
from db import get_db_connection
from member_interactions import bot
from datetime import datetime, timedelta
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

        # Fetch boss configurations for name, category, color, and allowed team sizes
        cursor.execute(
            """
            SELECT boss_name, category, color, allowed_team_sizes FROM boss_cfg WHERE active=true
            """
        )
        boss_configs = {}
        for row in cursor.fetchall():
            boss_name, category, color, allowed_team_sizes = row
            if category not in boss_configs:
                boss_configs[category] = {}
            boss_configs[category][boss_name] = {
                "color": color,
                "allowed_team_sizes": [int(x) for x in allowed_team_sizes.split(",")] if allowed_team_sizes else None,
            }

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
            for boss_name, boss_data in sorted(bosses.items()):  # Sort boss names alphabetically
                if boss_name not in categories[category]:
                    categories[category][boss_name] = {}
                if boss_data["allowed_team_sizes"]:
                    for team_size in boss_data["allowed_team_sizes"]:
                        if team_size not in categories[category][boss_name]:
                            categories[category][boss_name][team_size] = []

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

            for boss_name in sorted(bosses.keys()):  # Sort boss names alphabetically
                team_sizes = bosses[boss_name]

                # Fetch color and allowed team sizes for the boss
                boss_config = boss_configs.get(category, {}).get(boss_name, {})
                color_name = boss_config.get("color", "White")  # Default color
                color_code = get_color_code(color_name)
                allowed_team_sizes = boss_config.get("allowed_team_sizes", None)

                colored_boss_name = f"\n```ansi\n{color_code}{boss_name}```"

                boss_section = f"{colored_boss_name}"
                team_entries = []

                # If allowed_team_sizes is NULL, behave as before (just use existing team sizes)
                if allowed_team_sizes is None:
                    if not team_sizes:  # Ensure bosses with no team sizes still display "1, 2, 3"
                        team_sizes[None] = []  # Use None to represent an empty team size

                    for team_size, records in team_sizes.items():
                        team_display = f"**`{format_team_size(team_size)}`**" if team_size else ""
                        entries = []

                        # Group records by time for tied users
                        grouped_by_time = defaultdict(list)
                        for record in records:
                            _, _, _, time_seconds, rsn, discord_id, unload_time, position = record
                            grouped_by_time[time_seconds].append((rsn, discord_id, unload_time, position))

                        # Determine the maximum RSN list string length
                        if not grouped_by_time:  # Check if grouped_by_time is empty
                            max_rsn_list_length = 0
                        else:
                            max_rsn_list_length = max(len(", ".join([user[0] for user in users])) for users in grouped_by_time.values())
                            max_rsn_list_length = min(20, max_rsn_list_length)
                            max_rsn_list_length = 20


                        position = 1
                        for time_seconds, users in sorted(grouped_by_time.items()):
                            if position > 5:
                                break
                        
                            rsns = [user[0] for user in users]
                            unload_time = users[0][2]
                            is_new = datetime.now() - unload_time < timedelta(days=6)
                        
                            prefix_len = len(f"{position}. ")
                            line_prefix = f"{position}. "
                            spacer = " " * prefix_len
                            max_line_length = 25#max_rsn_list_length
                        
                            # Build wrapped RSN lines with comma separation
                            lines = []
                            current_line = line_prefix
                            for i, rsn in enumerate(rsns):
                                next_part = rsn + (", " if i < len(rsns) - 1 else "")
                                if len(current_line.strip()) + len(next_part) > max_line_length:
                                    lines.append(f"`{current_line.ljust(max_line_length)}`")
                                    current_line = spacer + next_part
                                else:
                                    current_line += next_part
                            lines.append(f"`{current_line.ljust(max_line_length)}`")
                        
                            # Add time on last line
                            lines[-1] += f" - **{format_time(time_seconds)}** <t:{int(unload_time.timestamp())}:R>"
                            if is_new:
                                lines[-1] += " :new:"
                        
                            entries.append("\n".join(lines))
                            position += 1
                        
                        # Pad missing positions
                        while position <= 5:
                            entries.append(f"`{position}.`")
                            position += 1


                        team_entries.append(f"**{team_display}**\n" + "\n".join(entries) if team_display else "\n".join(entries))
                else:
                    # If allowed_team_sizes is defined, ensure all team sizes are displayed
                    for team_size in allowed_team_sizes:
                        team_display = f"**`{format_team_size(team_size)}`**"
                        records = team_sizes.get(team_size, [])
                        entries = []

                        # Group records by time for tied users
                        grouped_by_time = defaultdict(list)
                        for record in records:
                            _, _, _, time_seconds, rsn, discord_id, unload_time, position = record
                            grouped_by_time[time_seconds].append((rsn, discord_id, unload_time, position))

                        # Determine the maximum RSN list string length
                        if not grouped_by_time:  # Check if grouped_by_time is empty
                            max_rsn_list_length = 0
                        else:
                            max_rsn_list_length = max(len(", ".join([user[0] for user in users])) for users in grouped_by_time.values())
                            max_rsn_list_length = min(20, max_rsn_list_length)
                            max_rsn_list_length = 20


                        position = 1
                        for time_seconds, users in sorted(grouped_by_time.items()):
                            if position > 3:
                                break
                            rsns = [user[0] for user in users]
                            unload_time = users[0][2]
                            is_new = datetime.now() - unload_time < timedelta(days=6)
                        
                            prefix_len = len(f"{position}. ")
                            line_prefix = f"{position}. "
                            spacer = " " * prefix_len
                            max_line_length = max_rsn_list_length
                        
                            # Build wrapped RSN lines
                            lines = []
                            current_line = line_prefix
                            for i, rsn in enumerate(rsns):
                                next_part = rsn + (", " if i < len(rsns) - 1 else "")
                                if len(current_line.strip()) + len(next_part) > max_line_length:
                                    lines.append(f"`{current_line.ljust(max_line_length)}`")
                                    current_line = spacer + next_part
                                else:
                                    current_line += next_part
                            lines.append(f"`{current_line.ljust(max_line_length)}`")
                        
                            # Add time on last line
                            lines[-1] += f" - **{format_time(time_seconds)}** <t:{int(unload_time.timestamp())}:R>"
                            if is_new:
                                lines[-1] += " :new:"
                        
                            entries.append("\n".join(lines))
                            position += 1
                        
                        # Pad missing positions
                        while position <= 3:
                            entries.append(f"`{position}.`")
                            position += 1



                        team_entries.append(f"**{team_display}**\n" + "\n".join(entries))

                embed.add_field(name="", value=boss_section + " \n\n".join(team_entries), inline=False)

            embeds.append(embed)

        # Post or update embeds
        channel = bot.get_channel(channel_id)

        def create_view_with_bosses(boss_list):
            view = discord.ui.View()
            view.add_item(ViewFullPBsButton(bosses=boss_list.copy()))
            return view

        if not clan_pb_post_ids:
            for embed_idx, embed in enumerate(embeds):
                category = list(categories.keys())[embed_idx]
                boss_list = list(categories[category].keys())
                view = create_view_with_bosses(boss_list)

                new_message = await channel.send(embed=embed, view=view)
                clan_pb_post_ids.append(new_message.id)
        else:
            for i, embed in enumerate(embeds):
                if i < len(clan_pb_post_ids):
                    try:
                        message = await channel.fetch_message(clan_pb_post_ids[i])
                        category = list(categories.keys())[i]
                        boss_list = list(categories[category].keys())
                        view = create_view_with_bosses(boss_list)

                        await message.edit(embed=embed, view=view)
                        await asyncio.sleep(2)
                    except discord.NotFound:
                        pass
    except Exception as e:
        print(f"Error while fetching clan PB hiscores: {e}")
    finally:
        cursor.close()
        db.close()



# Task to periodically post clan PB hiscores
@tasks.loop(minutes=1)
async def post_clan_pb_hiscores():
    await post_or_update_clan_pb_hiscores(MEMBER_CHANNEL_ID)

class ViewFullPBsButton(Button):
    def __init__(self, bosses):
        super().__init__(label="Check All PBs", style=discord.ButtonStyle.primary)
        self.bosses = bosses

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Boss:",
            view=PBSelectView(self.bosses),
            ephemeral=True
        )


class PBSelectView(View):
    def __init__(self, bosses):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=boss, value=boss) for boss in sorted(bosses)]
        self.add_item(PBSelect(options))


class PBSelect(Select):
    def __init__(self, options):
        super().__init__(placeholder="Choose a boss", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        boss_name = self.values[0]
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT category, color, allowed_team_sizes
                FROM boss_cfg
                WHERE boss_name = %s
            """, (boss_name,))
            boss_row = cursor.fetchone()
            if not boss_row:
                await interaction.response.send_message("Boss not found.", ephemeral=True)
                return

            category, color, allowed_team_sizes = boss_row
            allowed_team_sizes = [int(x) for x in allowed_team_sizes.split(",")] if allowed_team_sizes else None
            color_code = get_color_code(color)

            cursor.execute("""
                SELECT category, boss_name, team_size, time_seconds, rsn, discord_id, unload_time, position
                FROM vw_clan_pb_hiscores
                WHERE boss_name = %s
                ORDER BY team_size, position ASC
            """, (boss_name,))
            rows = cursor.fetchall()
            if not rows:
                await interaction.response.send_message("No PBs found for that boss.", ephemeral=True)
                return

            user_discord_id = str(interaction.user.id)
            user_pb_time = None
            for row in rows:
                _, _, _, time_seconds, _, discord_id, _, _ = row
                if discord_id == user_discord_id:
                    user_pb_time = time_seconds
                    break

            team_sizes = defaultdict(list)
            for row in rows:
                _, _, team_size, *_ = row
                team_sizes[team_size].append(row)

            def render_team_entries(team_size, records):
                grouped_by_time = defaultdict(list)
                for record in records:
                    _, _, _, time_seconds, rsn, discord_id, unload_time, position = record
                    grouped_by_time[time_seconds].append((rsn, discord_id, unload_time, position))

                entries = []
                position = 1
                max_rsn_line_length = 45
                for time_seconds, users in sorted(grouped_by_time.items()):
                    rsns = [u[0] for u in users]
                    unload_time = users[0][2]
                    is_new = datetime.now() - unload_time < timedelta(days=6)

                    line_prefix = f"{position}. "
                    spacer = " " * len(line_prefix)
                    current_line = line_prefix
                    lines = []
                    for i, rsn in enumerate(rsns):
                        next_part = rsn + (", " if i < len(rsns) - 1 else "")
                        if len(current_line.strip()) + len(next_part) > max_rsn_line_length:
                            lines.append(f"`{current_line.ljust(max_rsn_line_length)}`")
                            current_line = spacer + next_part
                        else:
                            current_line += next_part
                    lines.append(f"`{current_line.ljust(max_rsn_line_length)}`")
                    lines[-1] += f" - **{format_time(time_seconds)}** <t:{int(unload_time.timestamp())}:R>"
                    if is_new:
                        lines[-1] += " :new:"
                    entries.append("\n".join(lines))
                    position += 1
                return entries

            sizes_to_display = allowed_team_sizes or list(team_sizes.keys())
            color_header = f"\n```ansi\n{color_code}{boss_name}```"

            embed = discord.Embed(
                title=f"{boss_name} Hiscores",
                description=color_header,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            if user_pb_time is not None:
                embed.add_field(name="Your Time", value=f"**{format_time(user_pb_time)}**", inline=False)

            MAX_ENTRIES_PER_FIELD = 10
            for team_size in sorted(sizes_to_display):
                records = team_sizes.get(team_size, [])
                if not records:
                    continue
                all_entries = render_team_entries(team_size, records)
                for i in range(0, len(all_entries), MAX_ENTRIES_PER_FIELD):
                    chunk = all_entries[i:i + MAX_ENTRIES_PER_FIELD]
                    field_label = f"**`{format_team_size(team_size)}`**" if i == 0 else ""
                    embed.add_field(name=field_label, value="\n".join(chunk), inline=False)

            await interaction.response.edit_message(embed=embed, view=self.view)

        finally:
            cursor.close()
            db.close()
