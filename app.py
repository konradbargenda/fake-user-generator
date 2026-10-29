import os
import math
import random
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
        ssl_verify_cert=False
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
                locale VARCHAR(20)
            );
        """)
        cursor.execute("SELECT COUNT(*) FROM names;")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_names = [
                ('en_US', 'first', 'James'), ('en_US', 'first', 'Mary'), ('en_US', 'first', 'John'), ('en_US', 'first', 'Patricia'),
                ('en_US', 'first', 'Robert'), ('en_US', 'first', 'Jennifer'), ('en_US', 'first', 'Michael'), ('en_US', 'first', 'Linda'),
                ('en_US', 'first', 'William'), ('en_US', 'first', 'Elizabeth'), ('en_US', 'last', 'Smith'), ('en_US', 'last', 'Johnson'),
                ('en_US', 'last', 'Williams'), ('en_US', 'last', 'Brown'), ('en_US', 'last', 'Jones'), ('en_US', 'last', 'Miller'),
                ('en_US', 'last', 'Davis'), ('en_US', 'last', 'Garcia'), ('en_US', 'last', 'Rodriguez'), ('en_US', 'last', 'Wilson'),
                ('de_DE', 'first', 'Hans'), ('de_DE', 'first', 'Anna'), ('de_DE', 'first', 'Stefan'), ('de_DE', 'first', 'Maria'),
                ('de_DE', 'first', 'Michael'), ('de_DE', 'first', 'Sabine'), ('de_DE', 'first', 'Thomas'), ('de_DE', 'first', 'Karin'),
                ('de_DE', 'first', 'Andreas'), ('de_DE', 'first', 'Monika'), ('de_DE', 'last', 'Schmidt'), ('de_DE', 'last', 'Schneider'),
                ('de_DE', 'last', 'Fischer'), ('de_DE', 'last', 'Weber'), ('de_DE', 'last', 'Meyer'), ('de_DE', 'last', 'Wagner'),
                ('de_DE', 'last', 'Becker'), ('de_DE', 'last', 'Schulz'), ('de_DE', 'last', 'Hoffmann'), ('de_DE', 'last', 'Schäfer')
            ]
            cursor.executemany("INSERT INTO names (locale, category, val) VALUES (%s, %s, %s);", sample_names)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Init DB error: {e}")

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

def generate_user_record(locale, seed, batch_index, user_index, first_names, last_names):
    combined_seed = hash((locale, seed, batch_index, user_index)) & 0xFFFFFFFF
    rng = random.Random(combined_seed)
    
    name = generate_formatted_name(rng, first_names, last_names)
    height, weight, eyes, gender = generate_physical_attributes(rng)
    address = generate_formatted_address(rng, locale)
    coordinates = generate_sphere_coordinates(rng)
    phone = generate_phone_number(rng, locale)
    email = generate_email(rng, name)
    
    return (name, gender, address, coordinates, height, weight, eyes, phone, email, locale)

@app.route('/')
def index():
    init_db()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 20;")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        users = []
        flash(f"Database connection error: {e}", "danger")
    return render_template('index.html', users=users)

@app.route('/generate', methods=['POST'])
def generate_users():
    init_db()
    try:
        count = int(os.environ.get('GENERATE_COUNT', 5))
        locale = request.form.get('locale', 'en_US')
        seed = int(request.form.get('seed', 42))
        batch_index = int(request.form.get('batch_index', 1))

        first_names, last_names = fetch_names_from_db(locale)

        conn = get_db_connection()
        cursor = conn.cursor()

        for i in range(count):
            user_data = generate_user_record(locale, seed, batch_index, i, first_names, last_names)
            cursor.execute(
                """INSERT INTO users (name, gender, address, coordinates, height, weight, eyes, phone, email, locale) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                user_data
            )

        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Successfully generated {count} users for locale {locale}!", "success")
    except Exception as e:
        flash(f"Error during user generation: {e}", "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)