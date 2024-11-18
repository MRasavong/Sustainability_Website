# Import required modules
from flask import Flask, render_template
import psycopg2
import os
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))


# Database connection setup
def get_db_connection():
    # Connect to the postgres database
    conn = psycopg2.connect(database="postgres", user="postgres", password="Uhosremote!", port="5433")
    return conn


# Render home page
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


# Render database page with most recent KWH data, sorted by meter name
@app.route('/show_entire_csv_data', methods=['GET'])
def show_recent_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch only the most recent data (e.g., last 156 records) from the postgres schema
    cur.execute('SELECT datetime, meter_reading, meter_name, stuck FROM kwh.kwh_last24hrs ORDER BY datetime DESC LIMIT 156;')
    kwh = cur.fetchall()

    cur.close()
    conn.close()

    # Sort data by the meter name (3rd column, index 2)
    kwh_sorted = sorted(kwh, key=lambda entry: entry[2].lower())  # sort alphabetically by meter_name

    # Render template with sorted KWH data
    return render_template('entire_csv_data.html', kwh=kwh_sorted)


# Render visualization page
@app.route('/visualization', methods=['GET', 'POST'])
def visualization():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch distinct meter names from the database
    cur.execute('SELECT DISTINCT meter_name FROM kwh.kwh_last24hrs ORDER BY meter_name;')
    meter_names = cur.fetchall()

    cur.close()
    conn.close()

    # Extract meter names from the result (list of tuples)
    meter_names_list = [meter[0] for meter in meter_names]

    # Render the visualization template and pass meter names
    return render_template('visualization.html', meters=meter_names_list)


if __name__ == '__main__':
    app.run(debug=True)
