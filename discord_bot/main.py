# main.py

import asyncio
import discord
from discord.ext import commands, tasks
from config import BOT_TOKEN, MEMBER_CHANNEL_ID, ROLES_CHANNEL_ID, MOD_TOOLS_CHANNEL_ID, MEMBER_INTERACTION_MESSAGE_ID, GET_ROLES_MESSAGE_ID
from member_interactions import bot, CheckRankButton, AddRSNModal, SetMainRSNButton, HowRanksWorkButton
from rank_management import change_rank_on_discord  
from mod_interactions import display_mod_tools, refresh_mod_tools, on_button_click, send_rankups_log
from splits_monitor import monitor_splits 
from db import get_db_connection
from loot_hiscores import post_loot_hiscores
from pb_hiscores import post_clan_pb_hiscores
from twitch_monitor import start_twitch_monitoring

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

    # Initialize the main member channel
    member_channel = bot.get_channel(MEMBER_CHANNEL_ID)
    roles_channel = bot.get_channel(ROLES_CHANNEL_ID)
    
    # Create the buttons
    add_rsn_button = discord.ui.Button(label="Add RSN", style=discord.ButtonStyle.secondary)
    choose_main_button = discord.ui.Button(label="Change My Main", style=discord.ButtonStyle.secondary)
    check_rank_button = CheckRankButton()
    how_ranks_work_button = HowRanksWorkButton()

    # Add functionality to the buttons
    async def add_rsn_callback(interaction):
        modal = AddRSNModal()
        await interaction.response.send_modal(modal)

    async def choose_main_callback(interaction):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            discord_id = str(interaction.user.id)

            # Query to get all RSNs with the main RSN listed first
            cursor.execute("""
                SELECT m.RSN
                FROM members m
                LEFT JOIN main_rsn_map mr ON m.DISCORD_ID = mr.DISCORD_ID
                WHERE m.DISCORD_ID = %s
                ORDER BY m.WOM_ID = mr.WOM_ID DESC, m.WOM_ID ASC
            """, (discord_id,))
            rsns = [row[0] for row in cursor.fetchall()]

            # Check if there are any RSNs registered
            if not rsns:
                await interaction.response.send_message("You don't have any registered RSNs.", ephemeral=True)
                return

            main_rsn = rsns[0]  # The main RSN will be the first entry in the list

            # Create a view with buttons for each RSN
            view = discord.ui.View()
            for rsn in rsns:
                label = f"{rsn} (Main)" if rsn == main_rsn else rsn
                style = discord.ButtonStyle.success if rsn == main_rsn else discord.ButtonStyle.primary
                button = SetMainRSNButton(rsn=rsn, label=label, style=style)
                view.add_item(button)

            # Send the ephemeral message with the buttons
            await interaction.response.send_message("Any `Split` points earned will go towards to your main account. If you have multiple accounts, let us know which one you want them to go to.", view=view, ephemeral=True, delete_after=60)
        finally:
            cursor.close()
            db.close()

    # Assign the callbacks to the buttons
    add_rsn_button.callback = add_rsn_callback
    choose_main_button.callback = choose_main_callback

    # Create a view with the buttons
    view = discord.ui.View(timeout=None)
    view.add_item(check_rank_button)
    view.add_item(how_ranks_work_button)
    view.add_item(add_rsn_button)
    view.add_item(choose_main_button)

    #Create the view for the #get-your-roles channel
    add_rsn_button = discord.ui.Button(label="Add RSN", style=discord.ButtonStyle.primary)
    add_rsn_button.callback = add_rsn_callback
    view_roles = discord.ui.View(timeout=None)
    view_roles.add_item(add_rsn_button)
    #Post in get-your-roles
    embed = discord.Embed(
        title="Clan Rank",
        description="Let us know your RSN to get your in-game rank as your Discord role.",
        color=discord.Color.default()  # You can customize the color
    )
    try:
        existing_message = await roles_channel.fetch_message(GET_ROLES_MESSAGE_ID)
        await existing_message.edit(embed=embed, view=view_roles)
    except Exception as e:
        await roles_channel.send(embed=embed, view=view_roles)
    

    # Initialize the mod tools in the mod tools channel
    mod_tools_channel = bot.get_channel(MOD_TOOLS_CHANNEL_ID)
    await display_mod_tools(mod_tools_channel)
    
    #REMOVE REMOVE REMOVE
    #await member_channel.purge(limit=50)
    #await asyncio.sleep(5) 

    # Start the periodic tasks
    monitor_discord_ranks.start()
    start_twitch_monitoring(bot)
    refresh_mod_tools.start()
    send_rankups_log.start()
    post_clan_pb_hiscores.start()
    await asyncio.sleep(10) 
    post_loot_hiscores.start()
    await asyncio.sleep(2) 
    
    
    try:
        existing_message = await member_channel.fetch_message(MEMBER_INTERACTION_MESSAGE_ID)
        await existing_message.edit(view=view)
    except Exception as e:
        # If the message doesn't exist, purge recent messages and send a new one
        #await member_channel.purge(limit=10)
        await member_channel.send(view=view)

    # Start monitoring the splits
    await monitor_splits(bot)  # Call the function to start monitoring splits

@bot.event
async def on_message(message):
    if message.channel.id in [MEMBER_CHANNEL_ID, MOD_TOOLS_CHANNEL_ID] and not message.author.bot:
        await message.delete()

@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        await on_button_click(interaction)

@tasks.loop(minutes=3) 
async def monitor_discord_ranks():
    db = get_db_connection()
    cursor = db.cursor()

    try:
        guild = bot.guilds[0]
        
        # Query the assigned discord rank
        cursor.execute("SELECT discord_id, deserved_rank FROM vw_max_rank_discord")
        rank_changes = cursor.fetchall()
        
        for discord_id, deserved_rank in rank_changes:
            member = guild.get_member(int(discord_id))
            if not member:
                continue
            # Check if the user already has the correct rank
            current_roles = [role.name for role in member.roles]

            if deserved_rank in current_roles:
                continue
            # Update the Discord role based on the new rank
            await change_rank_on_discord(guild, int(discord_id), deserved_rank)

    except Exception as e:
        print(f"Error while checking rank changes: {e}")
    finally:
        cursor.close()
        db.close()

bot.run(BOT_TOKEN)
