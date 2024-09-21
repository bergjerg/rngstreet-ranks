# member_interactions.py

import asyncio
import discord 
from datetime import datetime, timedelta
from discord import Embed
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from db import get_db_connection
from how_ranks_work import get_how_ranks_work
from config import MOD_LOG_CHANNEL_ID

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Modal to add a new RSN
class AddRSNModal(Modal):
    def __init__(self):
        super().__init__(title="Add a New RSN")
        self.rsn_input = TextInput(label="Enter your RSN", placeholder="Type your RSN here")
        self.add_item(self.rsn_input)

    async def on_submit(self, interaction: discord.Interaction):
        new_rsn = self.rsn_input.value
        discord_id = str(interaction.user.id)
        await interaction.response.defer(ephemeral=True)
        db = get_db_connection()
        cursor = db.cursor()
        

        try:
            # Check if the RSN is in the WOM group
            cursor.execute("SELECT discord_id, rsn FROM members WHERE lower(rsn) = lower(%s) and wom_rank is not null", (new_rsn,))
            result = cursor.fetchone()

            if not result: 
                # RSN not found in members. Ask if new
                await interaction.followup.send(
                    f"The RSN `{new_rsn}` was not found in the Wise Old Man group. Is this account new to the clan?",
                    ephemeral=True,
                    view=NewRSNView(new_rsn, discord_id)
                )
                return
            
            existing_discord_id = result[0]
            formatted_rsn = result[1]

            if existing_discord_id == "":
                # RSN Available, assign discord id
                cursor.execute("""
                    CALL assign_rsn_to_discord_id(%s, %s)
                """, (discord_id, formatted_rsn))
                db.commit()
                await interaction.followup.send(f'Your RSN has been set to: `{formatted_rsn}`', ephemeral=True)
                
            elif existing_discord_id != discord_id:
                # If the RSN is assigned to someone else, ask the user if they want it reviewed by a mod
                await interaction.followup.send(
                    f"The RSN `{formatted_rsn}` is already assigned to another user. Do you want this reviewed by a moderator?",
                    ephemeral=True,
                    view=ReviewRequestView(formatted_rsn, discord_id, existing_discord_id)
                )
            elif existing_discord_id == discord_id:
                # RSN already assigned to requester
                await interaction.followup.send(f'This RSN is already assigned to you.', ephemeral=True)
        except:
            await interaction.followup.send(f'Something went wrong.', ephemeral=True)
        finally:
            cursor.close()
            db.close()

# View for handling new RSN scenario
class NewRSNView(View):
    def __init__(self, new_rsn, discord_id):
        super().__init__()
        self.new_rsn = new_rsn
        self.discord_id = discord_id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute( """
            INSERT INTO stg_discord_new_rsn (unload_time, discord_id, rsn)
            VALUES (NOW(), %s, lower(%s))
            """, (self.discord_id, self.new_rsn))
            db.commit()
        except: None #RSN has already been pre-registered.
        finally:
            cursor.close()
            db.close()
        mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)        
        embed = discord.Embed(
            title="New Member - Update WOM",
            description=(
                f"""<@{self.discord_id}> tried to assign the RSN **{self.new_rsn}**
                It wasn't found in the WOM group and they have confirmed it's new to the clan.
                """
            ),
            color=discord.Color.orange()
        )
        await mod_channel.send(embed=embed)
        await interaction.response.edit_message(content="The mods have been notified to update the WOM group. You'll be ranked when we can track your RSN.", delete_after=10, view=None)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"The RSN `{self.new_rsn}` could not be assigned.", delete_after=5, view=None)

# Button to set a specific RSN as the main account
class SetMainRSNButton(Button):
    def __init__(self, rsn, label, style):
        super().__init__(label=label, style=style)
        self.rsn = rsn

    async def callback(self, interaction: discord.Interaction):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            #await interaction.response.defer(ephemeral=True)  # Defer early

            # Update the wom_id in main_rsn_map based on the RSN and discord_id
            cursor.execute("""
                UPDATE main_rsn_map mrm
                JOIN members m ON m.RSN = %s
                SET mrm.wom_id = m.WOM_ID
                WHERE mrm.discord_id = %s
            """, (self.rsn, interaction.user.id))
            db.commit()

            # Notify the user
            await interaction.response.edit_message(delete_after=5, view=None, content=f'`{self.rsn}` has been set as your Main.')
        finally:
            cursor.close()
            db.close()

# Button to check the user's rank
class CheckRankButton(Button):
    def __init__(self):
        super().__init__(label="Check My Rank", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        discord_id = str(interaction.user.id)

        db = get_db_connection()
        cursor = db.cursor()

        try:
            await interaction.response.defer(ephemeral=True)  # Defer early

            cursor.execute("""
                SELECT wom_id, RSN, wom_rank, current_rank, current_rank_points, points, next_rank, next_rank_points, XP_POINTS, EHB_POINTS, SPLIT_POINTS, EVENT_POINTS, month_total_points,    prev_XP_POINTS,     prev_EHB_POINTS,     prev_SPLIT_POINTS,     prev_EVENT_POINTS,     prev_month_total_points
                FROM vw_discord_rank_check
                WHERE discord_id = %s
                ORDER BY points desc
            """, (discord_id,))
            results = cursor.fetchall()

            if not results:
                await interaction.followup.send("You don't have any registered RSNs.", ephemeral=True)
                return
            
            skilling_emoji = discord.utils.get(interaction.guild.emojis, name="99")
            bossing_emoji = discord.utils.get(interaction.guild.emojis, name="Comfyinfepepe")
            split_emoji = discord.utils.get(interaction.guild.emojis, name="gp")
            event_emoji = discord.utils.get(interaction.guild.emojis, name="WoahMama2")
       
            msg_list = []
            for row in results:
                wom_id, rsn, wom_rank, current_rank, current_rank_points, points, next_rank, next_rank_points, xp_points, ehb_points, split_points, event_points, month_total_points, prev_xp_points, prev_ehb_points, prev_split_points, prev_event_points, prev_month_total_points = row

                def format_points(value):
                    if not value: return "0"
                    return str(int(value)) if value == int(value) else str(value)

                emoji_current = discord.utils.get(interaction.guild.emojis, name=str(current_rank).replace(" ", ""))
                emoji_next = discord.utils.get(interaction.guild.emojis, name=str(next_rank).replace(" ", ""))

                next_rank_value = f"{emoji_next} {next_rank} ({next_rank_points} points)" if next_rank else ""
                current_points_display = f"({current_rank_points} points)" if current_rank_points != None else "(Special Consideration)"

                embed = discord.Embed(title=f"{rsn} - {points} Points", color=discord.Color.blue())
                embed.add_field(name="**Current Rank**", value=f"{emoji_current} {current_rank} {current_points_display}", inline=True)
                embed.add_field(name="\u200B", value="\u200B", inline=True)
                embed.add_field(name="**Next Rank**", value=next_rank_value, inline=True)
                embed.add_field(
                    name="**Points This Month**",
                    value=(
                        f"{skilling_emoji} Skilling: **{format_points(xp_points)}**\n"
                        f"{bossing_emoji} Bossing: **{format_points(ehb_points)}**\n"
                        f"{split_emoji} Splits: **{format_points(split_points)}**\n"
                        f"{event_emoji} Events: **{format_points(event_points)}**\n"
                        f"**Total: {format_points(month_total_points)}**"
                    ),
                    inline=True
                )
                embed.add_field(name="\u200B", value="\u200B", inline=True)
                embed.add_field(
                    name="**Points Last Month**",
                    value=(
                        f"{skilling_emoji} Skilling: **{format_points(prev_xp_points)}**\n"
                        f"{bossing_emoji} Bossing: **{format_points(prev_ehb_points)}**\n"
                        f"{split_emoji} Splits: **{format_points(prev_split_points)}**\n"
                        f"{event_emoji} Events: **{format_points(prev_event_points)}**\n"
                        f"**Total: {format_points(prev_month_total_points)}**"
                    ),
                    inline=True
                )

                embed.set_footer(text="Points are updated every 15 minutes via Wise Old Man.\nRanks are updated monthly. You can request an early rank up review if eligible.")

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                msg_list.append(msg)

                # Check if user is still in WOM group
                # else Check if user has enough points for the next rank
                if wom_rank == None:
                    msg = await self.send_rsn_left_clan_notification(interaction, rsn)
                    msg_list.append(msg)
                elif next_rank_points != None and points >= next_rank_points:
                    msg = await self.send_early_review_option(interaction, wom_id, rsn, points, current_rank, current_rank_points, next_rank, next_rank_points)
                    msg_list.append(msg)

            #Clear the messages after timeout
            await clear_messages_after_timeout(msg_list)

        finally:
            cursor.close()
            db.close()

    async def send_early_review_option(self, interaction, wom_id, rsn, points, current_rank, current_rank_points, next_rank, next_rank_points):
        # Create the embed notification
        emoji_next = discord.utils.get(interaction.guild.emojis, name=str(next_rank).replace(" ", ""))
        embed = discord.Embed(
            title="Rank Up Opportunity!",
            description=(
                f"You have earned enough points for {emoji_next} **{next_rank}**.\n"
                "Ranks are updated monthly, however, you can request an early review once every 30 days."
            ),
            color=discord.Color.green()
        )
        # Create the button to request an early review
        view = View()
        view.add_item(RequestEarlyReviewButton(wom_id=wom_id
                                               ,rsn=rsn
                                               ,points=points
                                               ,current_rank=current_rank
                                               ,current_rank_points=current_rank_points
                                               ,next_rank=next_rank
                                               ,next_rank_points=next_rank_points))

        return await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    async def send_rsn_left_clan_notification(self, interaction, rsn):
        wom_url = "https://wiseoldman.net/players/" + str.replace(rsn, " ", "%20")
        embed = discord.Embed(
            title=f"Account Not Found - {rsn}",
            description=(
                f"Your Wise Old Man profile wasn't found in the clan. Check if you need to update your name here: {wom_url} "
                "Otherwise message <@477469957710544897>"
            ),
            color=discord.Color.red()
        )

        return await interaction.followup.send(embed=embed, ephemeral=True)


class RequestEarlyReviewButton(Button):
    def __init__(self, wom_id, rsn, points, current_rank, current_rank_points, next_rank, next_rank_points):
        super().__init__(label="Request Early Review", style=discord.ButtonStyle.primary)
        self.wom_id = wom_id
        self.rsn = rsn
        self.points = points
        self.current_rank = current_rank
        self.current_rank_points = current_rank_points
        self.next_rank = next_rank
        self.next_rank_points = next_rank_points

    async def callback(self, interaction: discord.Interaction):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            # Check if a rank-up request already exists for this WOM_ID
            cursor.execute("SELECT request_timestamp FROM discord_rankup_request WHERE wom_id = %s", (self.wom_id,))
            result = cursor.fetchone()

            if result:
                # Calculate the time until the user can request again (assuming 30 days limit)
                request_timestamp = result[0]
                cooldown_period = timedelta(days=30)
                next_allowed_request_time = request_timestamp + cooldown_period
                time_remaining = next_allowed_request_time - datetime.now()

                if time_remaining > timedelta(0):
                    # User must wait before requesting again
                    await interaction.response.edit_message(
                        content=f"You have already requested a rank-up. You can request again <t:{int(next_allowed_request_time.timestamp())}:R>.",
                        view=None,
                        embed=None,
                        delete_after=10                        
                    )
                    return
                else:
                    # If the cooldown period has passed, update the timestamp and proceed
                    cursor.execute("UPDATE discord_rankup_request SET request_timestamp = NOW() WHERE wom_id = %s", (self.wom_id,))
            else:
                # No previous request, insert a new record
                cursor.execute("INSERT INTO discord_rankup_request (wom_id, request_timestamp) VALUES (%s, NOW())", (self.wom_id,))

            db.commit()

            # Continue with the original functionality
            mod_channel = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)

            # Format rank display with emoji
            emoji_current = discord.utils.get(interaction.guild.emojis, name=self.current_rank.replace(" ", ""))
            emoji_next = discord.utils.get(interaction.guild.emojis, name=self.next_rank.replace(" ", ""))
            current_rank_display = f"{emoji_current} {self.current_rank}" if emoji_current else self.current_rank
            next_rank_display = f"{emoji_next} {self.next_rank}" if emoji_next else self.next_rank

            # Send the request to the mod log channel
            embed = discord.Embed(
                title="Rank Up Request",
                description=f"{interaction.user.mention} has requested an early rank up review for **{self.rsn}** to **{next_rank_display}** ({self.next_rank_points} points)",
                color=discord.Color.orange()
            )

            # Add fields to the embed for additional details
            embed.add_field(name="RSN", value=self.rsn, inline=True)
            embed.add_field(name="Total Points", value=self.points, inline=True)
            embed.add_field(name="Current Rank", value=f"{current_rank_display} ({self.current_rank_points} points)", inline=True)

            # Create approve and deny buttons
            view = View(timeout=None)
            view.add_item(EarlyReviewApproveButton(user=interaction.user, rsn=self.rsn, next_rank=self.next_rank))
            view.add_item(EarlyReviewDenyButton(user=interaction.user, rsn=self.rsn, next_rank=self.next_rank))

            await mod_channel.send(embed=embed, view=view)
            await interaction.response.send_message("Your request has been sent to the moderators for review.", ephemeral=True, delete_after=60)

        except Exception as e:
            print(f"Error during rank up request: {e}")
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)
        finally:
            cursor.close()
            db.close()

# Button to approve the rank up
class EarlyReviewApproveButton(Button):
    def __init__(self, user, rsn, next_rank):
        super().__init__(label="Approve", style=discord.ButtonStyle.success)
        self.user = user
        self.rsn = rsn
        self.next_rank = next_rank

    async def callback(self, interaction: discord.Interaction):
        # Create the result log embed
        emoji = discord.utils.get(interaction.guild.emojis, name=self.next_rank.replace(" ", ""))
        emoji_display = f"{emoji} " if emoji else ""
        embed = discord.Embed(
            title="Rank Up Request - Approved",
            description=f"{self.user.mention}'s request for **{self.rsn}** to rank up to {emoji_display} **{self.next_rank}** has been approved by {interaction.user.mention}",
            color=discord.Color.green()
        )

        # Edit the original message with the result log
        await interaction.message.edit(embed=embed, view=None)

# Button to deny the rank up
class EarlyReviewDenyButton(Button):
    def __init__(self, user, rsn, next_rank):
        super().__init__(label="Deny", style=discord.ButtonStyle.danger)
        self.user = user
        self.rsn = rsn
        self.next_rank = next_rank

    async def callback(self, interaction: discord.Interaction):
        # Create the result log embed
        emoji = discord.utils.get(interaction.guild.emojis, name=self.next_rank.replace(" ", ""))
        emoji_display = f"{emoji} " if emoji else ""
        embed = discord.Embed(
            title="Rank Up Request - Denied",
            description=f"{self.user.mention}'s request for **{self.rsn}** to rank up to {emoji_display} **{self.next_rank}** has been denied by {interaction.user.mention}",
            color=discord.Color.red()
        )

        # Edit the original message with the result log
        await interaction.message.edit(embed=embed, view=None)


# View for requesting a review if an RSN is taken
class ReviewRequestView(View):
    def __init__(self, rsn, discord_id, existing_discord_id):
        super().__init__()
        self.rsn = rsn
        self.discord_id = discord_id
        self.existing_discord_id = existing_discord_id

    @discord.ui.button(label="Request Review", style=discord.ButtonStyle.primary)
    async def request_review(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # Defer response to prevent timeout
        db = get_db_connection()
        cursor = db.cursor()

        try:
            mod_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
            # Create the result log embed
            embed = discord.Embed(
                title="RSN Conflict",
                description=f"<@{self.discord_id}> has requested to assign the RSN **{self.rsn}** which is already taken by <@{self.existing_discord_id}>.",
                color=discord.Color.red()
            )
            view = ApprovalView(self.rsn, self.discord_id, self.existing_discord_id)

            await mod_channel.send(embed=embed, view=view)
            await interaction.followup.send("Your request has been sent to the moderators for review.", ephemeral=True)

        except Exception as e:
            print(f"Error querying RSN and Discord ID: {e}")
            await interaction.followup.send("An error occurred while processing your request.", ephemeral=True)
        finally:
            cursor.close()
            db.close()

# View for approving or denying the RSN assignment
class ApprovalView(View):
    def __init__(self, rsn, discord_id, existing_discord_id):
        super().__init__(timeout=None)
        self.rsn = rsn
        self.discord_id = discord_id
        self.existing_discord_id = existing_discord_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            # Insert or update the RSN in the database
            cursor.execute("""
                CALL assign_rsn_to_discord_id(%s, %s)
            """, (self.discord_id, self.rsn))
            db.commit()

            embed = discord.Embed(
                title="RSN Conflict - Approved",
                description=f"<@{self.discord_id}> has requested to assign the RSN **{self.rsn}** which is already taken by <@{self.existing_discord_id}>.\nApproved by <@{interaction.user.id}>.",
                color=discord.Color.green()
            )
            
            # Edit the original message to reflect the approval
            await interaction.message.edit(embed=embed, view=None)
        finally:
            cursor.close()
            db.close()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # Defer response to prevent timeout

        embed = discord.Embed(
            title="RSN Conflict - Denied",
            description=f"<@{self.discord_id}> has requested to assign the RSN **{self.rsn}** which is already taken by <@{self.existing_discord_id}>.\nDenied by <@{interaction.user.id}>.",
            color=discord.Color.red()
        )
    
        # Edit the original message to reflect the denial
        await interaction.message.edit(embed=embed, view=None)

# Define the new "How Ranks Work" button
class HowRanksWorkButton(Button):
    def __init__(self):
        super().__init__(label="How Ranks Work", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            await interaction.response.defer(ephemeral=True)  # Defer early

            # Fetch the rank explanation text
            explanation_text = get_how_ranks_work(interaction)

            # Query the rank configuration table for rank names and points
            cursor.execute("""
                SELECT NAME, POINTS
                FROM rank_cfg
                WHERE POINTS is not null
                ORDER BY POINTS ASC
            """)
            ranks = cursor.fetchall()

            # Create an embed for rank information
            embed = Embed(title="Ranks", color=discord.Color.blue())

            # Add a field for each rank
            for name, points in ranks:
                # Find the emoji by rank name
                emoji = discord.utils.get(interaction.guild.emojis, name=name.replace(" ", ""))
                emoji_display = f"{emoji} " if emoji else ""

                if points < 0:
                    points = "Unranked"
                elif points == 0:
                    points = "Default"
                else: points = f"{points} points"

                # Add the rank as a field in the embed
                embed.add_field(name=f"{emoji_display}{name}", value=f"{points}", inline=True)

            msg_list = []
            # First, send the description outside the embed
            msg_list.append(await interaction.followup.send(embed=explanation_text, ephemeral=True))

            # Then, send the embed with the rank information
            msg_list.append(await interaction.followup.send(embed=embed, ephemeral=True))

            #Clear messages after timeout
            await clear_messages_after_timeout(msg_list)

        finally:
            cursor.close()
            db.close()




async def clear_messages_after_timeout(msg_list):        
    #Clean up the messages after 3 minutes    
    await asyncio.sleep(120)
    try:
        for msg in msg_list:
            await msg.delete()
    except:
        None