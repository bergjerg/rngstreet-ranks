import asyncio
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import datetime
from db import get_db_connection
from member_interactions import bot
from rank_management import change_rank_on_discord  
from config import MOD_TOOLS_CHANNEL_ID, MOD_LOG_CHANNEL_ID

original_message_id = None

# Global list to store rank-up details
rankups_log_buffer = []

class RankUpButton(Button):
    def __init__(self, wom_id, discord_id, rsn, current_rank, next_rank):
        super().__init__(label=f"Approve {rsn}", style=discord.ButtonStyle.success)
        self.wom_id = wom_id
        self.discord_id = discord_id
        self.current_rank = current_rank
        self.next_rank = next_rank
        self.rsn = rsn

    async def callback(self, interaction: discord.Interaction):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            # Update the rank in the database
            cursor.execute("UPDATE members SET `rank` = %s WHERE wom_id = %s", (self.next_rank, self.wom_id))
            db.commit()

            # Update the rank in Discord
            guild = interaction.guild
            result = await change_rank_on_discord(guild, self.discord_id, self.next_rank)

            # Append the rank-up info to the global buffer (without emoji formatting)
            rankups_log_buffer.append({
                'rsn': self.rsn,
                'current_rank': self.current_rank,
                'next_rank': self.next_rank,
                'moderator': interaction.user.mention,
                'guild': guild
            })

            await interaction.response.edit_message(delete_after=0)
            await refresh_mod_tools()

        except Exception as e:
            print(f"Error during rank up approval: {e}")
            await interaction.followup.send("An error occurred while processing the rank up.", ephemeral=True)
        finally:
            cursor.close()
            db.close()

class IgnoreButton(Button):
    def __init__(self, rsn):
        super().__init__(label=f"Ignore", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(delete_after=0)

class ModToolsView(View):
    def __init__(self, rank_ups_count, mismatches_count):
        super().__init__(timeout=None)
        self.add_item(Button(label=f"Rank Ups ({rank_ups_count})", style=discord.ButtonStyle.primary, custom_id="rank_ups"))
        self.add_item(Button(label=f"Mismatches ({mismatches_count})", style=discord.ButtonStyle.secondary, custom_id="mismatches"))
        self.add_item(Button(label="Website", style=discord.ButtonStyle.link, url="https://ranks.rngstreet.com/"))
        self.add_item(Button(label="Refresh", style=discord.ButtonStyle.success, custom_id="refresh"))
        #self.add_item(Button(label="Restart Test", style=discord.ButtonStyle.secondary, custom_id="resettest"))


async def on_button_click(interaction: discord.Interaction):
    # Check if the user has the "Moderator" role
    custom_id = interaction.data.get("custom_id")
    if custom_id not in ["rank_ups", "mismatches", "refresh"]: return

    moderator_role = discord.utils.get(interaction.guild.roles, name="Moderator")    
    if moderator_role not in interaction.user.roles:    
        await interaction.response.send_message("Moderator role required.", ephemeral=True, delete_after=3)
        return
    if custom_id == "rank_ups":
        await display_rank_ups(interaction)
    elif custom_id == "mismatches":
        await display_mismatches(interaction)
    elif custom_id == "refresh":
        await interaction.response.defer(ephemeral=True)
        await refresh_mod_tools()


async def display_mod_tools(channel: discord.TextChannel):
    global original_message_id
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Query for rank ups count
        cursor.execute("SELECT COUNT(*) FROM vw_member_rankups WHERE NEXT_RANK <> '' AND rsn IS NOT NULL")
        rank_ups_count = cursor.fetchone()[0]

        # Query for mismatches count
        cursor.execute("SELECT COUNT(*) FROM vw_discord_mod_rank_mismatch ")
        mismatches_count = cursor.fetchone()[0]

        # Create the view with the buttons
        view = ModToolsView(rank_ups_count, mismatches_count)
        content = "Mod Tools:"
        
        # Edit the existing buttons if they exist
        # Else purge the channel and send new message (startup)
        if original_message_id != None:
            message = await channel.fetch_message(original_message_id)
            await message.edit(view=view)
        else:
            await channel.purge(limit=10)
            message = await channel.send(view=view)
            original_message_id = message.id
    
    except Exception as e:
        print(f"Error while displaying mod tools: {e}")
    finally:
        cursor.close()
        db.close()

class ApproveAllButton(Button):
    def __init__(self, rankups, msg_list):
        super().__init__(label="Approve All", style=discord.ButtonStyle.success)
        self.rankups = rankups
        self.msg_list = msg_list

    async def callback(self, interaction: discord.Interaction):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            for rankup in self.rankups:
                cursor.execute("UPDATE members SET `rank` = %s WHERE wom_id = %s", (rankup['next_rank'], rankup['wom_id']))
                # Update rank on Discord
                guild = interaction.guild
                await change_rank_on_discord(guild, rankup['discord_id'], rankup['next_rank'])

                # Append the rank-up info to the global buffer
                rankups_log_buffer.append({
                    'rsn': rankup['rsn'],
                    'current_rank': rankup['current_rank'],
                    'next_rank': rankup['next_rank'],
                    'moderator': interaction.user.mention,
                    'guild': guild
                })
                
            db.commit()
            await send_rankups_log()
            # Delete all messages after approval
            await interaction.response.edit_message(view=None, content="All rank-ups have been approved.", delete_after=3)
            await clear_messages_after_timeout(self.msg_list, 0)
            await refresh_mod_tools()

        except Exception as e:
            await interaction.followup.send("An error occurred while approving rank-ups.", ephemeral=True)
        finally:
            cursor.close()
            db.close()


class IgnoreAllButton(Button):
    def __init__(self, msg_list):
        super().__init__(label="Ignore All", style=discord.ButtonStyle.danger)
        self.msg_list = msg_list

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(delete_after=0)
        await clear_messages_after_timeout(self.msg_list, 0)


async def display_rank_ups(interaction: discord.Interaction):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT WOM_ID, NAME, `RANK`, POINTS, WOM_RANK, DISCORD_ID, RSN, NEXT_RANK, NEXT_RANK_POINTS, CURRENT_RANK_POINTS
            FROM vw_member_rankups
            WHERE NEXT_RANK <> ''
            AND rsn IS NOT NULL
            ORDER BY POINTS DESC
        """)
        rank_ups = cursor.fetchall()

        await interaction.response.defer(ephemeral=True)

        if not rank_ups:
            await interaction.response.send_message("No rank ups found.", ephemeral=True, delete_after=2)
            return

        rankup_data = []
        msg_list = []
        for index, (wom_id, name, current_rank, points, wom_rank, discord_id, rsn, next_rank, next_rank_points, current_rank_points) in enumerate(rank_ups):
            # Store rank-up data for approval
            rankup_data.append({
                'wom_id': wom_id,
                'discord_id': discord_id,
                'rsn': rsn,
                'current_rank': current_rank,
                'next_rank': next_rank
            })

            # Fetch the emoji for the current and next rank
            emoji_current = discord.utils.get(interaction.guild.emojis, name=current_rank.replace(" ", ""))
            emoji_next = discord.utils.get(interaction.guild.emojis, name=next_rank.replace(" ", ""))
            current_rank_display = f"{emoji_current} {current_rank}" if emoji_current else current_rank
            next_rank_display = f"{emoji_next} {next_rank}" if emoji_next else next_rank

            embed = discord.Embed(
                title=name,
                description=f"**{current_rank_display}**  ({current_rank_points} points)  -->  **{next_rank_display}** ({next_rank_points} points)",
                color=discord.Color.orange()
            )

            # Add fields to the embed for additional details
            embed.add_field(name="RSN", value=rsn, inline=True)
            embed.add_field(name="Total Points", value=points, inline=True)

            # Create the view with the buttons for individual rank-ups
            rank_up_view = View(timeout=None)
            rank_up_view.add_item(RankUpButton(wom_id, discord_id, rsn, current_rank, next_rank))
            rank_up_view.add_item(IgnoreButton(rsn))

            # Send the message
            msg = await interaction.followup.send(embed=embed, view=rank_up_view, ephemeral=True)
            msg_list.append(msg)

        # Add "Approve All" and "Ignore All" buttons
        all_buttons_view = View()
        all_buttons_view.add_item(ApproveAllButton(rankup_data, msg_list))
        all_buttons_view.add_item(IgnoreAllButton(msg_list))

        # Send the "Approve All" and "Ignore All" message
        msg = await interaction.followup.send(view=all_buttons_view, ephemeral=True)
        msg_list.append(msg)

        # Clean up the messages after 3 minutes    
        await clear_messages_after_timeout(msg_list, 180)

    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message("An error occurred while displaying rank-ups.", ephemeral=True)
        else:
            await interaction.followup.send("An error occurred while displaying rank-ups.", ephemeral=True)
        print(f"Error while displaying rank-ups: {e}")
    finally:
        cursor.close()
        db.close()



async def display_mismatches(interaction: discord.Interaction):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        await interaction.response.defer(ephemeral=True)
        cursor.execute("""
            SELECT discord_id, rsn, `rank`, wom_rank 
            FROM vw_discord_mod_rank_mismatch
        """)
        mismatches = cursor.fetchall()

        if not mismatches:
            await interaction.response.send_message("No mismatches found.", ephemeral=True)
            return

        # Character limit for Discord messages
        char_limit = 2000

        # Initialize the first message content
        table = "```\n"  # Start a code block
        table += f"{'RSN':<20} {'Assigned Rank':<20} {'InGame (WOM) Rank':<20}\n"
        table += "-" * 60 + "\n"

        total_entries = len(mismatches)
        visible_entries = 0

        messages = []

        for discord_id, rsn, current_rank, wom_rank in mismatches:
            entry = f"{rsn:<20} {current_rank:<20} {wom_rank:<20}\n"
            
            # Check if adding the next entry will exceed the character limit
            if len(table) + len(entry) > char_limit - 10:  # Reserve space for "... and X more"
                remaining_entries = total_entries - visible_entries
                table += f"... and {remaining_entries} more\n"
                table += "```"  # End the code block
                messages.append(table)

                # Start a new table for the next message
                table = "```\n"
                table += f"{'RSN':<20} {'Deserved Rank':<20} {'InGame (WOM) Rank':<20}\n"
                table += "-" * 60 + "\n"

            table += entry
            visible_entries += 1

        # Finalize the last message
        if visible_entries < total_entries:
            remaining_entries = total_entries - visible_entries
            table += f"... and {remaining_entries} more\n"
        table += "```"  # End the code block
        messages.append(table)

        msg_list = []
        # Send the responses
        for msg in messages:
            msg_list.append(await interaction.followup.send(msg, ephemeral=True))
        
        await clear_messages_after_timeout(msg_list, 180)
    
    except Exception as e:
        print(f"Error while displaying mismatches: {e}")
        await interaction.response.send_message("An error occurred while displaying mismatches.", ephemeral=True)
    finally:
        cursor.close()
        db.close()

async def clear_messages_after_timeout(msg_list, timeout):        
    #Clean up the messages after 3 minutes   
    try: 
        await asyncio.sleep(timeout)
        for msg in msg_list:
            await msg.delete()
    except:
        None


@tasks.loop(minutes=1)
async def refresh_mod_tools():
    channel = bot.get_channel(MOD_TOOLS_CHANNEL_ID)
    await display_mod_tools(channel)

    
# Task to send rank-ups log every 2 minutes if there are any
@tasks.loop(minutes=2)
async def send_rankups_log():
    if rankups_log_buffer:
        channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        description = f"Approved by {rankups_log_buffer[0]['moderator']}\n"

        max_chars = 4096  
        current_description = description  
        embeds = []  
        max_rsn_length = max(len(rankup['rsn']) for rankup in rankups_log_buffer)


        for rankup in rankups_log_buffer:
            guild = rankup['guild']
            current_rank = rankup['current_rank']
            next_rank = rankup['next_rank']

            # Fetch the emoji for the current and next rank
            emoji_current = discord.utils.get(guild.emojis, name=current_rank.replace(" ", ""))
            emoji_next = discord.utils.get(guild.emojis, name=next_rank.replace(" ", ""))

            # Format the rank display with emoji
            current_rank_display = f"{emoji_current} `{current_rank}`" if emoji_current else current_rank
            next_rank_display = f"{emoji_next} `{next_rank}`" if emoji_next else next_rank

            padded_rsn = f"`{rankup['rsn'].ljust(max_rsn_length)}`"

            # Create the rankup entry with the formatted ranks
            rankup_entry = f"\n{padded_rsn}: {current_rank_display} --> {next_rank_display}"
            
            # Check if adding this entry will exceed the character limit
            if len(current_description) + len(rankup_entry) > max_chars:
                # Create a new embed for the current description
                embed = discord.Embed(
                    title="Rank Ups",
                    description=current_description,
                    color=discord.Color.green()
                )
                embeds.append(embed) 
                
                current_description = f"Approved by {rankups_log_buffer[0]['moderator']}\n{rankup_entry}"
            else:
                # Add the rankup entry to the current description
                current_description += rankup_entry

        # Add the last description as an embed
        embed = discord.Embed(
            title="Rank Ups",
            description=current_description,
            color=discord.Color.green()
        )
        embeds.append(embed)

        # Send all embeds to the mod log channel
        for embed in embeds:
            await channel.send(embed=embed)

        # Clear the buffer after sending the logs
        rankups_log_buffer.clear()
