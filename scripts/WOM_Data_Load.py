from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd
import mysql.connector
from config import DB_CONFIG  # Import the DB configuration

# Database config
mydb = mysql.connector.connect(**DB_CONFIG)
mycursor = mydb.cursor()

# Set date ranges to start and end of current month
startDate = datetime.today() + relativedelta(months=0, day=1, hour=0, minute=0, second=0, microsecond=0)
endDate = startDate + relativedelta(day=31, hour=23, minute=59, second=59)
month = int(startDate.strftime("%Y%m"))
startDate = startDate.astimezone(timezone.utc)
endDate = endDate.astimezone(timezone.utc)

# Final data to be loaded into DB from WOM
members_load = []
ehp_load = []
ehb_load = []

# Gets a list of clan members from WOM
response = requests.get('https://api.wiseoldman.net/v2/groups/916')
for player in response.json()["memberships"]:
    new_entry = (
        player["player"]["id"],
        player["player"]["displayName"],
        player["role"],
        player["player"]["type"]
    )
    members_load.append(new_entry)

# Get XP Gains from WOM
params = {'metric': 'ehp',  'startDate': startDate, 'endDate': endDate, 'limit' : 500}
response = requests.get('https://api.wiseoldman.net/v2/groups/916/gained', params=params)
for player in response.json():
    new_entry = (
        player["player"]["id"],
        month,
        player["player"]["displayName"],
        "EHP",
        player["data"]["gained"]
    )
    ehp_load.append(new_entry)

# Get EHB Gains from WOM
params = {'metric': 'ehb',  'startDate': startDate, 'endDate': endDate, 'limit' : 500}
response = requests.get('https://api.wiseoldman.net/v2/groups/916/gained', params=params)
for player in response.json():
    new_entry = (
        player["player"]["id"],
        month,
        player["player"]["displayName"],
        "EHB",
        player["data"]["gained"]
    )
    ehb_load.append(new_entry)

# Load collected data into DB
mycursor.execute("TRUNCATE TABLE stg_gained")
mycursor.execute("TRUNCATE TABLE stg_members")
mycursor.executemany("""
                 INSERT INTO stg_members (WOM_ID, RSN, WOM_RANK, ACCOUNT_TYPE) 
                 VALUES (%s, %s, %s, %s)                 
                 """, members_load)
mycursor.executemany("""
                 INSERT INTO stg_gained (WOM_ID, MONTH, RSN, METRIC, GAINED) 
                 VALUES (%s, %s, %s, %s, %s)                 
                 """, ehp_load)
mycursor.executemany("""
                 INSERT INTO stg_gained (WOM_ID, MONTH, RSN, METRIC, GAINED) 
                 VALUES (%s, %s, %s, %s, %s)                 
                 """, ehb_load)
mydb.commit()

# Push data through to live layer
mycursor.execute("CALL update_members()")
mycursor.execute("CALL update_member_points()")
mydb.commit()
