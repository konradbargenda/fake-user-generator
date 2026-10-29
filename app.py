import os
import math
import random
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from faker import Faker

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key-session')

faker = Faker()

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-34267e89-konradbargenda2-f765.c.aivencloud.com'),
        port=int(os.environ.get('DB_PORT', 21548)),
        user=os.environ.get('DB_USER', 'avnadmin'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'defaultdb'),
        ssl_verify_cert=False
    )

def generate_uniform_sphere_coordinates():
    phi = random.uniform(0, 2 * math.pi)
    costheta = random.uniform(-1, 1)
    theta = math.acos(costheta)
    lat = math.degrees(theta) - 90
    lon = math.degrees(phi) - 180
    return f"{lat:.6f}, {lon:.6f}"

def generate_normal_distribution_value(mean, std_dev, min_val, max_val):
    val = int(random.gauss(mean, std_dev))
    return max(min_val, min(max_val, val))

def generate_user_attributes(locale, seed, batch_index, user_index):
    combined_seed = hash((locale, seed, batch_index, user_index)) & 0xFFFFFFFF
    random.seed(combined_seed)
    
    use_title = random.choice([True, False])
    use_middle = random.choice([True, False])
    
    title = random.choice(["Mr.", "Ms.", "Dr.", "Prof."]) if use_title else ""
    first_name = faker.first_name()
    middle_name = faker.first_name() if use_middle else ""
    last_name = faker.last_name()
    
    name_parts = [p for p in [title, first_name, middle_name, last_name] if p]
    full_name = " ".join(name_parts)
    
    gender = random.choice(['Male', 'Female', 'Other'])
    address = faker.address().replace('\n', ', ')
    coordinates = generate_uniform_sphere_coordinates()
    
    height = generate_normal_distribution_value(175, 10, 140, 210)
    weight = generate_normal_distribution_value(70, 15, 40, 140)
    eyes = random.choice(['Blue', 'Green', 'Hazel', 'Brown', 'Amber'])
    
    phone_format = random.choice([
        f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        f"({random.randint(20,99)}) {random.randint(100,999)} {random.randint(1000,9999)}",
        f"00{random.randint(10,99)} {random.randint(1000,999999)}"
    ])
    email = faker.email()
    
    return (full_name, gender, address, coordinates, height, weight, eyes, phone_format, email, locale)

@app.route('/')
def index():
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
    try:
        count = int(os.environ.get('GENERATE_COUNT', 5))
        locale = request.form.get('locale', 'en_US')
        seed = int(request.form.get('seed', 42))
        batch_index = int(request.form.get('batch_index', 1))

        conn = get_db_connection()
        cursor = conn.cursor()
        
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

        for i in range(count):
            user_data = generate_user_attributes(locale, seed, batch_index, i)
            cursor.execute(
                """INSERT INTO users (name, gender, address, coordinates, height, weight, eyes, phone, email, locale) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                user_data
            )
            
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Successfully generated {count} new users for locale {locale}!", "success")
    except Exception as e:
        flash(f"Error during user generation: {e}", "danger")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)