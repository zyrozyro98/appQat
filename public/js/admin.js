// admin.js
let currentUser = null;
let currentSection = 'dashboard';

// تهيئة التطبيق
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadDashboard();
    setupEventListeners();
});

// التحقق من المصادقة
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!token || !user || user.role !== 'admin') {
        window.location.href = '/';
        return;
    }
    
    currentUser = user;
    document.getElementById('adminName').textContent = user.name;
    
    // تحميل الإشعارات
    loadNotifications();
}

// إعداد مستمعي الأحداث
function setupEventListeners() {
    // التنقل في القائمة الجانبية
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showSection(section);
        });
    });
    
    // نموذج إضافة سوق
    document.getElementById('addMarketForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addMarket(new FormData(this));
    });
    
    // نموذج إضافة مغسلة
    document.getElementById('addWashingStationForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addWashingStation(new FormData(this));
    });
    
    // نموذج إضافة مندوب
    document.getElementById('addDriverForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addDriver(new FormData(this));
    });
}

// تحميل لوحة التحكم
async function loadDashboard() {
    try {
        const response = await fetch('/api/admin/dashboard', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderStats(data.stats);
        }
    } catch (error) {
        console.error('خطأ في تحميل لوحة التحكم:', error);
    }
}

// عرض الإحصائيات
function renderStats(stats) {
    const statsContainer = document.getElementById('statsContainer');
    const statsHTML = `
        <div class="stat-card">
            <div class="stat-number">${stats.totalUsers}</div>
            <div class="stat-label">إجمالي المستخدمين</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.totalSellers}</div>
            <div class="stat-label">البائعون</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.totalBuyers}</div>
            <div class="stat-label">المشترون</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.totalDrivers}</div>
            <div class="stat-label">مندوبي التوصيل</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.totalProducts}</div>
            <div class="stat-label">المنتجات</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.totalOrders}</div>
            <div class="stat-label">الطلبات</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.totalRevenue.toFixed(2)}</div>
            <div class="stat-label">إجمالي الإيرادات (ريال)</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.pendingOrders}</div>
            <div class="stat-label">طلبات معلقة</div>
        </div>
    `;
    
    statsContainer.innerHTML = statsHTML;
}

// عرض القسم المحدد
async function showSection(sectionName) {
    currentSection = sectionName;
    
    // تحديث القائمة الجانبية
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionName}`) {
            link.classList.add('active');
        }
    });
    
    // تحديث العنوان
    const titles = {
        dashboard: 'لوحة التحكم',
        markets: 'إدارة الأسواق',
        'washing-stations': 'مغاسل القات',
        drivers: 'مندوبي التوصيل',
        users: 'إدارة المستخدمين',
        products: 'إدارة المنتجات',
        orders: 'الطلبات',
        ads: 'الإعلانات',
        coupons: 'كوبونات الهدايا',
        transactions: 'المعاملات',
        settings: 'الإعدادات',
        backup: 'النسخ الاحتياطي'
    };
    
    const contentArea = document.querySelector('.content-area');
    contentArea.innerHTML = `
        <div class="content-section active" id="${sectionName}">
            <h1>${titles[sectionName]}</h1>
            <div id="${sectionName}Content"></div>
        </div>
    `;
    
    // تحميل محتوى القسم
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'markets':
            loadMarkets();
            break;
        case 'washing-stations':
            loadWashingStations();
            break;
        case 'drivers':
            loadDrivers();
            break;
        case 'users':
            loadUsers();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'backup':
            showBackupSection();
            break;
    }
}

// إضافة سوق جديد
async function addMarket(formData) {
    try {
        const marketData = {};
        formData.forEach((value, key) => {
            if (key === 'isActive') {
                marketData[key] = value === 'on';
            } else {
                marketData[key] = value;
            }
        });
        
        const response = await fetch('/api/admin/markets', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(marketData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('تم إضافة السوق بنجاح');
            closeModal('addMarketModal');
            loadMarkets();
        }
    } catch (error) {
        console.error('خطأ في إضافة السوق:', error);
        alert('حدث خطأ أثناء إضافة السوق');
    }
}

// إضافة مغسلة
async function addWashingStation(formData) {
    try {
        const stationData = {};
        formData.forEach((value, key) => {
            if (key === 'isActive' || key === 'washingPrice') {
                stationData[key] = key === 'isActive' ? value === 'on' : parseFloat(value);
            } else if (key === 'marketId') {
                stationData[key] = parseInt(value);
            } else {
                stationData[key] = value;
            }
        });
        
        const response = await fetch('/api/admin/washing-stations', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(stationData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('تم إضافة المغسلة بنجاح');
            closeModal('addWashingStationModal');
            loadWashingStations();
        }
    } catch (error) {
        console.error('خطأ في إضافة المغسلة:', error);
        alert('حدث خطأ أثناء إضافة المغسلة');
    }
}

// إضافة مندوب
async function addDriver(formData) {
    try {
        const driverData = {};
        formData.forEach((value, key) => {
            if (key === 'isActive') {
                driverData[key] = value === 'on';
            } else if (key === 'marketId') {
                driverData[key] = parseInt(value);
            } else {
                driverData[key] = value;
            }
        });
        
        const response = await fetch('/api/admin/drivers', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(driverData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('تم إضافة المندوب بنجاح');
            closeModal('addDriverModal');
            loadDrivers();
        }
    } catch (error) {
        console.error('خطأ في إضافة المندوب:', error);
        alert('حدث خطأ أثناء إضافة المندوب');
    }
}

// تحميل الأسواق
async function loadMarkets() {
    try {
        const response = await fetch('/api/admin/markets', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderMarkets(data.markets);
        }
    } catch (error) {
        console.error('خطأ في تحميل الأسواق:', error);
    }
}

// عرض الأسواق
function renderMarkets(markets) {
    const container = document.getElementById('marketsContent');
    const addButton = '<button class="btn-primary" onclick="openModal(\'addMarketModal\')"><i class="fas fa-plus"></i> إضافة سوق جديد</button>';
    
    if (!markets || markets.length === 0) {
        container.innerHTML = addButton + '<p>لا توجد أسواق</p>';
        return;
    }
    
    let tableHTML = `
        ${addButton}
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>اسم السوق</th>
                        <th>الموقع</th>
                        <th>رقم الهاتف</th>
                        <th>المدير</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    markets.forEach((market, index) => {
        tableHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${market.name}</td>
                <td>${market.location}</td>
                <td>${market.phone}</td>
                <td>${market.managerName}</td>
                <td>
                    <span class="status-badge ${market.isActive ? 'active' : 'inactive'}">
                        ${market.isActive ? 'نشط' : 'غير نشط'}
                    </span>
                </td>
                <td>
                    <button class="btn-sm btn-edit"><i class="fas fa-edit"></i></button>
                    <button class="btn-sm btn-delete"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table></div>';
    container.innerHTML = tableHTML;
}

// فتح النافذة المنبثقة
function openModal(modalId) {
    document.getElementById('modalOverlay').style.display = 'block';
    document.getElementById(modalId).style.display = 'block';
}

// إغلاق النافذة المنبثقة
function closeModal(modalId) {
    document.getElementById('modalOverlay').style.display = 'none';
    document.getElementById(modalId).style.display = 'none';
}

// تحميل مغاسل القات
async function loadWashingStations() {
    try {
        const response = await fetch('/api/admin/washing-stations', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderWashingStations(data.stations);
            
            // تحميل الأسواق لقائمة الاختيار
            loadMarketsForSelect();
        }
    } catch (error) {
        console.error('خطأ في تحميل المغاسل:', error);
    }
}

// تحميل الأسواق لقائمة الاختيار
async function loadMarketsForSelect() {
    try {
        const response = await fetch('/api/admin/markets', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            const marketSelect = document.getElementById('marketSelect');
            marketSelect.innerHTML = '<option value="">اختر السوق</option>';
            
            data.markets.forEach(market => {
                const option = document.createElement('option');
                option.value = market.id;
                option.textContent = market.name;
                marketSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('خطأ في تحميل الأسواق:', error);
    }
}

// تحميل مندوبي التوصيل
async function loadDrivers() {
    try {
        const response = await fetch('/api/admin/drivers', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderDrivers(data.drivers);
        }
    } catch (error) {
        console.error('خطأ في تحميل المندوبين:', error);
    }
}

// تحميل الإشعارات
async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            const unreadCount = data.notifications.filter(n => !n.read).length;
            document.getElementById('notificationCount').textContent = unreadCount;
        }
    } catch (error) {
        console.error('خطأ في تحميل الإشعارات:', error);
    }
}

// قسم النسخ الاحتياطي
function showBackupSection() {
    const container = document.getElementById('backupContent');
    container.innerHTML = `
        <div class="backup-section">
            <div class="card">
                <h3>نسخ احتياطي لقاعدة البيانات</h3>
                <p>قم بإنشاء نسخة احتياطية من جميع البيانات بصيغة Excel</p>
                <button class="btn-primary" onclick="createBackup()">
                    <i class="fas fa-download"></i> إنشاء نسخة احتياطية
                </button>
            </div>
            
            <div class="card">
                <h3>النسخ الاحتياطية السابقة</h3>
                <div id="backupList">
                    جاري تحميل النسخ الاحتياطية...
                </div>
            </div>
        </div>
    `;
    
    loadBackups();
}

// إنشاء نسخة احتياطية
async function createBackup() {
    try {
        const response = await fetch('/api/admin/backup', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('تم إنشاء النسخة الاحتياطية بنجاح');
            loadBackups();
            
            // تحميل الملف
            const link = document.createElement('a');
            link.href = data.downloadUrl;
            link.download = data.fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    } catch (error) {
        console.error('خطأ في إنشاء النسخة الاحتياطية:', error);
        alert('حدث خطأ أثناء إنشاء النسخة الاحتياطية');
    }
}

// تحميل النسخ الاحتياطية
async function loadBackups() {
    try {
        const response = await fetch('/api/admin/backups', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderBackups(data.backups);
        }
    } catch (error) {
        console.error('خطأ في تحميل النسخ الاحتياطية:', error);
    }
}

// الدوال المساعدة
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// تسجيل الخروج
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// التعامل مع الأخطاء
function handleApiError(error) {
    console.error('خطأ في API:', error);
    if (error.status === 401) {
        alert('انتهت الجلسة، يرجى تسجيل الدخول مرة أخرى');
        logout();
    }
}

// تحميل المستخدمين
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderUsers(data.users);
        }
    } catch (error) {
        console.error('خطأ في تحميل المستخدمين:', error);
    }
}

// تحميل الطلبات
async function loadOrders() {
    try {
        const response = await fetch('/api/admin/orders', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderOrders(data.orders);
        }
    } catch (error) {
        console.error('خطأ في تحميل الطلبات:', error);
    }
}

// معالجة طلبات الدفع اليدوية
async function processManualPayment(orderId, status) {
    try {
        const response = await fetch(`/api/admin/orders/${orderId}/payment`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ status })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`تم ${status === 'confirmed' ? 'تأكيد' : 'رفض'} الدفع`);
            loadOrders();
        }
    } catch (error) {
        console.error('خطأ في معالجة الدفع:', error);
        alert('حدث خطأ أثناء معالجة الدفع');
    }
}
