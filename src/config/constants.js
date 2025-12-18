// src/config/constants.js
export const APP_CONFIG = {
  APP_NAME: 'تطبيق قات',
  APP_VERSION: '1.0.0',
  CURRENCY: 'ريال',
  CURRENCY_SYMBOL: 'ر.س',
  SUPPORT_PHONE: '771831482',
  SUPPORT_EMAIL: 'support@qatapp.com',
  ADMIN_PHONE: '771831482',
  ADMIN_NAME: 'يوسف محمد علي حمود زهير',
  WASHING_PRICE: 100,
  DELIVERY_FEE: 10,
  TAX_PERCENTAGE: 0,
  MIN_WITHDRAWAL_AMOUNT: 50,
  MAX_WITHDRAWAL_AMOUNT: 5000,
  WITHDRAWAL_FEE_PERCENTAGE: 2,
};

export const PAYMENT_METHODS = {
  BALANCE: { id: 'balance', name: 'رصيد الحساب', icon: 'wallet' },
  JIB: { id: 'jib', name: 'محفظة جيب', icon: 'cellphone', phone: '771831482' },
  JAWALY: { id: 'jawaly', name: 'محفظة جوالي', icon: 'cellphone', phone: '771831482' },
  MOBI_MONEY: { id: 'mobi', name: 'محفظة موبايل موني', icon: 'cellphone' },
  SHAMEL_MONEY: { id: 'shamel', name: 'محفظة الشامل موني', icon: 'cellphone' },
  FULOOS: { id: 'fuloos', name: 'محفظة فلوسك', icon: 'cellphone' },
};

export const ORDER_STATUS = {
  PENDING: { id: 'pending', name: 'قيد الانتظار', color: '#FF9800' },
  CONFIRMED: { id: 'confirmed', name: 'تم التأكيد', color: '#2196F3' },
  PREPARING: { id: 'preparing', name: 'قيد التحضير', color: '#FF5722' },
  WASHING: { id: 'washing', name: 'في المغسلة', color: '#00BCD4' },
  READY_FOR_DELIVERY: { id: 'ready', name: 'جاهز للتوصيل', color: '#9C27B0' },
  DELIVERING: { id: 'delivering', name: 'قيد التوصيل', color: '#795548' },
  DELIVERED: { id: 'delivered', name: 'تم التوصيل', color: '#4CAF50' },
  CANCELLED: { id: 'cancelled', name: 'ملغى', color: '#D32F2F' },
  REFUNDED: { id: 'refunded', name: 'تم الاسترجاع', color: '#607D8B' },
};

export const USER_TYPES = {
  BUYER: 'buyer',
  SELLER: 'seller',
  DRIVER: 'driver',
  WASHER: 'washer',
  ADMIN: 'admin',
};

export const AD_TYPES = {
  BANNER: 'banner',
  INTERSTITIAL: 'interstitial',
  NATIVE: 'native',
  VIDEO: 'video',
};

export const AD_PACKAGES = [
  {
    id: 'basic',
    name: 'الباقة الأساسية',
    price: 100,
    duration: 7,
    features: ['إعلان في الشريط العلوي', '7 أيام', '1000 ظهور'],
  },
  {
    id: 'standard',
    name: 'الباقة المتوسطة',
    price: 250,
    duration: 15,
    features: ['إعلان مميز', '15 يوم', '5000 ظهور', 'أولوية في البحث'],
  },
  {
    id: 'premium',
    name: 'الباقة المميزة',
    price: 500,
    duration: 30,
    features: ['إعلان رئيسي', '30 يوم', '15000 ظهور', 'أولوية عالية', 'إحصاءات مفصلة'],
  },
];
