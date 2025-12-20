import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///qat_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # App settings
    APP_NAME = 'تطبيق قات'
    WASHING_PRICE = 100.0
    DELIVERY_FEE = 0.0
    MIN_WITHDRAWAL = 50.0
    CONTACT_PHONE = '771831482'
    CONTACT_EMAIL = 'support@qat.com'
    
    # Payment settings
    WALLET_NUMBER = '771831482'
    WALLET_NAME = 'يوسف محمد علي حمود زهير'
    
    # Notification settings
    SMS_ENABLED = False
    EMAIL_ENABLED = False
    
    # Backup settings
    BACKUP_DIR = 'backups'
    BACKUP_RETENTION_DAYS = 30

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
    # In production, use environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
