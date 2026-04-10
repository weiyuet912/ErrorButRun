from flask import Flask, render_template, request, session, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy extention
from datetime import datetime
import os
import json

# --- Basic Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder='.', static_folder='static')
app.secret_key = 'lang_sushi_sql_2026'

# --- Database Configuration ---
# this will create a file named sushi_database.db in the project directory----this part of code is AI created
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_dir, 'sushi_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Define database model ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True) # ID column
    order_no = db.Column(db.String(20), unique=True) # order number
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    people = db.Column(db.Integer)
    details = db.Column(db.Text) # order details
    total = db.Column(db.String(20))
    time = db.Column(db.String(50)) # order time

# Create database tables
with app.app_context():
    db.create_all()

# --- Function using in the website ---
def is_opening_hours():
    return 12 <= datetime.now().hour < 20

def get_menu_data():
    json_path = os.path.join(current_dir, 'menu.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# --- Routing Logic ---

@app.route('/')
def index():
    return render_template('firstpage.html')

@app.route('/first_page', methods=['POST'])
def handle_first_page():
    if not is_opening_hours():
        return jsonify({"status": "error", "message": "Closed now.\nOpening hours: 12:00 – 20:00."})
    
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    people = request.form.get('people_count')

    session['user_info'] = {"name": last_name, "phone": phone, "people": people}
    return jsonify({"status": "success", "next_page": "/menu"})

@app.route('/menu')
def menu_page():
    if 'user_info' not in session: return redirect(url_for('index'))
    return render_template('menu.html', dishes=get_menu_data(), user=session['user_info'])

@app.route('/bill')
def bill_page():
    if 'user_info' not in session: return redirect(url_for('index'))
    return render_template('bill.html', dishes=get_menu_data(), user=session['user_info'])

# --- Confirm order and Store in SQL ---
@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if 'user_info' not in session:
        return jsonify({"status": "error", "message": "Session expired."})
    
    data = request.json
    user = session['user_info']
    
    # Create order number based on order count----this part of code is AI created
    order_count = Order.query.count()
    new_order_no = f"#{order_count + 1:03d}"
    
    # Create database record
    new_record = Order(
        order_no=new_order_no,
        name=user['name'],
        phone=user['phone'],
        people=int(user['people']),
        details=data.get('items'),
        total=data.get('total'),
        time=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    
    # Commit to database----this part of code is AI created
    try:
        db.session.add(new_record)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

# --- Admin Logic ---

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == '00000000':
        session['admin_logged_in'] = True
        return jsonify({"status": "success", "next_page": "/admin_orders"})
    return jsonify({"status": "error"})

@app.route('/admin_orders')
def admin_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    # Retrieve all orders from the database----this part of code is AI created 
    all_orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin_orders.html', orders=all_orders)

# Automatically create database tables
with app.app_context():
    db.create_all()
    print("Database created!")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
