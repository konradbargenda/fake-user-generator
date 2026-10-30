import os
import math
import random
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key-session')

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-34267e89-konradbargenda2-f765.c.aivencloud.com'),
        port=int(os.environ.get('DB_PORT', 21548)),
        user=os.environ.get('DB_USER', 'avnadmin'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'defaultdb'),
        ssl_verify_cert=False,
        autocommit=True
    )

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS names (
                id INT AUTO_INCREMENT PRIMARY KEY,
                locale VARCHAR(20),
                category VARCHAR(20),
                val VARCHAR(100)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150),
                gender VARCHAR(50),
                address VARCHAR(255),
                coordinates VARCHAR(100),
                height INT,
                weight INT,
                eyes VARCHAR(50),
                phone VARCHAR(50),
                email VARCHAR(100),
                locale VARCHAR(20),
                seed INT,
                batch_index INT
            );
        """)
        
        for col, col_type in [('locale', 'VARCHAR(20)'), ('seed', 'INT'), ('batch_index', 'INT')]:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type};")
            except Exception:
                pass

        cursor.execute("SELECT COUNT(*) FROM names;")
        count = cursor.fetchone()[0]
        if count == 0:
            en_firsts = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"]
            en_lasts = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker"]
            
            de_firsts = ["Hans", "Anna", "Stefan", "Maria", "Michael", "Sabine", "Thomas", "Karin", "Andreas", "Monika", "Wolfgang", "Ursula", "Klaus", "Erika", "Dieter", "Helga", "Jürgen", "Renate", "Peter", "Bernd", "Gisela", "Manfred", "Ingrid", "Heinz", "Brigitte", "Günter", "Christa", "Werner", "Hannelore"]
            de_lasts = ["Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann", "Braun", "Krüger", "Hofmann", "Hartmann", "Lange", "Schmitt", "Werner", "Schmitz", "Krause", "Meier", "Lehmann"]

            name_inserts = []
            for f in en_firsts:
                name_inserts.append(('en_US', 'first', f))
            for l in en_lasts:
                name_inserts.append(('en_US', 'last', l))
            for f in de_firsts:
                name_inserts.append(('de_DE', 'first', f))
            for l in de_lasts:
                name_inserts.append(('de_DE', 'last', l))
                
            cursor.executemany("INSERT INTO names (locale, category, val) VALUES (%s, %s, %s);", name_inserts)
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Init DB Error: {e}")

def fetch_names_from_db(locale):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT category, val FROM names WHERE locale = %s;", (locale,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    firsts = [r['val'] for r in rows if r['category'] == 'first']
    lasts = [r['val'] for r in rows if r['category'] == 'last']
    if not firsts:
        firsts = ['DefaultFirst']
    if not lasts:
        lasts = ['DefaultLast']
    return firsts, lasts

def generate_sphere_coordinates(rng):
    phi = rng.uniform(0, 2 * math.pi)
    costheta = rng.uniform(-1, 1)
    theta = math.acos(costheta)
    lat = math.degrees(theta) - 90
    lon = math.degrees(phi) - 180
    return f"{lat:.6f}, {lon:.6f}"

def generate_physical_attributes(rng):
    height = int(rng.gauss(175, 10))
    height = max(140, min(210, height))
    weight = int(rng.gauss(70, 15))
    weight = max(40, min(140, weight))
    eyes = rng.choice(['Blue', 'Green', 'Hazel', 'Brown', 'Amber'])
    gender = rng.choice(['Male', 'Female', 'Other'])
    return height, weight, eyes, gender

def generate_formatted_name(rng, first_names, last_names):
    use_title = rng.choice([True, False])
    use_middle = rng.choice([True, False])
    title = rng.choice(["Mr.", "Ms.", "Dr.", "Prof."]) if use_title else ""
    first = rng.choice(first_names)
    middle = rng.choice(first_names) if use_middle else ""
    last = rng.choice(last_names)
    parts = [p for p in [title, first, middle, last] if p]
    return " ".join(parts)

def generate_formatted_address(rng, locale):
    street_num = rng.randint(1, 999)
    if locale == 'de_DE':
        streets = ['Hauptstraße', 'Gartenstraße', 'Bahnhofstraße', 'Schulstraße', 'Lindenstraße']
        cities = ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne']
        street = rng.choice(streets)
        city = rng.choice(cities)
        postal = f"{rng.randint(10000, 99999)}"
        return f"{street} {street_num}, {postal} {city}"
    else:
        streets = ['Main St', 'Oak Rd', 'Pine St', 'Maple Ave', 'Cedar Ln']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        street = rng.choice(streets)
        city = rng.choice(cities)
        postal = f"{rng.randint(10000, 99999)}"
        return f"{street} #{street_num}, {city}, NY {postal}"

def generate_phone_number(rng, locale):
    if locale == 'de_DE':
        return f"+49 {rng.randint(100,999)} {rng.randint(1000000,9999999)}"
    else:
        return f"+1 ({rng.randint(200,999)}) {rng.randint(100,999)}-{rng.randint(1000,9999)}"

def generate_email(rng, name):
    clean_name = name.lower().replace('.', '').replace(' ', '')
    domain = rng.choice(['example.com', 'test.org', 'mail.net', 'fakeuser.io'])
    number = rng.randint(10, 999)
    return f"{clean_name}{number}@{domain}"

def generate_user_record(locale, seed, global_absolute_index, first_names, last_names):
    seed_str = f"{locale}_{seed}_{global_absolute_index}"
    hash_val = int(hashlib.md5(seed_str.encode('utf-8')).hexdigest(), 16) & 0xFFFFFFFF
    rng = random.Random(hash_val)
    
    name = generate_formatted_name(rng, first_names, last_names)
    height, weight, eyes, gender = generate_physical_attributes(rng)
    address = generate_formatted_address(rng, locale)
    coordinates = generate_sphere_coordinates(rng)
    phone = generate_phone_number(rng, locale)
    email = generate_email(rng, name)
    
    return (name, gender, address, coordinates, height, weight, eyes, phone, email, locale, seed, global_absolute_index)

def get_or_create_batch(locale, seed, batch_index, count=10):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch existing users for this batch
    cursor.execute(
        "SELECT * FROM users WHERE locale = %s AND seed = %s AND batch_index = %s ORDER BY id ASC;",
        (locale, seed, batch_index)
    )
    users = cursor.fetchall()
    
    # If we don't have exactly 10 users, clear incomplete ones and generate the full batch of 10
    if len(users) != count:
        del_cursor = conn.cursor()
        del_cursor.execute(
            "DELETE FROM users WHERE locale = %s AND seed = %s AND batch_index = %s;",
            (locale, seed, batch_index)
        )
        del_cursor.close()

        first_names, last_names = fetch_names_from_db(locale)
        ins_cursor = conn.cursor()
        for i in range(count):
            global_absolute_index = (batch_index - 1) * count + i
            user_data = generate_user_record(locale, seed, global_absolute_index, first_names, last_names)
            ins_cursor.execute(
                """INSERT INTO users (name, gender, address, coordinates, height, weight, eyes, phone, email, locale, seed, batch_index) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                user_data
            )
        ins_cursor.close()
        
        cursor.execute(
            "SELECT * FROM users WHERE locale = %s AND seed = %s AND batch_index = %s ORDER BY id ASC;",
            (locale, seed, batch_index)
        )
        users = cursor.fetchall()
        
    cursor.close()
    conn.close()
    return users

@app.route('/')
def index():
    init_db()
    locale = request.args.get('locale', 'en_US')
    try:
        seed = int(request.args.get('seed', 42))
    except ValueError:
        seed = 42
    try:
        batch_index = int(request.args.get('batch_index', 1))
    except ValueError:
        batch_index = 1
        
    users = []
    try:
        users = get_or_create_batch(locale, seed, batch_index, 10)
    except Exception as e:
        flash(f"Database error: {e}", "danger")
        
    return render_template('index.html', users=users, current_locale=locale, current_seed=seed, current_batch=batch_index)

@app.route('/generate', methods=['POST'])
def generate_users():
    locale = request.form.get('locale', 'en_US')
    try:
        seed = int(request.form.get('seed', 42))
    except ValueError:
        seed = 42
    try:
        batch_index = int(request.form.get('batch_index', 1))
    except ValueError:
        batch_index = 1
        
    return redirect(url_for('index', locale=locale, seed=seed, batch_index=batch_index))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)