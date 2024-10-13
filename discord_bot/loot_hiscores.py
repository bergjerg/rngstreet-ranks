import asyncio
import os
import random
import discord
from discord.ext import tasks
from discord.ui import Button, View
from config import MEMBER_CHANNEL_ID, LOOT_HISCORES_MESSAGE_ID
from db import get_db_connection
from member_interactions import bot
from datetime import datetime
import random
import requests
import urllib.parse  # For URL encoding

# Store the last fetched item name 
last_fetched_item = None
last_fetched_image_url = None

# Store the message ID in memory
loot_hiscores_message_id = LOOT_HISCORES_MESSAGE_ID

# Function to format the values into a shortened format
def format_value(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    else:
        return f"{value / 1_000:.0f}K"

# Function to add medals based on position
def get_medal_emoji(position):
    if position == 1:
        return ":first_place:"
    elif position == 2:
        return ":second_place:"
    elif position == 3:
        return ":third_place:"
    else:
        return f"**{position}**. "

from datetime import datetime, timedelta

# Function to calculate the time remaining until the next reset
def get_reset_timestamp():
    now = datetime.now()
    # Calculate the first day of the next month
    next_month = now.month % 12 + 1
    year = now.year + (now.month // 12)
    reset_time = datetime(year, next_month, 1, 0, 0)
    return reset_time

async def get_thumbnail_url(item_name, discord_id):
    # Define the four options
    options = [
         get_item_image(item_name),  # Option 1: Item image from OSRS Wiki
         await get_discord_profile_image(discord_id),  # Option 2: Discord profile image
        "https://i.imgur.com/pTQFkrw.png",  # Option 3: Existing image 1
        "https://i.imgur.com/YhMEB3o.png"   # Option 4: Existing image 2
    ]
    
    # Set the weights: 33% for option 1 and option 2, and 16.5% each for option 3 and option 4
    weights = [33, 33, 16.5, 16.5]
    
    # Select one of the options with the specified probability
    return random.choices(options, weights=weights, k=1)[0]

# Cache variables for the last fetched item and image URL
last_fetched_item = None
last_fetched_image_url = None

def get_item_image(item_name):
    global last_fetched_item, last_fetched_image_url
    item_name = item_name.replace(" (uncharged)", "")

    # If no image is found, return a fallback image URL
    fallback_image_url = "https://i.imgur.com/pTQFkrw.png"

    # If the item name is the same as the last fetched item, return the cached image URL
    if item_name == last_fetched_item:
        return last_fetched_image_url

    # URL encode the item name to handle special characters like apostrophes
    encoded_item_name = urllib.parse.quote(item_name)

    # API call to get the item image using OSRS Wiki API
    url = f"https://oldschool.runescape.wiki/api.php?action=query&titles={encoded_item_name}&prop=pageimages&format=json&pithumbsize=1000"

    try:
        response = requests.get(url).json()

        # Extract pages from the API response
        pages = response.get('query', {}).get('pages', {})

        # Look through pages to find an image
        for page_id, page_data in pages.items():
            if 'thumbnail' in page_data:
                image_url = page_data['thumbnail']['source']
                # Cache the current item and image URL for future use
                last_fetched_item = item_name
                last_fetched_image_url = image_url
                return image_url

    except Exception as e:
        print(f"Error fetching item image from API: {e}")
        return fallback_image_url

    return fallback_image_url


async def get_discord_profile_image(discord_id):
    try:
        guild = bot.guilds[0]  # Assuming bot is in one guild
        member = guild.get_member(int(discord_id))
        if member and member.avatar:
            return member.avatar.url  # Updated to use avatar.url
        else:
            return "https://i.imgur.com/pTQFkrw.png"  # Fallback image
    except Exception as e:
        print(f"Error fetching Discord profile image: {e}")
        return "https://i.imgur.com/pTQFkrw.png"  # Fallback image



async def post_or_update_loot_hiscores(channel_id):
    global loot_hiscores_message_id

    # Get the database connection
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Query to get the loot leaderboard data
        cursor.execute("""
            SELECT position, wom_id, rsn, discord_id, total_earned, item_name_first, item_value_first, 
                   quantity_first, source_first
            FROM vw_loot_hiscores
            ORDER BY total_earned DESC
            LIMIT 25
        """)
        leaderboard = cursor.fetchall()

        # Get the current month name
        current_month = datetime.now().strftime("%B")
        # Get the time remaining until the next reset
        reset_time = get_reset_timestamp()
        reset_time_remaining = f"<t:{int(reset_time.timestamp())}:R>" 

        # Create an embed message for the loot hiscores with the current month in the title and description
        embed = discord.Embed(
            title=f"**Loot Hiscores - {current_month}** (BETA)", 
            description=f"**Updated:** <t:{int(datetime.now().timestamp())}:R>\n**Reset:** {reset_time_remaining}\n", 
            color=discord.Color.blue(), 
            timestamp=datetime.now()
        )

        # Get the highest value item and leading Discord ID for the thumbnail
        item_name_first = leaderboard[0][5]  # Assuming first entry has the highest value
        discord_id = leaderboard[0][3]
        thumbnail_url = await get_thumbnail_url(item_name_first, discord_id)

        # Set the embed thumbnail
        embed.set_thumbnail(url=thumbnail_url)

        for row in leaderboard:
            position, wom_id, rsn, discord_id, total_earned, item_name_first, item_value_first, quantity_first, source_first = row

            # Format the total_earned and item value using bold/italics for emphasis
            total_earned_str = f"{format_value(total_earned)}"  # Bold for total earned
            item_value_first_str = format_value(item_value_first)

            # Fetch the Discord member object to mention the user
            guild = bot.guilds[0]  # Assuming bot is in one guild, adjust if necessary
            member = guild.get_member(int(discord_id))

            # Get the appropriate medal emoji
            medal = get_medal_emoji(position)

            # Using get_color_by_value to color rsn and total_earned_str based on total_earned
            member_str = ""
            if member:
                member_str = f"{member.mention}"

            # Get the color for the rsn and total_earned based on total_earned value
            color = get_name_color_by_value(total_earned)
            reset = "\x1b[0m"  # Reset to default color
            white = "\x1b[0;37m"  # Default white text

            # Apply the color to the rsn and total_earned_str
            message_value = f"{medal} {member_str}```ansi\n{color}{rsn} | {total_earned_str}{reset}"
        
            quantity_first_msg = ""
            if quantity_first > 1:
                quantity_first_msg = f"{quantity_first}x "

            item_color = get_color_by_value(item_value_first)
            # Append the item name, value, and source to the message
            message_value += f"\n{quantity_first_msg}{item_name_first} {item_color}({item_value_first_str}){reset} - {source_first}"

            message_value += '```'

            # Add entry to the embed with markdown-based emphasis: mention user, show RSN, total earned, top item, quantity, and source
            embed.add_field(name=f"", value=message_value, inline=False)

        # Create a button to show how to join the hiscores
        join_button = Button(label="How to Join", style=discord.ButtonStyle.primary)

        # Define a function to handle the button press
        async def on_join_button_click(interaction):
            # Path to the images directory (relative to the current file)
            images_dir = os.path.join(os.path.dirname(__file__), 'images')

            # Attach the images from the images directory
            dink_image = discord.File(os.path.join(images_dir, "dink.png"), filename="dink.png")
            dink_setup_image = discord.File(os.path.join(images_dir, "dink_setup.png"), filename="dink_setup.png")

            # Send the ephemeral message with the attachments and improved indentation
            await interaction.response.send_message(
                """**What is the Loot Hiscores?**

The Loot Hiscores track all your drops over 100gp sent from the Dink plugin to our bot. 
Throughout the month, we collect this data to build a leaderboard, showing who’s raking in the most GP from their drops. 
The competition resets at midnight on the first of each month, so be sure to keep looting and aiming for the top spot!
You can also view a summary of all the loot you've gained this month by hitting the 'Check My Loot' button. 
The leaderboard refreshes every 60 seconds, so any drops you get will be shown here within a minute.

For any issues, message <@477469957710544897>
                
**How to join:** ```ansi
1. Add your RSN to the bot above.
2. Get \x1b[1;33mDink\x1b[0m from the Plugin Hub.
3. Setup Dink: (Image attached)
    - Add \x1b[1;33mhttps://loot.rngstreet.com/dink\x1b[0m to the Primary Webhook.
    - Enable Loot.
    - Disable Send Images.
    - Set the minimum value to \x1b[1;33mat least 100gp\x1b[0m.
4. If you already use Dink for other reasons, add the webhook to the \x1b[1;33mLoot\x1b[0m section in the \x1b[1;33mWebhook Overrides\x1b[0m tab instead of the \x1b[1;33mPrimary Webhook\x1b[0m. You can add multiple URLs here and this just means not sending uneccesary data to the bot. You can also leave images on if you're using it for other webhooks.```
                """, 
                ephemeral=True, 
                delete_after=180,
                files=[dink_image, dink_setup_image]  # Attach the images
            )

        # Create a button to view loot data
        view_loot_button = Button(label="Check My Loot", style=discord.ButtonStyle.primary)

        # Attach the click handler for the loot button
        view_loot_button.callback = on_view_loot_button_click
        join_button.callback = on_join_button_click

        # Create a view to hold the button
        view = View(timeout=None)
        view.add_item(view_loot_button)
        view.add_item(join_button)

        # Get the member channel
        member_channel = bot.get_channel(channel_id)

        embed.description=f"**Updated:** <t:{int(datetime.now().timestamp())}:R>\n**Reset:** {reset_time_remaining}\n"

        if loot_hiscores_message_id:
            # Try to fetch and edit the existing message if it exists
            try:
                message = await member_channel.fetch_message(loot_hiscores_message_id)
                await message.edit(embed=embed, view=view)  # Add the button view
            except discord.NotFound:
                # If the message doesn't exist anymore, post a new message and store its ID
                message = await member_channel.send(embed=embed, view=view)  # Add the button view
                loot_hiscores_message_id = message.id
        else:
            # If no message has been posted yet, send a new one and store its ID
            message = await member_channel.send(embed=embed, view=view)  # Add the button view
            loot_hiscores_message_id = message.id

    except Exception as e:
        print(f"Error while fetching loot hiscores: {e}")

    finally:
        cursor.close()
        db.close()

# Function to fetch loot data for a specific user by Discord ID
async def fetch_loot_data(discord_id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT RSN, item_name, value, quantity, source, last_seen
            FROM vw_loot_check
            WHERE DISCORD_ID = %s
            ORDER BY value DESC;
        """, (discord_id,))
        loot_data = cursor.fetchall()
        return loot_data
    finally:
        cursor.close()
        db.close()

# Reusable function to determine the color based on value
def get_color_by_value(value):
    # ANSI escape codes for different colors
    pink = "\x1b[1;35m"  # Bright magenta/pink text
    orange = "\x1b[1;33m"  # Yellow (orange-like)
    green = "\x1b[1;32m"  # Bright green text
    blue = "\x1b[1;34m"  # Bright blue text
    white = "\x1b[1;37m"  # Default white

    # Determine the color based on the value
    if value > 10_000_000:
        return pink
    elif value > 1_000_000:
        return orange
    elif value > 500_000:
        return green
    elif value > 100_000:
        return blue
    else:
        return ""  # Default to white for values below 100k

# Reusable function to determine the color based on value
def get_name_color_by_value(value):
    # ANSI escape codes for different colors
    teal = "\x1b[1;36m"  # Gold-like text (using bright yellow)
    purple = "\x1b[1;35m"  # Bright magenta/purple text
    red = "\x1b[1;31m"  # Bright red text
    pink = "\x1b[1;35m"  # Bright magenta/pink text
    orange = "\x1b[1;33m"  # Yellow (orange-like)
    green = "\x1b[1;32m"  # Bright green text
    blue = "\x1b[1;34m"  # Bright blue text
    white = "\x1b[1;37m"  # Default white

    # Determine the color based on the value
    if value > 1_000_000_000:
        return red  
    elif value > 250_000_000:
        return pink  
    elif value > 100_000_000:
        return orange
    elif value > 50_000_000:
        return green
    elif value > 10_000_000:
        return blue
    elif value > 1_000_000:
        return teal
    else:
        return white  # Default to white for values below 1 million



# Function to format the loot data with correct ANSI coloring based on value
def format_loot_data(loot_data):
    # ANSI escape code for reset
    reset = "\x1b[0m"  # Reset to default color
    white = "\x1b[0;37m"  # Default white text

    # Headers in white text
    headers = f"{white}{'Name':<25} {'$':<10} {'Amt':<10} {'Source':<20} {'Last Seen':<25}{reset}\n"
    table_separator = f"{white}{'-' * 85}{reset}\n"

    rows = []

    # Function to format the last_seen timestamp like Discord's timestamps
    def format_last_seen(last_seen):
        now = datetime.now()

        # Ensure last_seen is a datetime object; otherwise, try to convert it
        if isinstance(last_seen, str):
            try:
                last_seen = datetime.fromisoformat(last_seen)
            except ValueError:
                return "Unknown"
        elif not isinstance(last_seen, datetime):
            return "Unknown"

        # Calculate the difference between now and last_seen
        time_diff = now - last_seen
        seconds = time_diff.total_seconds()
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        days = int(hours // 24)

        # Format the time difference like Discord timestamps
        if minutes < 1:
            return "Just now"
        elif minutes < 60:
            return f"{minutes} minutes ago"
        elif hours < 24:
            return f"{hours} hours ago"
        else:
            return f"{days} days ago"

    # Loop through each row of loot data and apply coloring based on value
    for row in loot_data:
        rsn, item_name, value, quantity, source, last_seen = row

        # Get the color based on the value using the reusable function
        color = get_color_by_value(value)

        # Format the row with color and columns and append to list
        formatted_row = f"{color}{item_name:<25} {format_value(value):<10} {quantity:<10} {source:<20} {format_last_seen(last_seen):<20}{reset}\n"
        rows.append(formatted_row)

    # Return both the table header and the rows separately to handle splitting
    return headers + table_separator, rows

class LootPaginator(View):
    def __init__(self, loot_data_pages, current_page=0):
        super().__init__(timeout=180)
        self.loot_data_pages = loot_data_pages
        self.current_page = current_page
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()  # Clear existing buttons
        # Add the Previous button if not on the first page
        if self.current_page > 0:
            prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="previous_page")
            prev_button.callback = self.previous_page
            self.add_item(prev_button)

        # Add the Next button if not on the last page
        if self.current_page < len(self.loot_data_pages) - 1:
            next_button = Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_page")
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def send_page(self, interaction):
        # Display the current page with ANSI code block
        await interaction.response.edit_message(
            content=f"```ansi\n{self.loot_data_pages[self.current_page]}```",
            view=self
        )

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await self.send_page(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.loot_data_pages) - 1:
            self.current_page += 1
            self.update_buttons()
            await self.send_page(interaction)


# Function to handle the button click and display loot data with pagination
async def on_view_loot_button_click(interaction):
    discord_id = str(interaction.user.id)
    await interaction.response.defer(ephemeral=True)  # Defer early

    # Fetch loot data for the user
    loot_data = await fetch_loot_data(discord_id)

    if not loot_data:
        await interaction.followup.send("Nothin D:", ephemeral=True)
        return

    # Get the formatted loot data, split into headers and rows
    headers, rows = format_loot_data(loot_data)

    # Discord has a 2000 character limit, let's use a slightly smaller limit to leave room for the headers
    max_message_length = 1800

    current_message = headers  # Start the first message with the headers
    messages = []  # List to hold all message parts

    # Go through each row and ensure no row is split between messages
    for row in rows:
        # If adding this row exceeds the limit, add the current message to the list
        if len(current_message) + len(row) > max_message_length:
            messages.append(current_message)  # Save the current message
            current_message = headers + row  # Start a new message without headers for subsequent posts
        else:
            current_message += row  # Append row to current message

    # Add the last message if it contains any rows
    if current_message:
        messages.append(current_message)

    # Initialize the paginator view with the messages
    view = LootPaginator(messages)
    
    # Send the first page
    msg_list = [await interaction.followup.send(f"```ansi\n{messages[0]}```", view=view, ephemeral=True)]
    await clear_messages_after_timeout(msg_list)

# Task to periodically update the loot hiscores message
@tasks.loop(minutes=1)  # Adjust the loop interval as needed
async def post_loot_hiscores():
    await post_or_update_loot_hiscores(MEMBER_CHANNEL_ID)


async def clear_messages_after_timeout(msg_list):        
    #Clean up the messages after 3 minutes   
    await asyncio.sleep(120)
    try:
        for msg in msg_list:
            await msg.delete()
    except Exception as e:
        print(e)
        None