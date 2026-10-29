import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from faker import Faker

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tajny-klucz-sesji') # Wymagane do komunikatów flash

faker = Faker()

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-34267e89-konradbargenda2-f765.c.aivencloud.com'),
        port=int(os.environ.get('DB_PORT', 21548)),
        user=os.environ.get('DB_USER', 'avnadmin'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'defaultdb'),
        ssl_verify_cert=False  # Poprawny parametr SSL dla mysql-connector-python
    )

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
        flash(f"Błąd połączenia z bazą: {e}", "danger")
    
    return render_template('index.html', users=users)

@app.route('/generate', methods=['POST'])
def generate_users():
    try:
        count = int(os.environ.get('GENERATE_COUNT', 5)) # Domyślnie generuje 5 użytkowników
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Upewnij się, że tabela istnieje
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                city VARCHAR(100)
            );
        """)

        for _ in range(count):
            name = faker.name()
            email = faker.email()
            city = faker.city()
            cursor.execute(
                "INSERT INTO users (name, email, city) VALUES (%s, %s, %s)",
                (name, email, city)
            )
            
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Pomyślnie wygenerowano {count} nowych użytkowników!", "success")
    except Exception as e:
        flash(f"Błąd podczas generowania użytkowników: {e}", "danger")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)