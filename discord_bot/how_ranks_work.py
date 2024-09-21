import discord

def get_how_ranks_work(interaction: discord.Interaction):
    guild = interaction.guild

    # Retrieve the emojis from the server
    skilling_emoji = discord.utils.get(guild.emojis, name="99")
    bossing_emoji = discord.utils.get(guild.emojis, name="Comfyinfepepe")
    split_emoji = discord.utils.get(guild.emojis, name="gp")
    event_emoji = discord.utils.get(guild.emojis, name="WoahMama2") 
    cadet_emoji = discord.utils.get(guild.emojis, name="Cadet") 

    # Create the embed
    embed = discord.Embed(
        title="How Ranks Work",
        description="""
        Ranks in RNG Street are based on a combination of Skilling, Bossing, Splitting Loots and Event Participation
        ‎ 
        """,
        color=discord.Color.blue()
    )

    # Add fields for each point category
    embed.add_field(
        name=f"{skilling_emoji} EHP (Efficient Hours Played - Skilling Points)",
        value="""
        Efficient Hours Played (EHP) is a way of scaling points based on the difficulty or time required to level a skill. It measures the amount of experience needed to represent one hour of gameplay at maximum efficiency for a given skill.
        For example, at level 70 you would need either 56k Agility XP or 250k Firemaking XP to earn 1 EHP. This reflects the relative time investment and difficulty of leveling different skills.
        
        In the clan, 4 EHP gained translates into 1 clan point.

        Find out more about EHP rates: [Wise Old Man - EHP](https://wiseoldman.net/ehp/main)
        ‎ 
        """,
        inline=False
    )

    embed.add_field(
        name=f"{bossing_emoji} EHB (Efficient Hours Bossed - Bossing Points)",
        value="""
        Efficient Hours Bossed (EHB) is a similar concept to EHP, but it applies to bossing. EHB scales based on the difficulty and time required to defeat different bosses. For example, completing a raid may count for more EHB than killing a lower-level boss because of the increased time and effort involved.

        In the clan, 3 EHB earned translates into 1 clan point.

        Find out more about EHB rates: [Wise Old Man - EHB](https://wiseoldman.net/ehb/main)
        ‎ 
        """,
        inline=False
    )

    embed.add_field(
        name=f"{split_emoji} Split Points",
        value="""
        Loot splits posted in the **#phat-loots-and-achievements** or **#clan-scrapbook** channel and tagged with the keywork **split** earn you 1 point. 
        A minimum item value of 10m is needed for the split, and 5m must be shared.
        ‎ 
        """,
        inline=False
    )

    embed.add_field(
        name=f"{event_emoji} Event Points",
        value="""
        Participate in a clan event and earn 1 point as a participation reward.
        Rank in the top 5 or top 10 of a tracked clan event, or win special events like bingo or tile-race, to earn 3 additional points. 
        ‎ 
        """,
        inline=False
    )

    embed.add_field(
        name=f"🕐 Time Points",
        value=f"""
        In addition to activity-based points, you earn 4 clan points per month up to 
        {cadet_emoji}Cadet rank.
        ‎ 
        """,
        inline=False
    )

    return embed
