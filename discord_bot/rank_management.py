# rank_management.py

import discord
from db import get_db_connection

async def change_rank_on_discord(guild: discord.Guild, discord_id: str, rank_name: str) -> str:
    """Change the rank of a user on Discord by managing their roles.

    Args:
        guild (discord.Guild): The guild where the rank change should happen.
        discord_id (str): The Discord ID of the user.
        rank_name (str): The rank name to assign as a role.

    Returns:
        str: 'Success' if the rank was updated, 'No Update Needed' if the rank was already correct, otherwise 'Fail'.
    """
    member = guild.get_member(discord_id)
    if not member:
        return "Fail: User not found"

    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Query the list of valid ranks from the database
        cursor.execute("SELECT NAME FROM rank_cfg WHERE POINTS is not null")
        valid_ranks = [row[0] for row in cursor.fetchall()]

        if rank_name not in valid_ranks:
            return "Fail: Rank does not exist in the database"

        # Find the role in the guild that matches the rank name
        role = discord.utils.get(guild.roles, name=rank_name)
        if not role:
            return "Fail: Role not found in Discord"

        # Check if the user already has the correct rank
        current_roles = [user_role.name for user_role in member.roles]
        if role.name in current_roles:
            return "No Update Needed: User already has the correct rank"

        # Remove all roles that could represent a rank (assuming rank roles are managed exclusively)
        for user_role in member.roles:
            if user_role.name in valid_ranks:
                await member.remove_roles(user_role)

        # Always apply the "ranked" role if the user doesn't already have it
        ranked_role_name = "ranked🙂🍌🌟"
        ranked_role = discord.utils.get(guild.roles, name=ranked_role_name)
        if ranked_role and ranked_role not in member.roles:
            await member.add_roles(ranked_role)
        


        # Add the new rank role
        await member.add_roles(role)
        return "Success"
    except Exception as e:
        print(f"Error: {e}")
        return "Fail: Could not update role"
    finally:
        cursor.close()
        db.close()
