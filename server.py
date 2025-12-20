const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const nodemailer = require('nodemailer');
const ExcelJS = require('exceljs');

const app = express();
const PORT = process.env.PORT || 3000;

// تهيئة قاعدة البيانات المحلية
const DB_FILE = path.join(__dirname, 'database', 'database.json');
let database = {};

// تحميل قاعدة البيانات
function loadDatabase() {
    if (fs.existsSync(DB_FILE)) {
        const data = fs.readFileSync(DB_FILE, 'utf8');
        database = JSON.parse(data);
    } else {
        database = {
            users: [],
            products: [],
            orders: [],
            markets: [],
            washingStations: [],
            drivers: [],
            advertisements: [],
            packages: [],
            wallets: [],
            transactions: [],
            notifications: [],
            coupons: [],
            backups: []
        };
        saveDatabase();
    }
}

// حفظ قاعدة البيانات
function saveDatabase() {
    fs.writeFileSync(DB_FILE, JSON.stringify(database, null, 2), 'utf8');
}

// تكوين multer للملفات
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/')
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname)
    }
});

const upload = multer({ storage: storage });

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));
app.use(session({
    secret: 'qat-app-secret-key',
    resave: false,
    saveUninitialized: true
}));

// JWT Secret
const JWT_SECRET = 'your-jwt-secret-key-change-in-production';

// Middleware للمصادقة
function authenticateToken(req, res, next) {
    const token = req.session.token || req.headers['authorization'];
    
    if (!token) {
        return res.status(401).json({ error: 'الوصول مرفوض' });
    }
    
    try {
        const decoded = jwt.verify(token.replace('Bearer ', ''), JWT_SECRET);
        req.user = decoded;
        next();
    } catch (error) {
        res.status(403).json({ error: 'توكن غير صالح' });
    }
}

// Middleware للتحقق من صلاحيات المدير
function isAdmin(req, res, next) {
    if (req.user && req.user.role === 'admin') {
        next();
    } else {
        res.status(403).json({ error: 'صلاحيات غير كافية' });
    }
}

// Middleware للتحقق من صلاحيات البائع
function isSeller(req, res, next) {
    if (req.user && (req.user.role === 'seller' || req.user.role === 'admin')) {
        next();
    } else {
        res.status(403).json({ error: 'صلاحيات غير كافية' });
    }
}

// Middleware للتحقق من صلاحيات المشتري
function isBuyer(req, res, next) {
    if (req.user && (req.user.role === 'buyer' || req.user.role === 'admin')) {
        next();
    } else {
        res.status(403).json({ error: 'صلاحيات غير كافية' });
    }
}

// تكوين البريد الإلكتروني
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'your-email@gmail.com',
        pass: 'your-email-password'
    }
});

// إرسال الإشعارات
async function sendNotification(userId, title, message) {
    const notification = {
        id: Date.now(),
        userId,
        title,
        message,
        read: false,
        createdAt: new Date().toISOString()
    };
    
    database.notifications.push(notification);
    saveDatabase();
    
    // إرسال بريد إلكتروني إذا كان المستخدم مفعل الإشعارات
    const user = database.users.find(u => u.id === userId);
    if (user && user.emailNotifications) {
        await transporter.sendMail({
            from: 'qat-app@example.com',
            to: user.email,
            subject: title,
            text: message,
            html: `<h1>${title}</h1><p>${message}</p>`
        });
    }
}

// المسارات الرئيسية
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

// المسارات العامة
app.post('/api/register', async (req, res) => {
    try {
        const { name, email, phone, password, role, storeName, vehicleType } = req.body;
        
        // التحقق من وجود المستخدم
        const existingUser = database.users.find(u => u.email === email);
        if (existingUser) {
            return res.status(400).json({ error: 'البريد الإلكتروني مسجل بالفعل' });
        }
        
        // تشفير كلمة المرور
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // إنشاء المستخدم
        const user = {
            id: Date.now(),
            name,
            email,
            phone,
            password: hashedPassword,
            role: role || 'buyer',
            storeName: role === 'seller' ? storeName : null,
            vehicleType: role === 'driver' ? vehicleType : null,
            walletBalance: 0,
            rating: 0,
            totalSales: 0,
            createdAt: new Date().toISOString(),
            isActive: true,
            emailNotifications: true,
            pushNotifications: true
        };
        
        // إنشاء محفظة للمستخدم
        const wallet = {
            id: Date.now(),
            userId: user.id,
            balance: 0,
            transactions: [],
            createdAt: new Date().toISOString()
        };
        
        database.users.push(user);
        database.wallets.push(wallet);
        saveDatabase();
        
        // إنشاء توكن
        const token = jwt.sign(
            { id: user.id, email: user.email, role: user.role },
            JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        res.json({
            success: true,
            token,
            user: {
                id: user.id,
                name: user.name,
                email: user.email,
                role: user.role
            }
        });
    } catch (error) {
        res.status(500).json({ error: 'خطأ في إنشاء الحساب' });
    }
});

app.post('/api/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        // البحث عن المستخدم
        const user = database.users.find(u => u.email === email);
        if (!user) {
            return res.status(400).json({ error: 'بيانات الدخول غير صحيحة' });
        }
        
        // التحقق من كلمة المرور
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({ error: 'بيانات الدخول غير صحيحة' });
        }
        
        // إنشاء توكن
        const token = jwt.sign(
            { id: user.id, email: user.email, role: user.role },
            JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        // حفظ في الجلسة
        req.session.token = token;
        req.session.userId = user.id;
        
        res.json({
            success: true,
            token,
            user: {
                id: user.id,
                name: user.name,
                email: user.email,
                role: user.role,
                walletBalance: user.walletBalance
            }
        });
    } catch (error) {
        res.status(500).json({ error: 'خطأ في تسجيل الدخول' });
    }
});

// مسارات المدير
app.get('/api/admin/dashboard', authenticateToken, isAdmin, (req, res) => {
    const stats = {
        totalUsers: database.users.length,
        totalSellers: database.users.filter(u => u.role === 'seller').length,
        totalBuyers: database.users.filter(u => u.role === 'buyer').length,
        totalDrivers: database.users.filter(u => u.role === 'driver').length,
        totalProducts: database.products.length,
        totalOrders: database.orders.length,
        totalRevenue: database.orders.reduce((sum, order) => sum + order.totalAmount, 0),
        pendingOrders: database.orders.filter(o => o.status === 'pending').length,
        activeMarkets: database.markets.filter(m => m.isActive).length,
        activeWashingStations: database.washingStations.filter(w => w.isActive).length
    };
    
    res.json({ success: true, stats });
});

// إدارة الأسواق
app.post('/api/admin/markets', authenticateToken, isAdmin, (req, res) => {
    const { name, location, address, phone, managerName, isActive } = req.body;
    
    const market = {
        id: Date.now(),
        name,
        location,
        address,
        phone,
        managerName,
        isActive: isActive !== false,
        washingStations: [],
        createdAt: new Date().toISOString()
    };
    
    database.markets.push(market);
    saveDatabase();
    
    res.json({ success: true, market });
});

// إدارة مغاسل القات
app.post('/api/admin/washing-stations', authenticateToken, isAdmin, (req, res) => {
    const { name, marketId, location, phone, managerName, washingPrice, isActive } = req.body;
    
    const washingStation = {
        id: Date.now(),
        name,
        marketId: parseInt(marketId),
        location,
        phone,
        managerName,
        washingPrice: washingPrice || 100,
        isActive: isActive !== false,
        createdAt: new Date().toISOString()
    };
    
    database.washingStations.push(washingStation);
    saveDatabase();
    
    res.json({ success: true, washingStation });
});

// إدارة مندوبي التوصيل
app.post('/api/admin/drivers', authenticateToken, isAdmin, (req, res) => {
    const { name, phone, vehicleType, vehicleNumber, marketId, isActive } = req.body;
    
    const driver = {
        id: Date.now(),
        name,
        phone,
        vehicleType,
        vehicleNumber,
        marketId: parseInt(marketId),
        isActive: isActive !== false,
        rating: 0,
        completedOrders: 0,
        currentLocation: null,
        isAvailable: true,
        createdAt: new Date().toISOString()
    };
    
    database.drivers.push(driver);
    saveDatabase();
    
    res.json({ success: true, driver });
});

// إنشاء كوبونات هدايا
app.post('/api/admin/coupons', authenticateToken, isAdmin, (req, res) => {
    const { code, amount, expiresAt, maxUses, isActive } = req.body;
    
    const coupon = {
        id: Date.now(),
        code,
        amount: parseFloat(amount),
        expiresAt,
        maxUses: parseInt(maxUses) || 1,
        usedCount: 0,
        isActive: isActive !== false,
        createdAt: new Date().toISOString()
    };
    
    database.coupons.push(coupon);
    saveDatabase();
    
    res.json({ success: true, coupon });
});

// إنشاء باقات إعلانية
app.post('/api/admin/ad-packages', authenticateToken, isAdmin, (req, res) => {
    const { name, description, price, duration, features, isActive } = req.body;
    
    const package = {
        id: Date.now(),
        name,
        description,
        price: parseFloat(price),
        duration: parseInt(duration), // بالأيام
        features: Array.isArray(features) ? features : [],
        isActive: isActive !== false,
        createdAt: new Date().toISOString()
    };
    
    database.packages.push(package);
    saveDatabase();
    
    res.json({ success: true, package });
});

// نسخ احتياطي لقاعدة البيانات
app.get('/api/admin/backup', authenticateToken, isAdmin, async (req, res) => {
    try {
        const workbook = new ExcelJS.Workbook();
        
        // إنشاء أوراق للبيانات
        const sheets = [
            { name: 'users', data: database.users },
            { name: 'products', data: database.products },
            { name: 'orders', data: database.orders },
            { name: 'markets', data: database.markets },
            { name: 'washingStations', data: database.washingStations },
            { name: 'drivers', data: database.drivers },
            { name: 'transactions', data: database.transactions }
        ];
        
        for (const sheet of sheets) {
            const worksheet = workbook.addWorksheet(sheet.name);
            
            if (sheet.data.length > 0) {
                // إضافة العناوين
                const headers = Object.keys(sheet.data[0]);
                worksheet.addRow(headers);
                
                // إضافة البيانات
                sheet.data.forEach(item => {
                    const row = headers.map(header => item[header]);
                    worksheet.addRow(row);
                });
            }
        }
        
        // حفظ الملف
        const fileName = `backup-${Date.now()}.xlsx`;
        const filePath = path.join(__dirname, 'backups', fileName);
        
        await workbook.xlsx.writeFile(filePath);
        
        // حفظ معلومات النسخ الاحتياطي
        const backup = {
            id: Date.now(),
            fileName,
            filePath,
            createdAt: new Date().toISOString(),
            createdBy: req.user.id
        };
        
        database.backups.push(backup);
        saveDatabase();
        
        res.json({ success: true, fileName, downloadUrl: `/backups/${fileName}` });
    } catch (error) {
        res.status(500).json({ error: 'خطأ في إنشاء النسخة الاحتياطية' });
    }
});

// مسارات البائعين
app.get('/api/seller/products', authenticateToken, isSeller, (req, res) => {
    const sellerId = req.user.id;
    const sellerProducts = database.products.filter(p => p.sellerId === sellerId);
    
    res.json({ success: true, products: sellerProducts });
});

app.post('/api/seller/products', authenticateToken, isSeller, upload.array('images', 5), (req, res) => {
    const { name, description, price, category, quantity, marketId } = req.body;
    const images = req.files ? req.files.map(f => f.filename) : [];
    
    const product = {
        id: Date.now(),
        sellerId: req.user.id,
        name,
        description,
        price: parseFloat(price),
        originalPrice: parseFloat(price),
        category,
        quantity: parseInt(quantity),
        marketId: parseInt(marketId),
        images,
        rating: 0,
        totalSold: 0,
        reviews: [],
        isActive: true,
        requiresWashing: false,
        washingPrice: 100,
        createdAt: new Date().toISOString()
    };
    
    database.products.push(product);
    saveDatabase();
    
    res.json({ success: true, product });
});

// طلبات البائع
app.get('/api/seller/orders', authenticateToken, isSeller, (req, res) => {
    const sellerId = req.user.id;
    
    // جلب طلبات منتجات البائع
    const sellerOrders = database.orders.filter(order => 
        order.items.some(item => {
            const product = database.products.find(p => p.id === item.productId);
            return product && product.sellerId === sellerId;
        })
    );
    
    res.json({ success: true, orders: sellerOrders });
});

// سحب الأموال
app.post('/api/seller/withdraw', authenticateToken, isSeller, (req, res) => {
    const { amount, walletType, walletPhone, walletName } = req.body;
    const sellerId = req.user.id;
    
    // التحقق من رصيد البائع
    const seller = database.users.find(u => u.id === sellerId);
    if (!seller || seller.walletBalance < amount) {
        return res.status(400).json({ error: 'رصيد غير كافي' });
    }
    
    // خصم المبلغ
    seller.walletBalance -= parseFloat(amount);
    
    // تسجيل المعاملة
    const transaction = {
        id: Date.now(),
        userId: sellerId,
        type: 'withdrawal',
        amount: parseFloat(amount),
        walletType,
        walletPhone,
        walletName,
        status: 'pending',
        createdAt: new Date().toISOString()
    };
    
    database.transactions.push(transaction);
    saveDatabase();
    
    // إرسال إشعار للمدير
    sendNotification(
        database.users.find(u => u.role === 'admin')?.id,
        'طلب سحب أموال',
        `طلب البائع ${seller.name} سحب مبلغ ${amount} ريال`
    );
    
    res.json({ success: true, transaction });
});

// مسارات المشترين
app.get('/api/buyer/products', authenticateToken, isBuyer, (req, res) => {
    const products = database.products.filter(p => p.isActive && p.quantity > 0);
    res.json({ success: true, products });
});

app.post('/api/buyer/cart/add', authenticateToken, isBuyer, (req, res) => {
    const { productId, quantity, requiresWashing } = req.body;
    
    const product = database.products.find(p => p.id === parseInt(productId));
    if (!product) {
        return res.status(404).json({ error: 'المنتج غير موجود' });
    }
    
    if (product.quantity < quantity) {
        return res.status(400).json({ error: 'الكمية غير متوفرة' });
    }
    
    // حساب السعر النهائي
    let finalPrice = product.price * quantity;
    if (requiresWashing) {
        finalPrice += product.washingPrice * quantity;
    }
    
    // إضافة للسلة (في حالة حقيقية، سيكون هناك جدول للسلة)
    const cartItem = {
        productId: product.id,
        productName: product.name,
        quantity,
        price: product.price,
        requiresWashing,
        washingPrice: requiresWashing ? product.washingPrice : 0,
        totalPrice: finalPrice,
        sellerId: product.sellerId,
        marketId: product.marketId
    };
    
    res.json({ success: true, cartItem });
});

// إنشاء طلب
app.post('/api/buyer/order/create', authenticateToken, isBuyer, async (req, res) => {
    try {
        const { items, deliveryAddress, paymentMethod, couponCode } = req.body;
        const buyerId = req.user.id;
        
        // التحقق من المنتجات والكميات
        let totalAmount = 0;
        const orderItems = [];
        
        for (const item of items) {
            const product = database.products.find(p => p.id === item.productId);
            if (!product) {
                return res.status(404).json({ error: `المنتج ${item.productId} غير موجود` });
            }
            
            if (product.quantity < item.quantity) {
                return res.status(400).json({ error: `الكمية غير متوفرة للمنتج ${product.name}` });
            }
            
            // حساب سعر المنتج
            let itemPrice = product.price * item.quantity;
            if (item.requiresWashing) {
                itemPrice += product.washingPrice * item.quantity;
            }
            
            totalAmount += itemPrice;
            
            orderItems.push({
                ...item,
                productName: product.name,
                itemPrice
            });
            
            // خصم الكمية من المخزون
            product.quantity -= item.quantity;
            product.totalSold += item.quantity;
        }
        
        // تطبيق الكوبون إذا كان موجوداً
        let discount = 0;
        if (couponCode) {
            const coupon = database.coupons.find(c => c.code === couponCode && c.isActive);
            if (coupon) {
                if (coupon.usedCount < coupon.maxUses && new Date(coupon.expiresAt) > new Date()) {
                    discount = coupon.amount;
                    coupon.usedCount++;
                }
            }
        }
        
        totalAmount -= discount;
        
        // التحقق من رصيد المشتري
        const buyer = database.users.find(u => u.id === buyerId);
        if (!buyer) {
            return res.status(404).json({ error: 'المشتري غير موجود' });
        }
        
        if (paymentMethod === 'wallet' && buyer.walletBalance < totalAmount) {
            return res.status(400).json({ error: 'رصيد غير كافي' });
        }
        
        // خصم المبلغ من رصيد المشتري
        if (paymentMethod === 'wallet') {
            buyer.walletBalance -= totalAmount;
        }
        
        // إنشاء رمز الطلب (باركود)
        const orderCode = Math.random().toString(36).substring(2, 10).toUpperCase();
        
        // البحث عن مغسلة في نفس السوق
        const firstProduct = database.products.find(p => p.id === items[0].productId);
        const washingStation = database.washingStations.find(w => 
            w.marketId === firstProduct.marketId && w.isActive
        );
        
        // البحث عن مندوب توصيل متاح
        const availableDriver = database.drivers.find(d => 
            d.marketId === firstProduct.marketId && d.isAvailable && d.isActive
        );
        
        // إنشاء الطلب
        const order = {
            id: Date.now(),
            buyerId,
            items: orderItems,
            totalAmount,
            discount,
            deliveryAddress,
            paymentMethod,
            status: 'pending',
            paymentStatus: paymentMethod === 'wallet' ? 'paid' : 'pending',
            orderCode,
            washingStationId: washingStation ? washingStation.id : null,
            driverId: availableDriver ? availableDriver.id : null,
            sellerIds: [...new Set(orderItems.map(item => {
                const product = database.products.find(p => p.id === item.productId);
                return product.sellerId;
            }))],
            createdAt: new Date().toISOString(),
            estimatedDelivery: new Date(Date.now() + 60 * 60 * 1000).toISOString() // بعد ساعة
        };
        
        database.orders.push(order);
        
        // إضافة المبلغ لحسابات البائعين
        orderItems.forEach(item => {
            const product = database.products.find(p => p.id === item.productId);
            if (product) {
                const seller = database.users.find(u => u.id === product.sellerId);
                if (seller) {
                    seller.walletBalance += item.itemPrice;
                    seller.totalSales += item.itemPrice;
                }
            }
        });
        
        saveDatabase();
        
        // إرسال الإشعارات
        // 1. للمشتري
        await sendNotification(
            buyerId,
            'تم إنشاء طلبك بنجاح',
            `تم إنشاء طلبك برقم #${order.id} والمبلغ ${totalAmount} ريال`
        );
        
        // 2. للبائعين
        order.sellerIds.forEach(async sellerId => {
            await sendNotification(
                sellerId,
                'طلب جديد',
                `لديك طلب جديد برقم #${order.id}`
            );
        });
        
        // 3. لمغسلة القات إذا كانت مطلوبة
        if (washingStation && items.some(item => item.requiresWashing)) {
            await sendNotification(
                washingStation.managerId || database.users.find(u => u.role === 'admin')?.id,
                'طلب غسل قات',
                `طلب جديد لغسل قات برقم #${order.id}`
            );
        }
        
        // 4. لمندوب التوصيل
        if (availableDriver) {
            await sendNotification(
                availableDriver.userId || database.users.find(u => u.role === 'admin')?.id,
                'طلب توصيل',
                `طلب توصيل جديد برقم #${order.id}`
            );
        }
        
        res.json({ 
            success: true, 
            order,
            orderCode,
            message: 'تم إنشاء الطلب بنجاح'
        });
        
    } catch (error) {
        res.status(500).json({ error: 'خطأ في إنشاء الطلب' });
    }
});

// شحن الرصيد
app.post('/api/wallet/topup', authenticateToken, (req, res) => {
    const { amount, walletType, transactionId, phone } = req.body;
    const userId = req.user.id;
    
    const user = database.users.find(u => u.id === userId);
    if (!user) {
        return res.status(404).json({ error: 'المستخدم غير موجود' });
    }
    
    // تسجيل المعاملة
    const transaction = {
        id: Date.now(),
        userId,
        type: 'deposit',
        amount: parseFloat(amount),
        walletType,
        transactionId,
        phone,
        status: 'pending',
        createdAt: new Date().toISOString()
    };
    
    database.transactions.push(transaction);
    
    // في حالة حقيقية، هنا يتم التحقق من المعاملة عبر بوابة الدفع
    // ولكن في هذا المثال، نفترض أن الدفع تم بنجاح
    
    setTimeout(() => {
        transaction.status = 'completed';
        user.walletBalance += parseFloat(amount);
        saveDatabase();
        
        sendNotification(
            userId,
            'تم شحن الرصيد',
            `تم شحن مبلغ ${amount} ريال إلى محفظتك`
        );
    }, 2000);
    
    res.json({ 
        success: true, 
        transaction,
        message: 'جاري معالجة طلب الشحن'
    });
});

// تطبيق الكوبون
app.post('/api/coupon/apply', authenticateToken, (req, res) => {
    const { code } = req.body;
    
    const coupon = database.coupons.find(c => c.code === code);
    if (!coupon) {
        return res.status(404).json({ error: 'كود الخصم غير صحيح' });
    }
    
    if (!coupon.isActive) {
        return res.status(400).json({ error: 'كود الخصم غير فعال' });
    }
    
    if (coupon.usedCount >= coupon.maxUses) {
        return res.status(400).json({ error: 'تم استخدام الحد الأقصى لرمز الخصم' });
    }
    
    if (new Date(coupon.expiresAt) < new Date()) {
        return res.status(400).json({ error: 'انتهت صلاحية كود الخصم' });
    }
    
    res.json({ 
        success: true, 
        coupon: {
            code: coupon.code,
            amount: coupon.amount
        }
    });
});

// شراء باقة إعلانية
app.post('/api/ad/buy', authenticateToken, isSeller, (req, res) => {
    const { packageId } = req.body;
    const sellerId = req.user.id;
    
    const adPackage = database.packages.find(p => p.id === parseInt(packageId));
    if (!adPackage) {
        return res.status(404).json({ error: 'الباقة غير موجودة' });
    }
    
    if (!adPackage.isActive) {
        return res.status(400).json({ error: 'الباقة غير فعالة' });
    }
    
    const seller = database.users.find(u => u.id === sellerId);
    if (!seller) {
        return res.status(404).json({ error: 'البائع غير موجود' });
    }
    
    if (seller.walletBalance < adPackage.price) {
        return res.status(400).json({ error: 'رصيد غير كافي' });
    }
    
    // خصم المبلغ
    seller.walletBalance -= adPackage.price;
    
    // إنشاء الإعلان
    const advertisement = {
        id: Date.now(),
        sellerId,
        packageId: adPackage.id,
        packageName: adPackage.name,
        price: adPackage.price,
        startDate: new Date().toISOString(),
        endDate: new Date(Date.now() + adPackage.duration * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active',
        impressions: 0,
        clicks: 0,
        createdAt: new Date().toISOString()
    };
    
    database.advertisements.push(advertisement);
    saveDatabase();
    
    sendNotification(
        sellerId,
        'تم شراء الباقة الإعلانية',
        `تم تفعيل الباقة ${adPackage.name} لمدة ${adPackage.duration} أيام`
    );
    
    res.json({ success: true, advertisement });
});

// تحميل قاعدة البيانات عند بدء التشغيل
loadDatabase();

// إنشاء مجلد النسخ الاحتياطي إذا لم يكن موجوداً
const backupsDir = path.join(__dirname, 'backups');
if (!fs.existsSync(backupsDir)) {
    fs.mkdirSync(backupsDir, { recursive: true });
}

// تشغيل الخادم
app.listen(PORT, () => {
    console.log(`✅ الخادم يعمل على http://localhost:${PORT}`);
    console.log(`✅ API متاح على http://localhost:${PORT}/api`);
});

// تصدير للتشغيل على Render.com
module.exports = app;
