# Standard library imports
import math
import os
import re
import json
import logging
import threading
from datetime import datetime, timedelta
from collections import deque
from logging.handlers import RotatingFileHandler

# Third-party imports
from flask import (
    Flask, render_template, request, jsonify, redirect, send_file, 
    url_for, flash, send_from_directory
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, 
    logout_user, current_user
)
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import mysql.connector



# Load environment variables from .env file
#
load_dotenv('config.env')

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initial global variables
db = None
cursor = None

# Global cache for player name to WOM ID mapping
player_name_to_wom_id = {}
cache_initialized = False  # Global flag to track initialization

def connect_db():
    global db, cursor
    if db is None or not db.is_connected():
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4' 
        )
        cursor = db.cursor()
        cursor.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")
        cursor.execute("SET character_set_client = 'utf8mb4'")
        cursor.execute("SET character_set_connection = 'utf8mb4'")
        cursor.execute("SET character_set_results = 'utf8mb4'")

# User model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Loading user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        connect_db()
        cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()  # Fetch the result
        db.close()

        if user_data:  # Check if any data was fetched
            return User(user_data[0], user_data[1], user_data[2])
        else:
            return None  # No user found, so return None
    except Exception as e:
        print(e)
        return


# Protect all routes except login and static files
@app.before_request
def require_login():
    if not current_user.is_authenticated and request.endpoint not in ['login', 'static', 'dink']:
        return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connect_db()
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        db.close()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/static/<path:filename>')
def serve_static(filename):
    try: return send_from_directory('static', filename)
    except: return

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector

# Change Password route
@app.route('/change_password', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Get current user's ID or username from Flask-Login's current_user
        user_id = current_user.id

        # Connect to the database and fetch the user's current password hash
        connect_db()
        cursor.execute("SELECT id, password FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        db.close()

        # Check if the current password is correct
        if user_data and check_password_hash(user_data[1], current_password):
            # Check if new password and confirm password match
            if new_password == confirm_password:
                # Hash the new password
                new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)

                # Update the password in the database
                connect_db()
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password_hash, user_id))
                db.commit()
                db.close()

                flash('Password changed successfully', 'success')
                return redirect(url_for('index'))  # Redirect to some page after success
            else:
                flash('New passwords do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')

    return render_template('change_password.html')





# Home route
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Function to hash passwords (for creating new users)
def create_user(username, password):
    hashed_password = generate_password_hash(password,  method='pbkdf2:sha256', salt_length=8)
    connect_db()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    db.commit()
    db.close()

@app.route('/points_tracking')
def points_tracking():
    return render_template('points_tracking.html')

@app.route('/members', methods=['GET'])
def get_members():
    connect_db()
    cursor.execute("SELECT WOM_ID, NAME, MAIN_WOM_ID, JOIN_DATE, `RANK`, POINTS, WOM_RANK, DISCORD_ID, ACCOUNT_TYPE, RSN, NEXT_RANK, CURRENT_RANK_POINTS, LAST_ACTIVE FROM rngstreet.vw_web_homepage where wom_rank <> 'Not In Clan';")
    members = cursor.fetchall()
    db.close()
    
    # Map the result to a list of dictionaries with meaningful keys
    member_list = [
        {
            'wom_id': member[0],
            'name': member[1],
            'mainWomId': member[2],
            'joinDate': member[3],
            'rank': member[4],
            'points': member[5],
            'inGameRank': member[6],
            'discordRank': member[7],
            'accountType': member[8],
            'rsn': member[9],
            'nextRank': member[10],
            'currentRankPoints': member[11],
            'lastActive': member[12]
        }
        for member in members
    ]

    return jsonify(member_list)

@app.route('/get_member/<int:wom_id>', methods=['GET'])
def get_member(wom_id):
    connect_db()
    cursor.execute("SELECT * FROM vw_web_homepage WHERE WOM_ID = %s", (wom_id,))
    member = cursor.fetchone()
    db.close()

    if member:
        return {
            'wom_id': member[0],
            'name': member[1],
            'rsn': member[9],
            'points': member[5],
            'rank': member[4],
            'nextRank': member[10],
            'inGameRank': member[6],
            'discordRank': member[7],
            'joinDate': member[3],
            'accountType': member[8],
            'lastActive': member[12]
        }
    else:
        return jsonify({'error': 'Member not found'}), 404

@app.route('/get_member_points/<int:wom_id>', methods=['GET'])
def get_member_points(wom_id):
    connect_db()
    query = """
        SELECT month,
        (xp_points + ehb_points + split_points + event_points + time_points)  as total_points,
        xp_points, ehb_points, split_points, event_points, time_points
        FROM member_points
        WHERE wom_id = %s
        ORDER BY month DESC
    """
    cursor.execute(query, (wom_id,))
    data = cursor.fetchall()

    # Convert the data to a serializable format (Decimal -> float)
    points_data = []
    for row in data:
        points_data.append({
            "MONTH": row[0],
            "TOTAL_POINTS": row[1],
            "XP_POINTS": float(row[2]),
            "EHB_POINTS": float(row[3]),
            "SPLIT_POINTS": float(row[4]),
            "EVENT_POINTS": float(row[5]),
            "TIME_POINTS": float(row[6])
        })

    return jsonify(points_data)



@app.route('/members/<int:wom_id>', methods=['POST'])
def update_member(wom_id):
    connect_db() 
    data = request.json
    cursor.execute("""
        UPDATE members 
        SET NAME=%s, MAIN_WOM_ID=%s, JOIN_DATE=%s, RANK=%s, POINTS=%s, 
            WOM_RANK=%s, DISCORD_RANK=%s, ACCOUNT_TYPE=%s, RSN=%s
        WHERE WOM_ID=%s
    """, (data['NAME'], data['MAIN_WOM_ID'], data['JOIN_DATE'], data['RANK'], data['POINTS'], 
          data['WOM_RANK'], data['DISCORD_RANK'], data['ACCOUNT_TYPE'], data['RSN'], wom_id))
    db.commit()
    db.close()
    return '', 204

@app.route('/points_tracking_data')
def points_tracking_data():
    connect_db() 
    # Get the selected month from the request arguments
    selected_month = request.args.get('month', default='202408', type=str)
    
    # Query to join members and member_points
    query = """
        SELECT
            m.WOM_ID,
            m.NAME AS NAME,
            case
                when m.RSN <> m.NAME
                then m.RSN
                else ''
            end as RSN,
            mp.MONTH AS MONTH,
            (mp.XP_POINTS + mp.EHB_POINTS + mp.EVENT_POINTS + mp.SPLIT_POINTS + mp.TIME_POINTS) AS TOTAL_POINTS,
            mp.XP_POINTS,
            mp.EHB_POINTS,
            mp.EVENT_POINTS,
            mp.SPLIT_POINTS,
            mp.TIME_POINTS
        FROM member_points mp
        JOIN members m ON mp.WOM_ID = m.WOM_ID
        WHERE mp.MONTH = %s
        ORDER BY 5 DESC;
    """
    
    cursor.execute(query, (selected_month,))
    
    # Fetch the results
    rows = cursor.fetchall()
    
    # Get the column names from the cursor
    column_names = [desc[0] for desc in cursor.description]
    
    # Convert rows to a list of dictionaries
    points_data = [dict(zip(column_names, row)) for row in rows]
    
    db.close()
    return jsonify(points_data)

@app.route('/update_points/<int:wom_id>/<int:month>', methods=['POST'])
def update_point(wom_id, month):
    connect_db() 
    data = request.json
    cursor.execute("""
        UPDATE member_points
        SET EVENT_POINTS=%s, SPLIT_POINTS=%s, TIME_POINTS=%s
        WHERE WOM_ID=%s AND MONTH=%s
    """, (data['EVENT_POINTS'], data['SPLIT_POINTS'], data['TIME_POINTS'], wom_id, month))
    db.commit()
    db.close()
    return jsonify({"status": "success"}), 200

@app.route('/update_all_points', methods=['POST'])
def update_all_points():
    connect_db() 
    data = request.json
    for row in data:
        cursor.execute("""
            UPDATE member_points
            SET EVENT_POINTS=%s, SPLIT_POINTS=%s, TIME_POINTS=%s
            WHERE WOM_ID=%s AND MONTH=%s
        """, (row['EVENT_POINTS'], row['SPLIT_POINTS'], row['TIME_POINTS'], row['WOM_ID'], row['MONTH']))
    db.commit()
    db.close()
    return jsonify({"status": "success"}), 200

@app.route('/get_months')
def get_months():
    connect_db() 
    cursor.execute("SELECT DISTINCT MONTH FROM member_points ORDER BY MONTH DESC")
    months = cursor.fetchall()
    db.close()
    return jsonify([month[0] for month in months])

@app.route('/rank_config')
def get_rank_config():
    return render_template('config.html')

@app.route('/get_rank_config')
def get_rank_config_data():
    connect_db() 
    cursor.execute("SELECT ID, NAME, DESCRIPTION, POINTS FROM rank_cfg ORDER BY ID;")
    rank_config = cursor.fetchall()
    
    # Convert the list of tuples to a list of dictionaries
    rank_config_data = []
    for row in rank_config:
        rank_config_data.append({
            "ID": row[0],
            "NAME": row[1],
            "DESCRIPTION": row[2],
            "POINTS": row[3]
        })
    
    db.close()
    return jsonify(rank_config_data)

@app.route('/update_rank_config', methods=['POST'])
def update_rank_config():
    connect_db() 
    data = request.json

    for entry in data:
        points = None
        if entry['points'] != '': 
            points = entry['points']
        if entry['id']:  # Update existing row
            cursor.execute("""
                UPDATE rank_cfg SET NAME = %s, DESCRIPTION = %s, POINTS = %s WHERE ID = %s
            """, (entry['name'], entry['description'], points, entry['id']))
        else:  # Insert new row
            cursor.execute("""
                INSERT INTO rank_cfg (NAME, DESCRIPTION, POINTS) VALUES (%s, %s, %s)
            """, (entry['name'], entry['description'], points))
    
    db.commit()
    db.close()
    return '', 204

@app.route('/points_config')
def points_config():
    return render_template('points_config.html')

@app.route('/get_points_config')
def get_points_config():
    connect_db() 
    cursor.execute("SELECT ID, CODE, NAME, VALUE, MONTHLY_LIMIT FROM points_cfg ORDER BY ID;")
    points_config = cursor.fetchall()
    
    # Convert the list of tuples to a list of dictionaries
    points_config_data = []
    for row in points_config:
        points_config_data.append({
            "ID": row[0],
            "CODE": row[1],
            "NAME": row[2],
            "VALUE": row[3],
            "MONTHLY_LIMIT": row[4]
        })
    db.close()
    
    return jsonify(points_config_data)

@app.route('/update_points_config', methods=['POST'])
def update_points_config():
    connect_db() 
    data = request.json

    for entry in data:
        if entry['id']:  # Update existing row
            cursor.execute("""
                UPDATE points_cfg SET CODE = %s, NAME = %s, VALUE = %s, MONTHLY_LIMIT = %s WHERE ID = %s
            """, (entry['code'], entry['name'], entry['value'], entry['monthlyLimit'], entry['id']))
        else:  # Insert new row
            cursor.execute("""
                INSERT INTO points_cfg (CODE, NAME, VALUE, MONTHLY_LIMIT) VALUES (%s, %s, %s, %s)
            """, (entry['code'], entry['name'], entry['value'], entry['monthlyLimit']))
    
    db.commit()
    db.close()
    return '', 204

@app.route('/ehb_config')
def ehb_config():
    return render_template('ehb_config.html')

@app.route('/approve_rank_up/<int:wom_id>', methods=['POST'])
def approve_rank_up(wom_id):
    connect_db()

    # First, get the NEXT_RANK value from the view
    cursor.execute("SELECT NEXT_RANK FROM vw_member_rankups WHERE WOM_ID = %s", (wom_id,))
    next_rank = cursor.fetchone()

    if next_rank:
        # Update the members table with the retrieved NEXT_RANK value
        cursor.execute("UPDATE members SET `RANK` = %s WHERE WOM_ID = %s", (next_rank[0], wom_id))
        db.commit()
        db.close()
        return '', 204
    else:
        return 'Next rank not found', 404
    

@app.route('/update_rsn/<int:wom_id>', methods=['POST'])
def update_rsn(wom_id):
    connect_db()
    data = request.json

    new_wom_id = data['new_wom_id']
    points_option = data['points_option']

    if points_option == 'merge':
        cursor.callproc('merge_points', [wom_id, new_wom_id])
        cursor.callproc('archive_member', [new_wom_id])

    elif points_option == 'keep':
        cursor.callproc('archive_member', [new_wom_id])

    # Update the members table with the new WOM ID
    cursor.execute("UPDATE members SET WOM_ID = %s WHERE WOM_ID = %s", (new_wom_id, wom_id))
    db.commit()
    db.close()

    return '', 204




@app.route('/link_account/<int:wom_id>', methods=['POST'])
def link_account(wom_id):
    connect_db()
    data = request.json
    main_wom_id = data['main_wom_id']
    alt_wom_id = data['alt_wom_id']
    
    # Fetch both entries based on WOM_ID
    cursor.execute("SELECT WOM_ID, DISCORD_ID FROM members WHERE WOM_ID IN (%s, %s)", (main_wom_id, alt_wom_id))
    accounts = cursor.fetchall()

    if len(accounts) != 2:
        db.close()
        return jsonify({'error': 'Invalid WOM_IDs provided'}), 400

    # Extract Discord IDs for both accounts
    main_account = next(acc for acc in accounts if acc[0] == main_wom_id)
    alt_account = next(acc for acc in accounts if acc[0] == alt_wom_id)

    main_discord_id = main_account[1]  # Discord ID for main account
    alt_discord_id = alt_account[1]    # Discord ID for alt account

    # Check if both accounts have empty Discord IDs
    if not main_discord_id  and not alt_discord_id:
        db.close()
        return jsonify({'error': 'Requires linking one account to a discord ID'}), 400

    # If one account has a Discord ID and the other does not, update the empty one
    if not main_discord_id and alt_discord_id != '':
        # Update main account's Discord ID
        cursor.execute("UPDATE members SET DISCORD_ID = %s WHERE WOM_ID = %s", (alt_discord_id, main_wom_id))
        db.commit()
    elif not alt_discord_id  and main_discord_id != '':
        # Update alt account's Discord ID
        cursor.execute("UPDATE members SET DISCORD_ID = %s WHERE WOM_ID = %s", (main_discord_id, alt_wom_id))
        db.commit()
    # Check if both have a Discord ID but they don't match
    elif main_discord_id != '' and alt_discord_id != '' and main_discord_id != alt_discord_id:
        db.close()
        return jsonify({'error': 'Account is already linked to a different Discord ID'}), 400

    db.close()
    return '', 204

@app.route('/unlink_account/<int:wom_id>', methods=['POST'])
def unlink_account(wom_id):
    connect_db()
    data = request.json
    cursor.execute("CALL remove_discord_id_from_member(%s)", (wom_id,))
    db.commit()
    db.close()
    return '', 204

@app.route('/update_name/<int:wom_id>', methods=['POST'])
def update_name(wom_id):
    connect_db()
    data = request.json
    cursor.execute("UPDATE members SET NAME = %s WHERE WOM_ID = %s", (data['name'], wom_id))
    db.commit()
    db.close()
    return '', 204

@app.route('/update_rank/<int:wom_id>', methods=['POST'])
def update_rank(wom_id):
    connect_db()
    data = request.json
    cursor.execute("UPDATE members SET `RANK` = %s WHERE WOM_ID = %s", (data['rank'], wom_id))
    db.commit()
    db.close()
    return '', 204

@app.route('/archive_member/<int:wom_id>', methods=['POST'])
def archive_member(wom_id):
    connect_db()
    data = request.json

    if data.get('points_option') == 'merge':
        new_wom_id = data['new_wom_id']
        cursor.callproc('merge_points', [new_wom_id, wom_id])
        cursor.callproc('archive_member', [wom_id])
    else:
        cursor.callproc('archive_member', [wom_id])

    db.commit()
    db.close()
    return '', 204

@app.route('/remove_alt/<int:wom_id>', methods=['POST'])
def remove_alt(wom_id):
    connect_db()
    
    cursor.execute("UPDATE members SET MAIN_WOM_ID = 0 WHERE WOM_ID = %s", (wom_id,))
    
    db.commit()
    db.close()

    return '', 204

recent_messages = deque(maxlen=50)  # Store up to 100 messages (adjust as needed)
cache_lock = threading.Lock()  # Ensure thread-safe access to the deque

def clean_expired_messages():
    """Remove messages older than 60 seconds from the deque."""
    now = datetime.now()
    with cache_lock:
        while recent_messages and recent_messages[0][0] < now - timedelta(seconds=60):
            recent_messages.popleft()

def is_duplicate(message_signature):
    """Check if the message is a duplicate."""
    with cache_lock:
        return any(signature == message_signature for _, signature in recent_messages)


def store_message_signature(message_signature):
    """Store the message signature with the current timestamp."""
    with cache_lock:
        recent_messages.append((datetime.now(), message_signature))

@app.route('/dink', methods=['GET', 'POST'])
def dink():
    global player_name_to_wom_id
    try:
        if request.method == 'GET':
            # Serve the dink.json file
            json_file_path = os.path.join(os.path.dirname(__file__), 'dink.json')
            if os.path.exists(json_file_path):
                return send_file(json_file_path, mimetype='application/json')
            else:
                return jsonify({"error": "dink.json file not found"}), 404
        # Get JSON payload from the 'payload_json' field
        data = request.form.get('payload_json')
        if data:
            data = json.loads(data)  # Convert JSON string to dictionary

            # Handle LOOT type
            if data['type'] == 'LOOT' and not data['seasonalWorld'] and data['clanName'] == 'RNG Street':
                connect_db()

                for item in data['extra']['items']:
                    if item['priceEach'] > 100:
                        discord_id = data['discordUser']['id'] if 'discordUser' in data else None
                        player_name_clean = re.sub(r'[^A-Za-z0-9 ]+', ' ', data['playerName'])
                        wom_id = player_name_to_wom_id.get(player_name_clean.lower(), None)

                        cursor.execute("""
                            INSERT INTO stg_loot (
                                unload_time, player_name, item_id, item_name, source, category, quantity, price_each, rarity, 
                                dink_account_hash, discord_id, world, regionid, wom_id
                            ) VALUES (
                                NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, (
                            player_name_clean, item['id'], item['name'],
                            data['extra']['source'], data['extra']['category'], item['quantity'],
                            item['priceEach'], item.get('rarity', None), data['dinkAccountHash'],
                            discord_id, data['world'], data['regionId'], wom_id
                        ))

                db.commit()
                cursor.close()
                db.close()
                return '', 200
            elif (
                data['type'] == 'CHAT' and
                data['clanName'] == 'RNG Street' and
                data['extra']['type'] == 'CLAN_MESSAGE'
            ):
                clean_expired_messages()
                message = data['extra'].get('message', '')

                # Create a unique message signature
                message_signature = message

                # Check for duplicate message
                if is_duplicate(message_signature):
                    logging.info("Duplicate message detected, skipping insert.")
                    return '', 200

                store_message_signature(message_signature)
                # pb_pattern = re.compile(
                #     r"(?P<player_name>[A-Za-z0-9\- ]+) has achieved a new (?P<boss_name>.+?) "
                #     r"(?:\(Team Size: (?P<team_size>\d+)(?: players)?\) )?personal best: "
                #     r"(?P<time>(?:\d+:)?\d{1,2}:\d{2}(?:\.\d{2})?)",
                #     re.IGNORECASE
                # )

                pb_pattern = re.compile(
                    r"(?P<player_name>[A-Za-z0-9_\- ]+) has achieved a new (?P<boss_name>[A-Za-z0-9' \(\)\-]+)"
                    r"(?: \(team size: (?P<team_size>\d+|Solo)(?: players)?\))?"
                    r"(?: (?P<mode>(?:Normal|Expert) mode(?: Challenge| Overall)?))? personal best: "
                    r"(?P<time>(?:\d+:)?\d{1,2}:\d{2}(?:\.\d{2})?)",
                    re.IGNORECASE
                )







                match = pb_pattern.search(message)
                if match:
                    # Extract details from the regex match
                    player_name = match.group('player_name').strip()
                    player_name = re.sub(r'[^A-Za-z0-9 ]+', ' ', player_name)
                    wom_id = player_name_to_wom_id.get(player_name.lower(), None)
                    boss_name = match.group('boss_name').strip()
                    mode = match.group('mode').strip() if match.group('mode') else None 
                    time_str = match.group('time')
                    unload_player_name = re.sub(r'[^A-Za-z0-9 ]+', ' ', data['playerName'])
                    team_size = match.group('team_size')  # Team size or None
                    if team_size:
                        if team_size.lower() == "solo":
                            team_size = 1
                        else:
                            team_size = int(team_size)
                    else:
                        team_size = None

                    if mode:
                        mode = mode.replace('mode ', '')
                        boss_name = f"{boss_name} {mode}"

                    # Parse time string
                    time_parts = list(map(float, time_str.split(':')))
                    total_seconds = sum(
                        part * 60 ** i for i, part in enumerate(reversed(time_parts))
                    )  # Handles HH:MM:SS and MM:SS formats

                    # Convert to ticks (1 tick = 0.6 seconds) (*10 to avoid floating point rounding issue)
                    total_ticks = math.ceil(math.ceil((total_seconds * 10) / 0.6)/10)
                    
                    # Re calculate total seconds to decimal
                    total_seconds = total_ticks * 0.6

                    # Insert into the database
                    connect_db()
                    try:
                        cursor.execute(
                            """
                            INSERT INTO stg_clan_pb (unload_time, player_name, boss_name, team_size, time_seconds, time_ticks, message, unload_player_name, wom_id)
                            VALUES (
                                NOW(), 
                                %s, %s, %s, %s, %s, %s, %s, %s
                            )
                            """,
                            (player_name, boss_name, team_size, total_seconds, total_ticks, message, unload_player_name, wom_id)
                        )

                        db.commit()
                    except Exception as e:
                        logging.error(f"Database error: {e}")
                        db.rollback()
                    finally:
                        cursor.close()
                        db.close()
                else:
                    logging.info(f" No match against message: {message}")
                    connect_db()
                    try:
                        cursor.execute(
                            """
                            INSERT INTO stg_clan_drops (unload_time, message)
                            VALUES (NOW(), %s)
                            """,
                            (message,)
                        )
                        db.commit()
                    except Exception as e:
                        logging.error(f"Database error while inserting drop message: {e}")
                        db.rollback()
                    finally:
                        cursor.close()
                        db.close()
                return '', 200
        return 'error', 200

    except Exception as e:
        player_name = data.get('playerName', 'Unknown')  # Safely get 'playerName' or default to 'Unknown'
        logging.error(f"Error: {e}. PlayerName: {player_name}")
        return 'error', 200
   
def refresh_cache():
    global player_name_to_wom_id
    try:
        connect_db()
        cursor.execute("SELECT lower(rsn), wom_id FROM members WHERE wom_rank IS NOT NULL")
        player_name_to_wom_id = {row[0]: row[1] for row in cursor.fetchall()}
        # logging.error(f"Success refreshing cache")
        cursor.close()
        db.close()
    except Exception as e:
        logging.error(f"Error refreshing cache: {e}")
    
    # Schedule the next cache refresh
    threading.Timer(300, refresh_cache).start()  # Refresh every 5 minutes

@app.before_request
def initialize_cache():
    global cache_initialized
    if not cache_initialized:
        app.logger.info("Initializing cache...")
        refresh_cache()
        cache_initialized = True


if __name__ == "__main__":
    # Determine if running in production or development
    if os.getenv('ENV') == 'prod':
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        app.run(host='127.0.0.1', port=8080, debug=True)

# Set up logging
if not app.debug:
    # Rotating file handler for logs
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    
    # Optional: Set up basic logging level
    logging.basicConfig(level=logging.INFO)
