# server.py
import os
import json
import sqlite3
import random
import string
from datetime import datetime, timedelta
from functools import wraps
import pandas as pd
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import jwt
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'qat_database.db'
app.config['BACKUP_FOLDER'] = 'backups'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database initialization
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL,  # buyer, seller, driver, admin
            store_name TEXT,
            store_description TEXT,
            wallet_balance REAL DEFAULT 0,
            rating REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Markets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            latitude REAL,
            longitude REAL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Washing stations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS washing_stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id INTEGER,
            name TEXT NOT NULL,
            owner_name TEXT,
            phone TEXT,
            address TEXT,
            capacity INTEGER,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (market_id) REFERENCES markets (id)
        )
    ''')
    
    # Drivers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            vehicle_type TEXT,
            vehicle_number TEXT,
            current_location TEXT,
            available BOOLEAN DEFAULT 1,
            rating REAL DEFAULT 0,
            total_deliveries INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            type TEXT,
            stock INTEGER DEFAULT 0,
            washing_available BOOLEAN DEFAULT 0,
            rating REAL DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            images TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users (id)
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            buyer_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            market_id INTEGER,
            washing_station_id INTEGER,
            driver_id INTEGER,
            total_amount REAL NOT NULL,
            washing_amount REAL DEFAULT 0,
            delivery_fee REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',  # pending, confirmed, preparing, washing, delivering, delivered, cancelled
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            delivery_address TEXT,
            sales_code TEXT UNIQUE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES users (id),
            FOREIGN KEY (seller_id) REFERENCES users (id),
            FOREIGN KEY (market_id) REFERENCES markets (id),
            FOREIGN KEY (washing_station_id) REFERENCES washing_stations (id),
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
        )
    ''')
    
    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            washing BOOLEAN DEFAULT 0,
            washing_price REAL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Transactions table (for wallet)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,  # deposit, withdraw, purchase, sale, refund
            amount REAL NOT NULL,
            payment_method TEXT,
            reference TEXT,
            status TEXT DEFAULT 'pending',  # pending, completed, failed
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT,  # order, payment, system, promotion
            related_id INTEGER,
            read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Ads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            link TEXT,
            target_audience TEXT,  # all, buyers, sellers
            bg_color TEXT,
            text_color TEXT,
            btn_color TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            budget REAL,
            clicks INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Ad packages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            duration_days INTEGER,
            price REAL NOT NULL,
            features TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_type TEXT NOT NULL,  # product, seller, driver
            target_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # System settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default settings
    default_settings = [
        ('app_name', 'تطبيق قات', 'اسم التطبيق'),
        ('support_email', 'support@qat-app.com', 'بريد الدعم'),
        ('support_phone', '771831482', 'هاتف الدعم'),
        ('seller_commission', '5', 'نسبة عمولة البائعين (%)'),
        ('delivery_fee', '15', 'رسوم التوصيل (ريال)'),
        ('washing_fee', '100', 'رسوم غسل القات (ريال)'),
        ('primary_color', '#2E7D32', 'اللون الرئيسي'),
        ('text_color', '#333333', 'لون النص'),
        ('bg_color', '#F5F7FA', 'لون الخلفية'),
        ('currency', 'ريال', 'العملة'),
        ('min_deposit', '10', 'أقل مبلغ للإيداع'),
        ('max_deposit', '5000', 'أكثر مبلغ للإيداع')
    ]
    
    for key, value, description in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)', 
                      (key, value, description))
    
    # Create default admin user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@qat.com'")
    if cursor.fetchone()[0] == 0:
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, user_type, wallet_balance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('مدير النظام', 'admin@qat.com', '771831482', hashed_password, 'admin', 0))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Utility functions
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_token(user_id, user_type):
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing!'}), 401
        
        try:
            payload = verify_token(token)
            if not payload:
                return jsonify({'success': False, 'message': 'Invalid token!'}), 401
        except:
            return jsonify({'success': False, 'message': 'Invalid token!'}), 401
        
        request.user_id = payload['user_id']
        request.user_type = payload['user_type']
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing!'}), 401
        
        try:
            payload = verify_token(token)
            if not payload or payload['user_type'] != 'admin':
                return jsonify({'success': False, 'message': 'Admin access required!'}), 403
        except:
            return jsonify({'success': False, 'message': 'Invalid token!'}), 401
        
        request.user_id = payload['user_id']
        request.user_type = payload['user_type']
        
        return f(*args, **kwargs)
    return decorated

def generate_sales_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_order_number():
    return f'ORD{datetime.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}'

def create_notification(user_id, title, message, type='system', related_id=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notifications (user_id, title, message, type, related_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, title, message, type, related_id))
    conn.commit()
    conn.close()

# API Routes

# Authentication
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type', 'buyer')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'})
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND user_type = ?', (email, user_type))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user['password']):
        if not user['active']:
            return jsonify({'success': False, 'message': 'الحساب موقوف'})
        
        token = generate_token(user['id'], user['user_type'])
        user_data = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
            'type': user['user_type'],
            'store_name': user['store_name'],
            'wallet_balance': user['wallet_balance']
        }
        
        # Create welcome notification
        create_notification(user['id'], 'مرحباً بك!', 'تم تسجيل دخولك بنجاح إلى تطبيق قات')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user_data,
            'message': 'تم تسجيل الدخول بنجاح'
        })
    
    return jsonify({'success': False, 'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['name', 'email', 'phone', 'password', 'confirm_password', 'user_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})
    
    if data['password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'كلمات المرور غير متطابقة'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'البريد الإلكتروني مسجل مسبقاً'})
    
    # Hash password
    hashed_password = hash_password(data['password'])
    
    # Insert new user
    cursor.execute('''
        INSERT INTO users (name, email, phone, password, user_type, store_name, store_description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['email'],
        data['phone'],
        hashed_password,
        data['user_type'],
        data.get('store_name', ''),
        data.get('store_description', '')
    ))
    
    user_id = cursor.lastrowid
    
    # Create driver record if user is a driver
    if data['user_type'] == 'driver':
        cursor.execute('''
            INSERT INTO drivers (user_id, name, phone)
            VALUES (?, ?, ?)
        ''', (user_id, data['name'], data['phone']))
    
    conn.commit()
    conn.close()
    
    # Create welcome notification
    create_notification(user_id, 'مرحباً بك في تطبيق قات!', 'تم إنشاء حسابك بنجاح')
    
    return jsonify({
        'success': True,
        'message': 'تم إنشاء الحساب بنجاح'
    })

# Products
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get query parameters
    seller_id = request.args.get('seller_id')
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = '''
        SELECT p.*, u.name as seller_name, u.store_name
        FROM products p
        JOIN users u ON p.seller_id = u.id
        WHERE p.active = 1 AND u.active = 1
    '''
    params = []
    
    if seller_id:
        query += ' AND p.seller_id = ?'
        params.append(seller_id)
    
    if category:
        query += ' AND p.type = ?'
        params.append(category)
    
    if search:
        query += ' AND (p.name LIKE ? OR p.description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY p.created_at DESC'
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(product) for product in products])

@app.route('/api/products', methods=['POST'])
@token_required
def create_product():
    if request.user_type != 'seller':
        return jsonify({'success': False, 'message': 'غير مصرح للبائعين فقط'})
    
    data = request.get_json()
    
    required_fields = ['name', 'price', 'stock']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (seller_id, name, description, price, type, stock, washing_available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        request.user_id,
        data['name'],
        data.get('description', ''),
        data['price'],
        data.get('type', ''),
        data['stock'],
        data.get('washing_available', False)
    ))
    
    product_id = cursor.lastrowid
    
    # Create notification for seller
    create_notification(
        request.user_id,
        'تم إضافة منتج جديد',
        f'تم إضافة منتج "{data["name"]}" بنجاح'
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'تم إضافة المنتج بنجاح',
        'product_id': product_id
    })

# Orders
@app.route('/api/orders/create', methods=['POST'])
@token_required
def create_order():
    data = request.get_json()
    
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'success': False, 'message': 'السلة فارغة'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get buyer wallet balance
    cursor.execute('SELECT wallet_balance FROM users WHERE id = ?', (request.user_id,))
    buyer = cursor.fetchone()
    
    total_amount = data.get('total', 0)
    washing_total = data.get('washing_total', 0)
    
    if buyer['wallet_balance'] < total_amount:
        return jsonify({'success': False, 'message': 'رصيد المحفظة غير كافي'})
    
    # Get seller ID from first item
    first_item = data['items'][0]
    product_id = first_item['product_id']
    
    cursor.execute('SELECT seller_id FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    seller_id = product['seller_id']
    
    # Generate order number and sales code
    order_number = generate_order_number()
    sales_code = generate_sales_code()
    
    # Get market and washing station for seller
    cursor.execute('''
        SELECT m.id as market_id, ws.id as washing_station_id
        FROM users u
        LEFT JOIN markets m ON 1=1  # In real app, link seller to market
        LEFT JOIN washing_stations ws ON ws.market_id = m.id
        WHERE u.id = ?
        LIMIT 1
    ''', (seller_id,))
    
    location = cursor.fetchone()
    market_id = location['market_id'] if location else None
    washing_station_id = location['washing_station_id'] if location else None
    
    # Get available driver
    cursor.execute('SELECT id FROM drivers WHERE available = 1 AND active = 1 LIMIT 1')
    driver = cursor.fetchone()
    driver_id = driver['id'] if driver else None
    
    # Create order
    cursor.execute('''
        INSERT INTO orders (
            order_number, buyer_id, seller_id, market_id, washing_station_id, driver_id,
            total_amount, washing_amount, delivery_fee, sales_code, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_number, request.user_id, seller_id, market_id, washing_station_id, driver_id,
        total_amount, washing_total, 15, sales_code, 'confirmed'
    ))
    
    order_id = cursor.lastrowid
    
    # Add order items
    for item in data['items']:
        cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, washing, washing_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            item['product_id'],
            item['quantity'],
            item['price'],
            item.get('washing', False),
            100 if item.get('washing', False) else 0
        ))
        
        # Update product stock
        cursor.execute('UPDATE products SET stock = stock - ? WHERE id = ?', 
                      (item['quantity'], item['product_id']))
    
    # Deduct amount from buyer's wallet
    cursor.execute('UPDATE users SET wallet_balance = wallet_balance - ? WHERE id = ?', 
                  (total_amount, request.user_id))
    
    # Add transaction for buyer
    cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, status, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (request.user_id, 'purchase', total_amount, 'completed', f'طلب #{order_number}'))
    
    # Notifications
    # Notify buyer
    create_notification(
        request.user_id,
        'تم إنشاء طلب جديد',
        f'تم إنشاء طلبك رقم #{order_number} بنجاح',
        'order',
        order_id
    )
    
    # Notify seller
    create_notification(
        seller_id,
        'طلب جديد',
        f'لديك طلب جديد رقم #{order_number}',
        'order',
        order_id
    )
    
    # Notify washing station if applicable
    if washing_station_id and washing_total > 0:
        cursor.execute('SELECT owner_name, phone FROM washing_stations WHERE id = ?', (washing_station_id,))
        washing_station = cursor.fetchone()
        if washing_station:
            create_notification(
                seller_id,  # For now, notify seller about washing
                'طلب غسيل',
                f'طلب غسيل جديد للطلب #{order_number}',
                'order',
                order_id
            )
    
    # Notify driver
    if driver_id:
        create_notification(
            driver_id,
            'طلب توصيل جديد',
            f'طلب توصيل جديد رقم #{order_number}',
            'order',
            order_id
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'تم إنشاء الطلب بنجاح',
        'order': {
            'id': order_id,
            'order_number': order_number,
            'sales_code': sales_code,
            'total': total_amount
        }
    })

# Wallet
@app.route('/api/wallet', methods=['GET'])
@token_required
def get_wallet():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT wallet_balance FROM users WHERE id = ?', (request.user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'balance': user['wallet_balance'] if user else 0
    })

@app.route('/api/wallet/charge', methods=['POST'])
@token_required
def charge_wallet():
    data = request.get_json()
    amount = data.get('amount')
    method = data.get('method')
    
    if not amount or amount < 10:
        return jsonify({'success': False, 'message': 'المبلغ يجب أن يكون 10 ريال على الأقل'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Add transaction
    cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, payment_method, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (request.user_id, 'deposit', amount, method, 'pending', 'شحن رصيد'))
    
    transaction_id = cursor.lastrowid
    
    # In real app, integrate with payment gateway
    # For now, simulate successful payment
    cursor.execute('UPDATE users SET wallet_balance = wallet_balance + ? WHERE id = ?', 
                  (amount, request.user_id))
    
    cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', 
                  ('completed', transaction_id))
    
    # Create notification
    create_notification(
        request.user_id,
        'شحن رصيد',
        f'تم شحن مبلغ {amount} ريال إلى محفظتك',
        'payment',
        transaction_id
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'تم شحن {amount} ريال بنجاح'
    })

@app.route('/api/wallet/withdraw', methods=['POST'])
@token_required
def withdraw_wallet():
    data = request.get_json()
    amount = data.get('amount')
    wallet_type = data.get('wallet_type')
    wallet_number = data.get('wallet_number')
    full_name = data.get('full_name')
    
    if not all([amount, wallet_type, wallet_number, full_name]):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check balance
    cursor.execute('SELECT wallet_balance FROM users WHERE id = ?', (request.user_id,))
    user = cursor.fetchone()
    
    if user['wallet_balance'] < amount:
        return jsonify({'success': False, 'message': 'الرصيد غير كافي'})
    
    # Add withdrawal transaction
    cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, payment_method, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (request.user_id, 'withdraw', amount, wallet_type, 'pending', f'سحب إلى {wallet_type}'))
    
    transaction_id = cursor.lastrowid
    
    # In real app, process withdrawal
    # For now, simulate processing
    cursor.execute('UPDATE users SET wallet_balance = wallet_balance - ? WHERE id = ?', 
                  (amount, request.user_id))
    
    cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', 
                  ('processing', transaction_id))
    
    # Notify admin
    cursor.execute('SELECT id FROM users WHERE user_type = ? LIMIT 1', ('admin',))
    admin = cursor.fetchone()
    if admin:
        create_notification(
            admin['id'],
            'طلب سحب جديد',
            f'طلب سحب جديد بمبلغ {amount} ريال من المستخدم #{request.user_id}',
            'payment',
            transaction_id
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'تم إرسال طلب السحب، سيتم المعالجة خلال 24 ساعة'
    })

# Notifications
@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        LIMIT 50
    ''', (request.user_id,))
    
    notifications = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(notif) for notif in notifications])

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@token_required
def mark_notification_read(notification_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE notifications SET read = 1 
        WHERE id = ? AND user_id = ?
    ''', (notification_id, request.user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Admin Routes

# Markets Management
@app.route('/api/admin/markets', methods=['GET'])
@admin_required
def get_markets():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, 
               (SELECT COUNT(*) FROM washing_stations ws WHERE ws.market_id = m.id) as washing_stations_count
        FROM markets m
        ORDER BY m.created_at DESC
    ''')
    
    markets = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(market) for market in markets])

@app.route('/api/admin/markets', methods=['POST'])
@admin_required
def create_market():
    data = request.get_json()
    
    required_fields = ['name', 'city']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO markets (name, city, address, latitude, longitude, active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['city'],
        data.get('address', ''),
        data.get('latitude'),
        data.get('longitude'),
        data.get('active', True)
    ))
    
    market_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'تم إنشاء السوق بنجاح',
        'market_id': market_id
    })

# Washing Stations Management
@app.route('/api/admin/washing-stations', methods=['GET'])
@admin_required
def get_washing_stations():
    conn = get_db()
    cursor = conn.cursor()
    
    market_id = request.args.get('market_id')
    
    query = '''
        SELECT ws.*, m.name as market_name
        FROM washing_stations ws
        LEFT JOIN markets m ON ws.market_id = m.id
        WHERE 1=1
    '''
    params = []
    
    if market_id:
        query += ' AND ws.market_id = ?'
        params.append(market_id)
    
    query += ' ORDER BY ws.name'
    
    cursor.execute(query, params)
    stations = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(station) for station in stations])

# Drivers Management
@app.route('/api/admin/drivers', methods=['GET'])
@admin_required
def get_drivers():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.*, u.email, u.phone as user_phone
        FROM drivers d
        LEFT JOIN users u ON d.user_id = u.id
        ORDER BY d.name
    ''')
    
    drivers = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(driver) for driver in drivers])

# Users Management
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    conn = get_db()
    cursor = conn.cursor()
    
    user_type = request.args.get('type')
    search = request.args.get('search')
    
    query = 'SELECT * FROM users WHERE 1=1'
    params = []
    
    if user_type:
        query += ' AND user_type = ?'
        params.append(user_type)
    
    if search:
        query += ' AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(user) for user in users])

# Export to Excel
@app.route('/api/admin/export/users', methods=['GET'])
@admin_required
def export_users():
    conn = get_db()
    
    # Get users data
    users_df = pd.read_sql_query('SELECT * FROM users', conn)
    
    # Create Excel file
    filename = f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join(app.config['BACKUP_FOLDER'], filename)
    
    # Ensure backup folder exists
    os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
    
    # Save to Excel
    users_df.to_excel(filepath, index=False)
    
    conn.close()
    
    return send_file(filepath, as_attachment=True)

# Backup Management
@app.route('/api/admin/backup', methods=['POST'])
@admin_required
def create_backup():
    table = request.get_json().get('table', 'all')
    
    conn = get_db()
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    backup_data = {}
    
    if table == 'all':
        for table_name in tables:
            df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
            backup_data[table_name] = df.to_dict('records')
    else:
        if table in tables:
            df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
            backup_data[table] = df.to_dict('records')
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Table not found'})
    
    conn.close()
    
    # Save backup to file
    filename = f'backup_{table}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    filepath = os.path.join(app.config['BACKUP_FOLDER'], filename)
    
    os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        'success': True,
        'message': f'تم إنشاء نسخة احتياطية',
        'filename': filename,
        'filepath': filepath
    })

# Ads Management
@app.route('/api/ads', methods=['GET'])
def get_ads():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get active ads that haven't expired
    cursor.execute('''
        SELECT * FROM ads 
        WHERE active = 1 
        AND (end_date IS NULL OR end_date > datetime('now'))
        ORDER BY created_at DESC
    ''')
    
    ads = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(ad) for ad in ads])

@app.route('/api/admin/ads', methods=['GET'])
@admin_required
def get_admin_ads():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, u.name as creator_name
        FROM ads a
        LEFT JOIN users u ON a.created_by = u.id
        ORDER BY a.created_at DESC
    ''')
    
    ads = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(ad) for ad in ads])

# System Settings
@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM settings')
    settings = cursor.fetchall()
    conn.close()
    
    settings_dict = {setting['key']: setting['value'] for setting in settings}
    
    return jsonify({'success': True, 'settings': settings_dict})

@app.route('/api/admin/settings', methods=['PUT'])
@admin_required
def update_settings():
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'لا توجد بيانات'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    for key, value in data.items():
        cursor.execute('''
            UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE key = ?
        ''', (str(value), key))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم تحديث الإعدادات'})

# Statistics
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    # Total users
    cursor.execute('SELECT COUNT(*) as total FROM users')
    total_users = cursor.fetchone()['total']
    
    # Total orders
    cursor.execute('SELECT COUNT(*) as total FROM orders')
    total_orders = cursor.fetchone()['total']
    
    # Total revenue
    cursor.execute('SELECT SUM(total_amount) as total FROM orders WHERE status = "delivered"')
    total_revenue = cursor.fetchone()['total'] or 0
    
    # Total products
    cursor.execute('SELECT COUNT(*) as total FROM products WHERE active = 1')
    total_products = cursor.fetchone()['total']
    
    # Recent orders
    cursor.execute('''
        SELECT o.*, u.name as buyer_name
        FROM orders o
        JOIN users u ON o.buyer_id = u.id
        ORDER BY o.created_at DESC
        LIMIT 10
    ''')
    recent_orders = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_products': total_products
        },
        'recent_orders': [dict(order) for order in recent_orders]
    })

# File Upload
@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'url': f'/uploads/{filename}'
        })
    
    return jsonify({'success': False, 'message': 'File type not allowed'})

# Serve static files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# Create necessary folders
os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    # Create default admin if not exists
    init_db()
    
    print("Starting Qat App Server...")
    print(f"Database: {app.config['DATABASE']}")
    print("API Endpoints:")
    print("  POST /api/login - User login")
    print("  POST /api/register - User registration")
    print("  GET  /api/products - Get products")
    print("  POST /api/products - Create product (seller)")
    print("  POST /api/orders/create - Create order")
    print("  GET  /api/wallet - Get wallet balance")
    print("  POST /api/wallet/charge - Charge wallet")
    print("  POST /api/wallet/withdraw - Withdraw from wallet")
    print("  GET  /api/notifications - Get notifications")
    print("\nAdmin Endpoints (require admin token):")
    print("  GET  /api/admin/markets - Get markets")
    print("  POST /api/admin/markets - Create market")
    print("  GET  /api/admin/washing-stations - Get washing stations")
    print("  GET  /api/admin/drivers - Get drivers")
    print("  GET  /api/admin/users - Get users")
    print("  GET  /api/admin/export/users - Export users to Excel")
    print("  POST /api/admin/backup - Create backup")
    print("  GET  /api/admin/settings - Get settings")
    print("  PUT  /api/admin/settings - Update settings")
    print("  GET  /api/admin/stats - Get statistics")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
