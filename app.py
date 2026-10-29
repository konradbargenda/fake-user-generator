import os
import mysql.connector
from flask import Flask, render_template

app = Flask(__name__)

# Konfiguracja bezpieczna (pobierana ze zmiennych środowiskowych)
db_config = {
    'host': os.environ.get('DB_HOST', 'mysql-34267e89-konradbargenda2-f765.c.aivencloud.com'),
    'port': int(os.environ.get('DB_PORT', 21548)),
    'user': os.environ.get('DB_USER', 'avnadmin'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': 'defaultdb',
    'ssl_disabled': False,
    'ssl_verify': True
}

@app.route('/')
def index():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.callproc('sp_generate_user_batch', ('en_US', 12345, 1, 10))
        
        users = []
        for result in cursor.stored_results():
            users = result.fetchall()
            
        cursor.close()
        conn.close()
        
        return render_template('index.html', users=users)
    except Exception as e:
        return f"Błąd połączenia z bazą: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)