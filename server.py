import os
import json
import random
import uuid
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import pandas as pd
import numpy as np
import qrcode
from io import BytesIO
import base64
from PIL import Image

# إعداد التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qat_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BACKUP_FOLDER'] = 'backups'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# إنشاء المجلدات
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)

# إعداد CORS و SQLAlchemy
CORS(app)
db = SQLAlchemy(app)

# ==== النماذج (Models) ====

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # admin, seller, buyer, driver
    avatar = db.Column(db.String(200))
    balance = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=5.0)
    total_rating = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verification_code = db.Column(db.String(6))
    
    # العلاقات
    products = db.relationship('Product', backref='seller', lazy=True)
    orders_as_buyer = db.relationship('Order', foreign_keys='Order.buyer_id', backref='buyer', lazy=True)
    orders_as_seller = db.relationship('Order', foreign_keys='Order.seller_id', backref='seller_rel', lazy=True)
    wallet_transactions = db.relationship('WalletTransaction', backref='user', lazy=True)
    ratings_received = db.relationship('Rating', foreign_keys='Rating.seller_id', backref='seller_rated', lazy=True)
    ratings_given = db.relationship('Rating', foreign_keys='Rating.buyer_id', backref='buyer_rating', lazy=True)
    advertisements = db.relationship('Advertisement', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        payload = {
            'user_id': self.id,
            'user_type': self.user_type,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'avatar': self.avatar,
            'balance': self.balance,
            'rating': self.rating,
            'total_rating': self.total_rating,
            'created_at': self.created_at.isoformat()
        }

class Market(db.Model):
    __tablename__ = 'markets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    qat_wash_centers = db.relationship('QatWashCenter', backref='market', lazy=True)
    drivers = db.relationship('DriverAssignment', backref='market', lazy=True)
    sellers = db.relationship('SellerMarket', backref='market', lazy=True)

class QatWashCenter(db.Model):
    __tablename__ = 'qat_wash_centers'
    
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    operator_name = db.Column(db.String(100))
    wash_price = db.Column(db.Float, default=100.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_number = db.Column(db.String(50))
    license_number = db.Column(db.String(100))
    rating = db.Column(db.Float, default=5.0)
    total_deliveries = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    current_location = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='driver_profile', lazy=True)
    assignments = db.relationship('DriverAssignment', backref='driver', lazy=True)
    deliveries = db.relationship('Order', backref='delivery_driver', lazy=True)

class DriverAssignment(db.Model):
    __tablename__ = 'driver_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    assignment_date = db.Column(db.Date, nullable=False)
    shift_start = db.Column(db.Time, nullable=False)
    shift_end = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SellerMarket(db.Model):
    __tablename__ = 'seller_markets'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    stall_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    seller = db.relationship('User', backref='market_assignments', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # صعدي، همداني، أرحبى، إلخ
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='كيلو')
    images = db.Column(db.Text)  # JSON array of image URLs
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_wash_available = db.Column(db.Boolean, default=True)
    wash_price = db.Column(db.Float, default=100.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    ratings = db.relationship('ProductRating', backref='product', lazy=True)

class ProductRating(db.Model):
    __tablename__ = 'product_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    buyer = db.relationship('User', backref='product_ratings_given', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    qat_wash_center_id = db.Column(db.Integer, db.ForeignKey('qat_wash_centers.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    
    total_amount = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0)
    wash_fee = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    
    payment_method = db.Column(db.String(50), nullable=False)  # wallet, jib, jawaly, etc.
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    payment_transaction_id = db.Column(db.String(100))
    
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, preparing, washing, ready_for_delivery, on_the_way, delivered, cancelled
    washing_code = db.Column(db.String(50))  # رمز المغسلة
    qr_code = db.Column(db.Text)  # QR code image base64
    
    seller_notified = db.Column(db.Boolean, default=False)
    wash_center_notified = db.Column(db.Boolean, default=False)
    driver_notified = db.Column(db.Boolean, default=False)
    buyer_notified = db.Column(db.Boolean, default=False)
    
    estimated_delivery_time = db.Column(db.DateTime)
    actual_delivery_time = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    market = db.relationship('Market', backref='orders', lazy=True)
    qat_wash_center = db.relationship('QatWashCenter', backref='orders', lazy=True)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    notifications = db.relationship('Notification', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    requires_washing = db.Column(db.Boolean, default=False)
    wash_price = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # deposit, withdraw, purchase, sale, refund
    amount = db.Column(db.Float, nullable=False)
    wallet_type = db.Column(db.String(50))  # jib, jawaly, mobicash, shamel, falousk, internal
    phone_number = db.Column(db.String(20))
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    notes = db.Column(db.Text)
    receipt_image = db.Column(db.String(200))
    admin_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    admin = db.relationship('User', foreign_keys=[approved_by], backref='approved_transactions', lazy=True)

class Advertisement(db.Model):
    __tablename__ = 'advertisements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    target_url = db.Column(db.String(500))
    ad_type = db.Column(db.String(50), nullable=False)  # banner, popup, interstitial
    position = db.Column(db.String(50))  # home_top, home_middle, etc.
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, default=0.0)
    spent = db.Column(db.Float, default=0.0)
    clicks = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdPackage(db.Model):
    __tablename__ = 'ad_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    max_impressions = db.Column(db.Integer)
    max_clicks = db.Column(db.Integer)
    features = db.Column(db.Text)  # JSON array of features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # order, payment, system, ad
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications', lazy=True)

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GiftCode(db.Model):
    __tablename__ = 'gift_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_gift_codes', lazy=True)
    user = db.relationship('User', foreign_keys=[used_by], backref='used_gift_codes', lazy=True)

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==== مصادقة التوكن (Token Authentication) ====

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] if " " in request.headers['Authorization'] else None
        
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type != 'admin':
            return jsonify({'error': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def seller_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type not in ['admin', 'seller']:
            return jsonify({'error': 'Seller access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# ==== مسارات API ====

@app.route('/')
def index():
    return jsonify({
        'message': 'Qat Application API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/*',
            'users': '/api/users/*',
            'products': '/api/products/*',
            'orders': '/api/orders/*',
            'admin': '/api/admin/*'
        }
    })

# ==== المصادقة ====

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # التحقق من البيانات
        required_fields = ['name', 'email', 'phone', 'password', 'user_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # التحقق من وجود المستخدم
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({'error': 'Phone number already exists'}), 400
        
        # إنشاء المستخدم
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            user_type=data['user_type']
        )
        user.set_password(data['password'])
        
        # إعدادات إضافية حسب نوع المستخدم
        if data['user_type'] == 'seller':
            user.balance = 0.0
        elif data['user_type'] == 'buyer':
            user.balance = 0.0
        
        db.session.add(user)
        db.session.commit()
        
        # إنشاء التوكن
        token = user.generate_token()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        token = user.generate_token()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

# ==== المنتجات ====

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category')
        seller_id = request.args.get('seller_id')
        search = request.args.get('search')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        
        query = Product.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        if seller_id:
            query = query.filter_by(seller_id=seller_id)
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        if min_price:
            query = query.filter(Product.price >= float(min_price))
        if max_price:
            query = query.filter(Product.price <= float(max_price))
        
        products = query.all()
        
        return jsonify({
            'success': True,
            'products': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'category': p.category,
                'price': p.price,
                'quantity': p.quantity,
                'unit': p.unit,
                'images': json.loads(p.images) if p.images else [],
                'rating': p.rating,
                'total_ratings': p.total_ratings,
                'is_wash_available': p.is_wash_available,
                'wash_price': p.wash_price,
                'seller': p.seller.to_dict() if p.seller else None,
                'created_at': p.created_at.isoformat()
            } for p in products]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
@token_required
@seller_required
def create_product(current_user):
    try:
        data = request.json
        
        required_fields = ['name', 'category', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        product = Product(
            seller_id=current_user.id,
            name=data['name'],
            description=data.get('description', ''),
            category=data['category'],
            price=float(data['price']),
            quantity=data.get('quantity', 0),
            unit=data.get('unit', 'كيلو'),
            images=json.dumps(data.get('images', [])),
            is_wash_available=data.get('is_wash_available', True),
            wash_price=data.get('wash_price', 100.0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@token_required
@seller_required
def update_product(current_user, product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        # التحقق من ملكية المنتج
        if product.seller_id != current_user.id and current_user.user_type != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'category' in data:
            product.category = data['category']
        if 'price' in data:
            product.price = float(data['price'])
        if 'quantity' in data:
            product.quantity = data['quantity']
        if 'images' in data:
            product.images = json.dumps(data['images'])
        if 'is_wash_available' in data:
            product.is_wash_available = data['is_wash_available']
        if 'wash_price' in data:
            product.wash_price = float(data['wash_price'])
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==== الطلبات ====

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    try:
        if current_user.user_type != 'buyer':
            return jsonify({'error': 'Only buyers can create orders'}), 403
        
        data = request.json
        
        required_fields = ['items', 'delivery_address', 'payment_method', 'market_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # التحقق من المنتجات والمخزون
        items = data['items']
        if not items:
            return jsonify({'error': 'Order must contain at least one item'}), 400
        
        order_items = []
        total_amount = 0.0
        wash_fee = 0.0
        seller_id = None
        
        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'error': f"Product {item['product_id']} not found"}), 404
            
            if product.quantity < item.get('quantity', 1):
                return jsonify({'error': f"Insufficient stock for {product.name}"}), 400
            
            # تحديد البائع (يجب أن تكون جميع المنتجات لنفس البائع)
            if seller_id is None:
                seller_id = product.seller_id
            elif seller_id != product.seller_id:
                return jsonify({'error': 'All products must be from the same seller'}), 400
            
            # حساب السعر
            quantity = item.get('quantity', 1)
            item_total = product.price * quantity
            
            # إضافة رسوم الغسيل إذا طلب
            requires_washing = item.get('requires_washing', False)
            item_wash_fee = 0.0
            if requires_washing and product.is_wash_available:
                item_wash_fee = product.wash_price * quantity
                wash_fee += item_wash_fee
            
            total_amount += item_total
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': product.price,
                'total_price': item_total,
                'requires_washing': requires_washing,
                'wash_price': item_wash_fee
            })
        
        # حساب المبلغ النهائي
        delivery_fee = 15.0  # رسوم التوصيل الثابتة
        final_amount = total_amount + wash_fee + delivery_fee
        
        # التحقق من رصيد المشتري إذا كانت طريقة الدفع بالرصيد
        if data['payment_method'] == 'wallet' and current_user.balance < final_amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # إنشاء رقم الطلب
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # تحديد مغسلة القات في السوق
        market = Market.query.get(data['market_id'])
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        qat_wash_center = QatWashCenter.query.filter_by(
            market_id=market.id,
            is_active=True
        ).first()
        
        if not qat_wash_center:
            return jsonify({'error': 'No wash center available in this market'}), 400
        
        # إنشاء الطلب
        order = Order(
            order_number=order_number,
            buyer_id=current_user.id,
            seller_id=seller_id,
            market_id=market.id,
            qat_wash_center_id=qat_wash_center.id,
            total_amount=total_amount,
            delivery_fee=delivery_fee,
            wash_fee=wash_fee,
            final_amount=final_amount,
            payment_method=data['payment_method'],
            delivery_address=data['delivery_address'],
            estimated_delivery_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        # إنشاء رمز الغسيل
        washing_code = f"WASH-{random.randint(1000, 9999)}"
        order.washing_code = washing_code
        
        # إنشاء QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_data = f"Order: {order_number}\nWash Code: {washing_code}\nTotal: {final_amount} SAR"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
        order.qr_code = qr_code_base64
        
        db.session.add(order)
        db.session.flush()  # للحصول على order.id
        
        # إضافة عناصر الطلب
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                requires_washing=item_data['requires_washing'],
                wash_price=item_data['wash_price']
            )
            db.session.add(order_item)
            
            # تحديث مخزون المنتج
            item_data['product'].quantity -= item_data['quantity']
        
        # معالجة الدفع
        if data['payment_method'] == 'wallet':
            # خصم من رصيد المشتري
            current_user.balance -= final_amount
            
            # إضافة للمحفظة
            wallet_transaction = WalletTransaction(
                user_id=current_user.id,
                transaction_type='purchase',
                amount=-final_amount,
                wallet_type='internal',
                transaction_id=f"TXN-{order_number}",
                status='completed',
                notes=f"Payment for order {order_number}"
            )
            db.session.add(wallet_transaction)
            
            order.payment_status = 'completed'
        
        # إنشاء الإشعارات
        notifications = []
        
        # إشعار للبائع
        seller_notification = Notification(
            user_id=seller_id,
            order_id=order.id,
            title="طلب جديد",
            message=f"لديك طلب جديد #{order_number} بقيمة {final_amount} ريال",
            notification_type='order'
        )
        notifications.append(seller_notification)
        order.seller_notified = True
        
        # إشعار لمغسلة القات
        wash_operator = User.query.filter_by(phone=qat_wash_center.phone).first()
        if wash_operator:
            wash_notification = Notification(
                user_id=wash_operator.id,
                order_id=order.id,
                title="طلب غسيل جديد",
                message=f"طلب غسيل جديد #{order_number} - الرمز: {washing_code}",
                notification_type='order'
            )
            notifications.append(wash_notification)
            order.wash_center_notified = True
        
        # إشعار للمشتري
        buyer_notification = Notification(
            user_id=current_user.id,
            order_id=order.id,
            title="تم إنشاء طلبك",
            message=f"تم إنشاء طلبك #{order_number} بنجاح. الرمز: {washing_code}",
            notification_type='order'
        )
        notifications.append(buyer_notification)
        order.buyer_notified = True
        
        # إضافة جميع الإشعارات
        for notification in notifications:
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'total_amount': order.final_amount,
                'washing_code': order.washing_code,
                'qr_code': order.qr_code,
                'estimated_delivery': order.estimated_delivery_time.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/my', methods=['GET'])
@token_required
def get_my_orders(current_user):
    try:
        status = request.args.get('status')
        
        if current_user.user_type == 'buyer':
            query = Order.query.filter_by(buyer_id=current_user.id)
        elif current_user.user_type == 'seller':
            query = Order.query.filter_by(seller_id=current_user.id)
        else:
            query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'orders': [{
                'id': o.id,
                'order_number': o.order_number,
                'total_amount': o.final_amount,
                'status': o.status,
                'payment_status': o.payment_status,
                'created_at': o.created_at.isoformat(),
                'estimated_delivery': o.estimated_delivery_time.isoformat() if o.estimated_delivery_time else None
            } for o in orders]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==== المحفظة ====

@app.route('/api/wallet/balance', methods=['GET'])
@token_required
def get_wallet_balance(current_user):
    return jsonify({
        'success': True,
        'balance': current_user.balance
    })

@app.route('/api/wallet/deposit', methods=['POST'])
@token_required
def deposit_to_wallet(current_user):
    try:
        data = request.json
        
        required_fields = ['amount', 'wallet_type', 'phone_number']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # إنشاء معاملة إيداع
        transaction = WalletTransaction(
            user_id=current_user.id,
            transaction_type='deposit',
            amount=amount,
            wallet_type=data['wallet_type'],
            phone_number=data['phone_number'],
            transaction_id=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            status='pending',
            notes=data.get('notes', '')
        )
        
        # إضافة صورة الإيصال إذا وجدت
        if 'receipt_image' in data:
            transaction.receipt_image = data['receipt_image']
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deposit request submitted successfully',
            'transaction_id': transaction.transaction_id,
            'instructions': {
                'deposit_number': '771831482',
                'account_name': 'يوسف محمد علي حمود زهير',
                'phone': '771831482'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet/withdraw', methods=['POST'])
@token_required
def withdraw_from_wallet(current_user):
    try:
        data = request.json
        
        required_fields = ['amount', 'wallet_type', 'phone_number', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        if current_user.balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # إنشاء معاملة سحب
        transaction = WalletTransaction(
            user_id=current_user.id,
            transaction_type='withdraw',
            amount=-amount,
            wallet_type=data['wallet_type'],
            phone_number=data['phone_number'],
            transaction_id=f"WTH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            status='pending',
            notes=f"Withdraw to {data['full_name']} - {data['wallet_type']}"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Withdrawal request submitted successfully',
            'transaction_id': transaction.transaction_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet/transactions', methods=['GET'])
@token_required
def get_wallet_transactions(current_user):
    try:
        transactions = WalletTransaction.query.filter_by(
            user_id=current_user.id
        ).order_by(WalletTransaction.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'transactions': [{
                'id': t.id,
                'type': t.transaction_type,
                'amount': t.amount,
                'wallet_type': t.wallet_type,
                'status': t.status,
                'notes': t.notes,
                'created_at': t.created_at.isoformat(),
                'approved': t.admin_approved
            } for t in transactions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet/redeem-gift', methods=['POST'])
@token_required
def redeem_gift_code(current_user):
    try:
        data = request.json
        
        if 'code' not in data:
            return jsonify({'error': 'Gift code is required'}), 400
        
        gift_code = GiftCode.query.filter_by(
            code=data['code'],
            is_used=False
        ).first()
        
        if not gift_code:
            return jsonify({'error': 'Invalid or expired gift code'}), 404
        
        if gift_code.expires_at and gift_code.expires_at < datetime.utcnow():
            return jsonify({'error': 'Gift code has expired'}), 400
        
        # استخدام الكود
        gift_code.is_used = True
        gift_code.used_by = current_user.id
        gift_code.used_at = datetime.utcnow()
        
        # إضافة الرصيد للمستخدم
        current_user.balance += gift_code.amount
        
        # إنشاء معاملة
        transaction = WalletTransaction(
            user_id=current_user.id,
            transaction_type='deposit',
            amount=gift_code.amount,
            wallet_type='gift_code',
            transaction_id=f"GIFT-{gift_code.code}",
            status='completed',
            notes=f"Redeemed gift code: {gift_code.code}"
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Gift code redeemed successfully! {gift_code.amount} SAR added to your balance',
            'amount': gift_code.amount
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==== الإشعارات ====

@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'order_id': n.order_id
            } for n in notifications]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_notification_read(current_user, notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Notification marked as read'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==== التقييمات ====

@app.route('/api/ratings', methods=['POST'])
@token_required
def create_rating(current_user):
    try:
        if current_user.user_type != 'buyer':
            return jsonify({'error': 'Only buyers can rate sellers'}), 403
        
        data = request.json
        
        required_fields = ['seller_id', 'order_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # التحقق من أن الطلب مكتمل وينتمي للمشتري
        order = Order.query.get(data['order_id'])
        if not order or order.buyer_id != current_user.id:
            return jsonify({'error': 'Invalid order'}), 404
        
        if order.seller_id != data['seller_id']:
            return jsonify({'error': 'Seller does not match order'}), 400
        
        # التحقق من عدم وجود تقييم سابق
        existing_rating = Rating.query.filter_by(
            buyer_id=current_user.id,
            order_id=data['order_id']
        ).first()
        
        if existing_rating:
            return jsonify({'error': 'You have already rated this order'}), 400
        
        # إنشاء التقييم
        rating = Rating(
            buyer_id=current_user.id,
            seller_id=data['seller_id'],
            order_id=data['order_id'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        # تحديث تقييم البائع
        seller = User.query.get(data['seller_id'])
        if seller:
            total_ratings = seller.total_rating + 1
            total_score = (seller.rating * seller.total_rating) + data['rating']
            seller.rating = total_score / total_ratings
            seller.total_rating = total_ratings
        
        db.session.add(rating)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully',
            'rating': {
                'id': rating.id,
                'rating': rating.rating,
                'comment': rating.comment
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==== الإعلانات ====

@app.route('/api/advertisements', methods=['GET'])
def get_advertisements():
    try:
        ad_type = request.args.get('type')
        position = request.args.get('position')
        
        query = Advertisement.query.filter_by(
            is_active=True
        ).filter(
            Advertisement.start_date <= datetime.utcnow(),
            Advertisement.end_date >= datetime.utcnow()
        )
        
        if ad_type:
            query = query.filter_by(ad_type=ad_type)
        if position:
            query = query.filter_by(position=position)
        
        advertisements = query.all()
        
        # زيادة عدد المشاهدات
        for ad in advertisements:
            ad.impressions += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'advertisements': [{
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'image_url': ad.image_url,
                'target_url': ad.target_url,
                'type': ad.ad_type,
                'position': ad.position
            } for ad in advertisements]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/advertisements/<int:ad_id>/click', methods=['POST'])
def track_ad_click(ad_id):
    try:
        ad = Advertisement.query.get(ad_id)
        if ad:
            ad.clicks += 1
            db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==== الإدارة (Admin Only) ====

@app.route('/api/admin/dashboard', methods=['GET'])
@token_required
@admin_required
def admin_dashboard(current_user):
    try:
        # الإحصائيات
        total_users = User.query.count()
        total_buyers = User.query.filter_by(user_type='buyer').count()
        total_sellers = User.query.filter_by(user_type='seller').count()
        total_drivers = User.query.filter_by(user_type='driver').count()
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(func.sum(Order.final_amount)).scalar() or 0
        
        # الطلبات حسب الحالة
        orders_by_status = db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        # المنتجات الأكثر مبيعاً
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem, Product.id == OrderItem.product_id
        ).group_by(Product.id
        ).order_by(func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        # البائعين الأعلى تقييماً
        top_sellers = db.session.query(
            User.name,
            User.rating,
            func.count(Order.id).label('total_orders')
        ).join(Order, User.id == Order.seller_id
        ).group_by(User.id
        ).order_by(User.rating.desc()
        ).limit(10).all()
        
        # التحويلات المعلقة
        pending_transactions = WalletTransaction.query.filter_by(
            status='pending'
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_buyers': total_buyers,
                'total_sellers': total_sellers,
                'total_drivers': total_drivers,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'pending_transactions': pending_transactions
            },
            'orders_by_status': dict(orders_by_status),
            'top_products': [{'name': p[0], 'sold': p[1]} for p in top_products],
            'top_sellers': [{'name': s[0], 'rating': s[1], 'orders': s[2]} for s in top_sellers]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def admin_get_users(current_user):
    try:
        user_type = request.args.get('type')
        search = request.args.get('search')
        
        query = User.query
        
        if user_type:
            query = query.filter_by(user_type=user_type)
        if search:
            query = query.filter(
                (User.name.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.phone.ilike(f'%{search}%'))
            )
        
        users = query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def admin_update_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'balance' in data:
            user.balance = float(data['balance'])
        if 'user_type' in data:
            user.user_type = data['user_type']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/markets', methods=['GET'])
@token_required
@admin_required
def admin_get_markets(current_user):
    try:
        markets = Market.query.all()
        
        return jsonify({
            'success': True,
            'markets': [{
                'id': m.id,
                'name': m.name,
                'location': m.location,
                'city': m.city,
                'is_active': m.is_active,
                'wash_centers': len(m.qat_wash_centers),
                'sellers': len(m.sellers)
            } for m in markets]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/markets', methods=['POST'])
@token_required
@admin_required
def admin_create_market(current_user):
    try:
        data = request.json
        
        required_fields = ['name', 'location', 'city']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        market = Market(
            name=data['name'],
            location=data['location'],
            city=data['city'],
            lat=data.get('lat'),
            lng=data.get('lng')
        )
        
        db.session.add(market)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Market created successfully',
            'market': {
                'id': market.id,
                'name': market.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/qat-wash-centers', methods=['GET'])
@token_required
@admin_required
def admin_get_wash_centers(current_user):
    try:
        market_id = request.args.get('market_id')
        
        query = QatWashCenter.query
        
        if market_id:
            query = query.filter_by(market_id=market_id)
        
        centers = query.all()
        
        return jsonify({
            'success': True,
            'wash_centers': [{
                'id': wc.id,
                'name': wc.name,
                'phone': wc.phone,
                'market': wc.market.name if wc.market else None,
                'wash_price': wc.wash_price,
                'is_active': wc.is_active
            } for wc in centers]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/qat-wash-centers', methods=['POST'])
@token_required
@admin_required
def admin_create_wash_center(current_user):
    try:
        data = request.json
        
        required_fields = ['name', 'phone', 'market_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        center = QatWashCenter(
            name=data['name'],
            phone=data['phone'],
            market_id=data['market_id'],
            operator_name=data.get('operator_name'),
            wash_price=data.get('wash_price', 100.0)
        )
        
        db.session.add(center)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Wash center created successfully',
            'center': {
                'id': center.id,
                'name': center.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/drivers', methods=['GET'])
@token_required
@admin_required
def admin_get_drivers(current_user):
    try:
        drivers = Driver.query.all()
        
        return jsonify({
            'success': True,
            'drivers': [{
                'id': d.id,
                'name': d.user.name,
                'phone': d.user.phone,
                'vehicle_type': d.vehicle_type,
                'vehicle_number': d.vehicle_number,
                'rating': d.rating,
                'total_deliveries': d.total_deliveries,
                'is_available': d.is_available
            } for d in drivers]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/drivers', methods=['POST'])
@token_required
@admin_required
def admin_create_driver(current_user):
    try:
        data = request.json
        
        required_fields = ['user_id', 'vehicle_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # التحقق من أن المستخدم موجود ونوعه driver
        user = User.query.get(data['user_id'])
        if not user or user.user_type != 'driver':
            return jsonify({'error': 'User must be of type driver'}), 400
        
        driver = Driver(
            user_id=data['user_id'],
            vehicle_type=data['vehicle_type'],
            vehicle_number=data.get('vehicle_number'),
            license_number=data.get('license_number')
        )
        
        db.session.add(driver)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver created successfully',
            'driver': {
                'id': driver.id,
                'name': user.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/driver-assignments', methods=['POST'])
@token_required
@admin_required
def admin_assign_driver(current_user):
    try:
        data = request.json
        
        required_fields = ['driver_id', 'market_id', 'assignment_date', 'shift_start', 'shift_end']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        assignment = DriverAssignment(
            driver_id=data['driver_id'],
            market_id=data['market_id'],
            assignment_date=datetime.strptime(data['assignment_date'], '%Y-%m-%d').date(),
            shift_start=datetime.strptime(data['shift_start'], '%H:%M').time(),
            shift_end=datetime.strptime(data['shift_end'], '%H:%M').time()
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver assigned successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/transactions', methods=['GET'])
@token_required
@admin_required
def admin_get_transactions(current_user):
    try:
        status = request.args.get('status')
        transaction_type = request.args.get('type')
        
        query = WalletTransaction.query
        
        if status:
            query = query.filter_by(status=status)
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        transactions = query.order_by(WalletTransaction.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'transactions': [{
                'id': t.id,
                'user': t.user.name if t.user else 'Unknown',
                'type': t.transaction_type,
                'amount': t.amount,
                'wallet_type': t.wallet_type,
                'phone': t.phone_number,
                'status': t.status,
                'notes': t.notes,
                'receipt_image': t.receipt_image,
                'approved': t.admin_approved,
                'created_at': t.created_at.isoformat()
            } for t in transactions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/transactions/<int:transaction_id>/approve', methods=['PUT'])
@token_required
@admin_required
def admin_approve_transaction(current_user, transaction_id):
    try:
        transaction = WalletTransaction.query.get_or_404(transaction_id)
        
        if transaction.status != 'pending':
            return jsonify({'error': 'Transaction is not pending'}), 400
        
        # إذا كانت معاملة إيداع، إضافة الرصيد للمستخدم
        if transaction.transaction_type == 'deposit':
            transaction.user.balance += transaction.amount
        
        # إذا كانت معاملة سحب، التحقق من الرصيد ثم الخصم
        elif transaction.transaction_type == 'withdraw':
            if transaction.user.balance < abs(transaction.amount):
                return jsonify({'error': 'User has insufficient balance'}), 400
            transaction.user.balance += transaction.amount  # المبلغ سالب
        
        transaction.status = 'completed'
        transaction.admin_approved = True
        transaction.approved_by = current_user.id
        transaction.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        # إرسال إشعار للمستخدم
        notification = Notification(
            user_id=transaction.user_id,
            title="تمت الموافقة على معاملتك",
            message=f"تمت الموافقة على معاملتك #{transaction.transaction_id}",
            notification_type='payment'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction approved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/transactions/<int:transaction_id>/reject', methods=['PUT'])
@token_required
@admin_required
def admin_reject_transaction(current_user, transaction_id):
    try:
        transaction = WalletTransaction.query.get_or_404(transaction_id)
        
        if transaction.status != 'pending':
            return jsonify({'error': 'Transaction is not pending'}), 400
        
        transaction.status = 'failed'
        transaction.admin_approved = False
        transaction.approved_by = current_user.id
        transaction.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        # إرسال إشعار للمستخدم
        notification = Notification(
            user_id=transaction.user_id,
            title="تم رفض معاملتك",
            message=f"تم رفض معاملتك #{transaction.transaction_id}",
            notification_type='payment'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction rejected'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/ad-packages', methods=['GET'])
@token_required
@admin_required
def admin_get_ad_packages(current_user):
    try:
        packages = AdPackage.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'packages': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'duration_days': p.duration_days,
                'max_impressions': p.max_impressions,
                'max_clicks': p.max_clicks,
                'features': json.loads(p.features) if p.features else []
            } for p in packages]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/ad-packages', methods=['POST'])
@token_required
@admin_required
def admin_create_ad_package(current_user):
    try:
        data = request.json
        
        required_fields = ['name', 'price', 'duration_days']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        package = AdPackage(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            duration_days=data['duration_days'],
            max_impressions=data.get('max_impressions'),
            max_clicks=data.get('max_clicks'),
            features=json.dumps(data.get('features', []))
        )
        
        db.session.add(package)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Ad package created successfully',
            'package': {
                'id': package.id,
                'name': package.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/gift-codes', methods=['POST'])
@token_required
@admin_required
def admin_create_gift_code(current_user):
    try:
        data = request.json
        
        required_fields = ['amount', 'expires_at']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # إنشاء كود فريد
        code = f"GIFT-{random.randint(100000, 999999)}"
        while GiftCode.query.filter_by(code=code).first():
            code = f"GIFT-{random.randint(100000, 999999)}"
        
        gift_code = GiftCode(
            code=code,
            amount=float(data['amount']),
            created_by=current_user.id,
            expires_at=datetime.strptime(data['expires_at'], '%Y-%m-%d')
        )
        
        db.session.add(gift_code)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Gift code created successfully',
            'code': code,
            'amount': gift_code.amount,
            'expires_at': gift_code.expires_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/backup', methods=['POST'])
@token_required
@admin_required
def admin_backup_database(current_user):
    try:
        # تصدير جميع الجداول إلى JSON
        backup_data = {}
        
        # المستخدمين
        users = User.query.all()
        backup_data['users'] = [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'phone': u.phone,
            'user_type': u.user_type,
            'balance': u.balance,
            'created_at': u.created_at.isoformat()
        } for u in users]
        
        # المنتجات
        products = Product.query.all()
        backup_data['products'] = [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'quantity': p.quantity,
            'seller_id': p.seller_id,
            'created_at': p.created_at.isoformat()
        } for p in products]
        
        # الطلبات
        orders = Order.query.all()
        backup_data['orders'] = [{
            'id': o.id,
            'order_number': o.order_number,
            'total_amount': o.final_amount,
            'status': o.status,
            'created_at': o.created_at.isoformat()
        } for o in orders]
        
        # المعاملات
        transactions = WalletTransaction.query.all()
        backup_data['transactions'] = [{
            'id': t.id,
            'user_id': t.user_id,
            'amount': t.amount,
            'type': t.transaction_type,
            'status': t.status,
            'created_at': t.created_at.isoformat()
        } for t in transactions]
        
        # حفظ النسخة الاحتياطية
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(app.config['BACKUP_FOLDER'], backup_filename)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'filename': backup_filename,
            'path': backup_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/system-settings', methods=['GET'])
@token_required
@admin_required
def admin_get_system_settings(current_user):
    try:
        settings = SystemSetting.query.all()
        
        return jsonify({
            'success': True,
            'settings': {s.key: s.value for s in settings}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/system-settings', methods=['POST'])
@token_required
@admin_required
def admin_update_system_settings(current_user):
    try:
        data = request.json
        
        for key, value in data.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = SystemSetting(key=key, value=str(value))
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'System settings updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==== مسار التحميل ====

@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # التحقق من نوع الملف
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'File type not allowed'}), 400
        
        # إنشاء اسم فريد للملف
        filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # حفظ الملف
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f"/uploads/{filename}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==== تهيئة قاعدة البيانات ====

def init_database():
    with app.app_context():
        db.create_all()
        
        # إنشاء مدير افتراضي إذا لم يكن موجود
        admin = User.query.filter_by(email='admin@qat.com').first()
        if not admin:
            admin = User(
                name='مدير النظام',
                email='admin@qat.com',
                phone='771000000',
                user_type='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # إنشاء إعدادات افتراضية
        default_settings = [
            ('app_name', 'تطبيق قات'),
            ('delivery_fee', '15'),
            ('min_order_amount', '50'),
            ('max_wash_price', '100'),
            ('support_phone', '771831482'),
            ('support_email', 'support@qat.com'),
            ('deposit_instructions', 'قم بالإيداع على الرقم 771831482 - يوسف محمد علي حمود زهير')
        ]
        
        for key, value in default_settings:
            if not SystemSetting.query.filter_by(key=key).first():
                setting = SystemSetting(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        print("Database initialized successfully!")

# ==== تشغيل التطبيق ====

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)
