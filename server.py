from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import json
import os
import csv
import pandas as pd
from io import BytesIO
import secrets
import hashlib
import jwt
from functools import wraps
import logging

# Configuration
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qat_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(200), nullable=False)
    user_type = Column(String(20), nullable=False)  # admin, seller, buyer, driver, washer
    balance = Column(Float, default=0.0)
    store_name = Column(String(100))
    vehicle_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')
    
    # Relationships
    products = relationship('Product', backref='seller', lazy=True)
    orders_as_buyer = relationship('Order', foreign_keys='Order.buyer_id', backref='buyer', lazy=True)
    orders_as_seller = relationship('Order', foreign_keys='Order.seller_id', backref='seller', lazy=True)
    advertisements = relationship('Advertisement', backref='user', lazy=True)
    withdrawals = relationship('Withdrawal', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'balance': self.balance,
            'store_name': self.store_name,
            'vehicle_type': self.vehicle_type,
            'created_at': self.created_at.isoformat()
        }

class Market(db.Model):
    __tablename__ = 'markets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    address = Column(Text)
    phone = Column(String(20))
    manager_name = Column(String(100))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    washers = relationship('Washer', backref='market', lazy=True)
    products = relationship('Product', backref='market', lazy=True)

class Washer(db.Model):
    __tablename__ = 'washers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    washing_price = Column(Float, default=100.0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    vehicle_type = Column(String(50))
    vehicle_number = Column(String(50))
    status = Column(String(20), default='available')  # available, busy, offline
    rating = Column(Float, default=5.0)
    completed_orders = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship('Order', backref='driver', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'))
    stock = Column(Integer, default=0)
    has_washing = Column(Boolean, default=True)
    washing_price = Column(Float, default=100.0)
    images = Column(Text)  # JSON array of image URLs
    rating = Column(Float, default=5.0)
    total_ratings = Column(Integer, default=0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = relationship('OrderItem', backref='product', lazy=True)
    reviews = relationship('Review', backref='product', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_code = Column(String(50), unique=True, nullable=False)
    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    washer_id = Column(Integer, ForeignKey('washers.id'))
    
    subtotal = Column(Float, nullable=False)
    washing_price = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    
    delivery_address = Column(Text, nullable=False)
    delivery_notes = Column(Text)
    
    payment_method = Column(String(50))
    payment_status = Column(String(20), default='pending')  # pending, paid, failed
    payment_reference = Column(String(100))
    
    order_status = Column(String(20), default='pending')  # pending, confirmed, washing, delivering, delivered, cancelled
    
    washing_required = Column(Boolean, default=False)
    washing_status = Column(String(20), default='pending')  # pending, washing, completed
    
    estimated_delivery = Column(DateTime)
    delivered_at = Column(DateTime)
    
    seller_notified = Column(Boolean, default=False)
    washer_notified = Column(Boolean, default=False)
    driver_notified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship('OrderItem', backref='order', lazy=True)
    notifications = relationship('Notification', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    washing = Column(Boolean, default=False)
    washing_price = Column(Float, default=0.0)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Advertisement(db.Model):
    __tablename__ = 'advertisements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    package_id = Column(Integer, ForeignKey('advertisement_packages.id'))
    title = Column(String(200), nullable=False)
    content = Column(Text)
    image_url = Column(String(500))
    type = Column(String(50))  # home, banner, sidebar, popup
    position = Column(Integer, default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

class AdvertisementPackage(db.Model):
    __tablename__ = 'advertisement_packages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    features = Column(Text)  # JSON array of features
    max_ads = Column(Integer, default=1)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))  # order, payment, system, promotion
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(20), nullable=False)  # deposit, withdrawal, purchase, sale, refund
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    reference = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)

class Withdrawal(db.Model):
    __tablename__ = 'withdrawals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    wallet_type = Column(String(50))  # jib, jawaly, mobile_money, etc.
    wallet_number = Column(String(50))
    wallet_name = Column(String(100))
    status = Column(String(20), default='pending')  # pending, approved, rejected, completed
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

class GiftCode(db.Model):
    __tablename__ = 'gift_codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    used_by = Column(Integer, ForeignKey('users.id'))
    used_at = Column(DateTime)
    expiry_date = Column(DateTime)
    status = Column(String(20), default='active')  # active, used, expired
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Auth decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def seller_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type != 'seller':
            return jsonify({'message': 'Seller access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/')
def index():
    return jsonify({'message': 'Qat App API', 'version': '1.0.0'})

# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists!'}), 400
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        user_type=data.get('user_type', 'buyer')
    )
    
    if 'store_name' in data:
        user.store_name = data['store_name']
    
    if 'vehicle_type' in data:
        user.vehicle_type = data['vehicle_type']
    
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'message': 'User created successfully!',
        'token': token,
        'user': user.to_dict()
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    # Create token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'message': 'Login successful!',
        'token': token,
        'user': user.to_dict()
    })

# Products routes
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    seller_id = request.args.get('seller_id')
    market_id = request.args.get('market_id')
    
    query = Product.query.filter_by(status='active')
    
    if category:
        query = query.filter_by(category=category)
    
    if seller_id:
        query = query.filter_by(seller_id=seller_id)
    
    if market_id:
        query = query.filter_by(market_id=market_id)
    
    products = query.all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'category': p.category,
        'seller': p.seller.to_dict(),
        'market': p.market.to_dict() if p.market else None,
        'stock': p.stock,
        'has_washing': p.has_washing,
        'washing_price': p.washing_price,
        'rating': p.rating,
        'total_ratings': p.total_ratings,
        'images': json.loads(p.images) if p.images else []
    } for p in products])

@app.route('/api/products', methods=['POST'])
@token_required
@seller_required
def create_product(current_user):
    data = request.json
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        category=data.get('category', 'general'),
        seller_id=current_user.id,
        market_id=data.get('market_id'),
        stock=data.get('stock', 0),
        has_washing=data.get('has_washing', True),
        washing_price=data.get('washing_price', 100.0),
        images=json.dumps(data.get('images', []))
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created successfully!',
        'product': {
            'id': product.id,
            'name': product.name,
            'price': product.price
        }
    }), 201

# Orders routes
@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.json
    
    # Check cart items
    items = data['items']
    if not items:
        return jsonify({'message': 'Cart is empty!'}), 400
    
    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    washing_price = sum(100 for item in items if item.get('washing', False))
    total = subtotal + washing_price + data.get('delivery_fee', 0)
    
    # Check balance if paying with balance
    if data.get('payment_method') == 'balance':
        if current_user.balance < total:
            return jsonify({'message': 'Insufficient balance!'}), 400
    
    # Get seller from first product
    first_product = Product.query.get(items[0]['product_id'])
    if not first_product:
        return jsonify({'message': 'Product not found!'}), 404
    
    # Create order
    order = Order(
        order_code=f"QAT-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}",
        buyer_id=current_user.id,
        seller_id=first_product.seller_id,
        subtotal=subtotal,
        washing_price=washing_price,
        delivery_fee=data.get('delivery_fee', 0),
        total=total,
        delivery_address=data['delivery_address'],
        payment_method=data.get('payment_method'),
        washing_required=washing_price > 0,
        estimated_delivery=datetime.utcnow() + timedelta(hours=1)
    )
    
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Create order items
    for item_data in items:
        item = OrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price'],
            washing=item_data.get('washing', False),
            washing_price=100 if item_data.get('washing', False) else 0
        )
        db.session.add(item)
    
    # Process payment
    if data.get('payment_method') == 'balance':
        current_user.balance -= total
        order.payment_status = 'paid'
        
        # Add to seller's balance
        seller = User.query.get(first_product.seller_id)
        seller.balance += total
    
    # Create notifications
    notifications = []
    
    # Notification to seller
    seller_notification = Notification(
        user_id=first_product.seller_id,
        order_id=order.id,
        title='طلب جديد',
        message=f'لديك طلب جديد #{order.order_code}',
        type='order'
    )
    notifications.append(seller_notification)
    
    # Notification to washer if washing required
    if washing_price > 0:
        washer = Washer.query.filter_by(market_id=first_product.market_id, status='active').first()
        if washer:
            order.washer_id = washer.id
            washer_notification = Notification(
                user_id=washer.id,
                order_id=order.id,
                title='طلب غسيل جديد',
                message=f'طلب غسيل جديد #{order.order_code}',
                type='order'
            )
            notifications.append(washer_notification)
    
    # Notification to driver
    driver = Driver.query.filter_by(status='available').first()
    if driver:
        order.driver_id = driver.id
        driver_notification = Notification(
            user_id=driver.id,
            order_id=order.id,
            title='مهمة توصيل جديدة',
            message=f'مهمة توصيل جديدة #{order.order_code}',
            type='order'
        )
        notifications.append(driver_notification)
    
    # Add all notifications
    for notification in notifications:
        db.session.add(notification)
    
    # Create wallet transaction
    transaction = WalletTransaction(
        user_id=current_user.id,
        type='purchase',
        amount=total,
        balance_before=current_user.balance + total,
        balance_after=current_user.balance,
        reference=order.order_code,
        description=f'شراء منتجات - طلب #{order.order_code}'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully!',
        'order': {
            'id': order.id,
            'order_code': order.order_code,
            'total': order.total,
            'estimated_delivery': order.estimated_delivery.isoformat()
        }
    }), 201

# Wallet routes
@app.route('/api/wallet/balance', methods=['GET'])
@token_required
def get_balance(current_user):
    return jsonify({'balance': current_user.balance})

@app.route('/api/wallet/deposit', methods=['POST'])
@token_required
def deposit_balance(current_user):
    data = request.json
    
    amount = data['amount']
    method = data['method']
    reference = data.get('reference')
    
    # Update balance
    current_user.balance += amount
    
    # Create transaction
    transaction = WalletTransaction(
        user_id=current_user.id,
        type='deposit',
        amount=amount,
        balance_before=current_user.balance - amount,
        balance_after=current_user.balance,
        reference=reference,
        description=f'شحن رصيد عبر {method}'
    )
    db.session.add(transaction)
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title='شحن ناجح',
        message=f'تم شحن {amount} ريال إلى رصيدك',
        type='payment'
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Balance deposited successfully!',
        'new_balance': current_user.balance
    })

# Admin routes
@app.route('/api/admin/markets', methods=['GET'])
@token_required
@admin_required
def get_markets_admin(current_user):
    markets = Market.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'location': m.location,
        'address': m.address,
        'phone': m.phone,
        'manager_name': m.manager_name,
        'status': m.status,
        'washers_count': len(m.washers),
        'products_count': len(m.products),
        'created_at': m.created_at.isoformat()
    } for m in markets])

@app.route('/api/admin/markets', methods=['POST'])
@token_required
@admin_required
def create_market(current_user):
    data = request.json
    
    market = Market(
        name=data['name'],
        location=data.get('location'),
        address=data.get('address'),
        phone=data.get('phone'),
        manager_name=data.get('manager_name')
    )
    
    db.session.add(market)
    db.session.commit()
    
    return jsonify({
        'message': 'Market created successfully!',
        'market': {
            'id': market.id,
            'name': market.name
        }
    }), 201

@app.route('/api/admin/washers', methods=['POST'])
@token_required
@admin_required
def create_washer(current_user):
    data = request.json
    
    washer = Washer(
        name=data['name'],
        market_id=data['market_id'],
        phone=data.get('phone'),
        address=data.get('address'),
        washing_price=data.get('washing_price', 100.0)
    )
    
    db.session.add(washer)
    db.session.commit()
    
    return jsonify({
        'message': 'Washer created successfully!',
        'washer': {
            'id': washer.id,
            'name': washer.name
        }
    }), 201

@app.route('/api/admin/drivers', methods=['POST'])
@token_required
@admin_required
def create_driver(current_user):
    data = request.json
    
    driver = Driver(
        name=data['name'],
        phone=data.get('phone'),
        vehicle_type=data.get('vehicle_type'),
        vehicle_number=data.get('vehicle_number')
    )
    
    db.session.add(driver)
    db.session.commit()
    
    return jsonify({
        'message': 'Driver created successfully!',
        'driver': {
            'id': driver.id,
            'name': driver.name
        }
    }), 201

# Backup routes
@app.route('/api/admin/backup', methods=['GET'])
@token_required
@admin_required
def export_backup(current_user):
    # Export all data to Excel
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Export users
        users = User.query.all()
        users_data = [u.to_dict() for u in users]
        pd.DataFrame(users_data).to_excel(writer, sheet_name='Users', index=False)
        
        # Export products
        products = Product.query.all()
        products_data = [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'category': p.category,
            'seller': p.seller.name,
            'stock': p.stock
        } for p in products]
        pd.DataFrame(products_data).to_excel(writer, sheet_name='Products', index=False)
        
        # Export orders
        orders = Order.query.all()
        orders_data = [{
            'id': o.id,
            'order_code': o.order_code,
            'buyer': o.buyer.name,
            'seller': o.seller.name,
            'total': o.total,
            'status': o.order_status,
            'created_at': o.created_at.isoformat()
        } for o in orders]
        pd.DataFrame(orders_data).to_excel(writer, sheet_name='Orders', index=False)
        
        # Export markets
        markets = Market.query.all()
        markets_data = [{
            'id': m.id,
            'name': m.name,
            'location': m.location,
            'address': m.address
        } for m in markets]
        pd.DataFrame(markets_data).to_excel(writer, sheet_name='Markets', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'qat-backup-{datetime.now().strftime("%Y-%m-%d")}.xlsx'
    )

# Settings routes
@app.route('/api/admin/settings', methods=['GET'])
@token_required
@admin_required
def get_settings(current_user):
    settings = SystemSetting.query.all()
    return jsonify({s.key: s.value for s in settings})

@app.route('/api/admin/settings', methods=['POST'])
@token_required
@admin_required
def update_settings(current_user):
    data = request.json
    
    for key, value in data.items():
        setting = SystemSetting.query.filter_by(key=key).first()
        
        if setting:
            setting.value = value
        else:
            setting = SystemSetting(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
    
    return jsonify({'message': 'Settings updated successfully!'})

# Advertisements routes
@app.route('/api/admin/advertisements', methods=['POST'])
@token_required
@admin_required
def create_advertisement(current_user):
    data = request.json
    
    advertisement = Advertisement(
        title=data['title'],
        content=data.get('content'),
        image_url=data.get('image_url'),
        type=data.get('type', 'home'),
        position=data.get('position', 0),
        start_date=datetime.fromisoformat(data['start_date']) if 'start_date' in data else None,
        end_date=datetime.fromisoformat(data['end_date']) if 'end_date' in data else None,
        status=data.get('status', 'active')
    )
    
    if 'user_id' in data:
        advertisement.user_id = data['user_id']
    
    if 'package_id' in data:
        advertisement.package_id = data['package_id']
    
    db.session.add(advertisement)
    db.session.commit()
    
    return jsonify({
        'message': 'Advertisement created successfully!',
        'advertisement': {
            'id': advertisement.id,
            'title': advertisement.title
        }
    }), 201

# Package routes
@app.route('/api/admin/packages', methods=['POST'])
@token_required
@admin_required
def create_package(current_user):
    data = request.json
    
    package = AdvertisementPackage(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        duration_days=data['duration_days'],
        features=json.dumps(data.get('features', [])),
        max_ads=data.get('max_ads', 1)
    )
    
    db.session.add(package)
    db.session.commit()
    
    return jsonify({
        'message': 'Package created successfully!',
        'package': {
            'id': package.id,
            'name': package.name
        }
    }), 201

# Gift code routes
@app.route('/api/admin/gift-codes', methods=['POST'])
@token_required
@admin_required
def create_gift_code(current_user):
    data = request.json
    
    code = GiftCode(
        code=data.get('code', secrets.token_hex(8).upper()),
        amount=data['amount'],
        created_by=current_user.id,
        expiry_date=datetime.fromisoformat(data['expiry_date']) if 'expiry_date' in data else None
    )
    
    db.session.add(code)
    db.session.commit()
    
    return jsonify({
        'message': 'Gift code created successfully!',
        'code': code.code,
        'amount': code.amount
    }), 201

@app.route('/api/wallet/redeem-gift', methods=['POST'])
@token_required
def redeem_gift_code(current_user):
    data = request.json
    
    code = GiftCode.query.filter_by(code=data['code'], status='active').first()
    
    if not code:
        return jsonify({'message': 'Invalid or expired gift code!'}), 400
    
    if code.expiry_date and code.expiry_date < datetime.utcnow():
        code.status = 'expired'
        db.session.commit()
        return jsonify({'message': 'Gift code has expired!'}), 400
    
    # Redeem code
    current_user.balance += code.amount
    code.used_by = current_user.id
    code.used_at = datetime.utcnow()
    code.status = 'used'
    
    # Create transaction
    transaction = WalletTransaction(
        user_id=current_user.id,
        type='deposit',
        amount=code.amount,
        balance_before=current_user.balance - code.amount,
        balance_after=current_user.balance,
        reference=code.code,
        description='كود هدية'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Gift code redeemed successfully! {code.amount} ريال added to your balance.',
        'new_balance': current_user.balance
    })

# Withdrawal routes
@app.route('/api/wallet/withdraw', methods=['POST'])
@token_required
def request_withdrawal(current_user):
    data = request.json
    
    amount = data['amount']
    
    if amount < 50:
        return jsonify({'message': 'Minimum withdrawal amount is 50 SAR!'}), 400
    
    if current_user.balance < amount:
        return jsonify({'message': 'Insufficient balance!'}), 400
    
    withdrawal = Withdrawal(
        user_id=current_user.id,
        amount=amount,
        wallet_type=data['wallet_type'],
        wallet_number=data['wallet_number'],
        wallet_name=data['wallet_name']
    )
    
    # Reserve amount
    current_user.balance -= amount
    
    db.session.add(withdrawal)
    db.session.commit()
    
    return jsonify({
        'message': 'Withdrawal request submitted successfully!',
        'request_id': withdrawal.id
    })

@app.route('/api/admin/withdrawals/<int:withdrawal_id>/approve', methods=['POST'])
@token_required
@admin_required
def approve_withdrawal(current_user, withdrawal_id):
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != 'pending':
        return jsonify({'message': 'Withdrawal already processed!'}), 400
    
    withdrawal.status = 'approved'
    withdrawal.processed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Withdrawal approved successfully!'})

# Dashboard stats
@app.route('/api/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_stats(current_user):
    total_users = User.query.count()
    total_sellers = User.query.filter_by(user_type='seller').count()
    total_buyers = User.query.filter_by(user_type='buyer').count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return jsonify({
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_buyers': total_buyers,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': [{
            'id': o.id,
            'order_code': o.order_code,
            'total': o.total,
            'status': o.order_status,
            'created_at': o.created_at.isoformat()
        } for o in recent_orders]
    })

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(email='admin@qat.com').first():
        admin = User(
            name='مدير النظام',
            email='admin@qat.com',
            phone='771831482',
            user_type='admin'
        )
        admin.set_password('admin123')
        admin.balance = 10000
        db.session.add(admin)
        db.session.commit()
    
    # Create default settings
    default_settings = {
        'app_name': 'تطبيق قات',
        'washing_price': '100',
        'delivery_fee': '0',
        'min_withdrawal': '50',
        'primary_color': '#2E7D32',
        'secondary_color': '#FF9800',
        'contact_phone': '771831482',
        'contact_email': 'support@qat.com'
    }
    
    for key, value in default_settings.items():
        if not SystemSetting.query.filter_by(key=key).first():
            setting = SystemSetting(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
