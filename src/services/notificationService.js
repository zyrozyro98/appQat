// src/services/notificationService.js
import * as Notifications from 'expo-notifications';
import api from './api';

export const notificationService = {
  // تسجيل الجهاز للحصول على الإشعارات
  registerDevice: async (userId) => {
    const { status } = await Notifications.requestPermissionsAsync();
    
    if (status !== 'granted') {
      throw new Error('Permission denied for notifications');
    }

    const token = (await Notifications.getExpoPushTokenAsync()).data;
    
    // حفظ التوكن في الخادم
    await api.post('/notifications/register-device', {
      userId,
      deviceToken: token,
      platform: Platform.OS,
    });
    
    return token;
  },

  // إرسال إشعار محلي
  sendLocalNotification: async (title, body, data = {}) => {
    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
        sound: true,
        vibrate: [0, 250, 250, 250],
      },
      trigger: null, // إرسال فوري
    });
  },

  // إعداد معالج الإشعارات
  setupNotificationHandler: () => {
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
      }),
    });

    // معالج عند استقبال الإشعار
    Notifications.addNotificationReceivedListener((notification) => {
      console.log('Notification received:', notification);
    });

    // معالج عند النقر على الإشعار
    Notifications.addNotificationResponseReceivedListener((response) => {
      const data = response.notification.request.content.data;
      console.log('Notification clicked:', data);
      // معالجة البيانات والتنقل للشاشة المناسبة
    });
  },

  // إرسال إشعارات العملية الكاملة
  sendOrderNotifications: async (orderData) => {
    const { orderId, sellerId, washerId, driverId, adminId, saleCode } = orderData;

    // إشعار البائع
    await api.post('/notifications/send', {
      userId: sellerId,
      title: 'طلب جديد!',
      body: `تم استلام طلب جديد برمز ${saleCode}`,
      data: { type: 'new_order', orderId },
    });

    // إشعار مغسلة القات
    await api.post('/notifications/send', {
      userId: washerId,
      title: 'طلب جديد للغسل',
      body: `يوجد طلب جديد للغسل برمز ${saleCode}`,
      data: { type: 'washing_order', orderId },
    });

    // إشعار مندوب التوصيل
    await api.post('/notifications/send', {
      userId: driverId,
      title: 'مهمة توصيل جديدة',
      body: `لديك طلب جديد للتوصيل برمز ${saleCode}`,
      data: { type: 'delivery_order', orderId },
    });

    // إشعار المدير
    await api.post('/notifications/send', {
      userId: adminId,
      title: 'تقرير مبيعات',
      body: `تم إتمام عملية بيع جديدة برمز ${saleCode}`,
      data: { type: 'sale_report', orderId },
    });

    // إشعار المشتري
    await this.sendLocalNotification(
      'تم تأكيد طلبك!',
      `تم تأكيد طلبك بنجاح. رمز البيع: ${saleCode}`,
      { type: 'order_confirmed', orderId }
    );
  },
};

// أنواع الإشعارات
export const NOTIFICATION_TYPES = {
  NEW_ORDER: 'new_order',
  ORDER_STATUS_CHANGED: 'order_status_changed',
  PAYMENT_RECEIVED: 'payment_received',
  WITHDRAWAL_REQUEST: 'withdrawal_request',
  AD_APPROVED: 'ad_approved',
  LOW_BALANCE: 'low_balance',
  NEW_MESSAGE: 'new_message',
  RATING_RECEIVED: 'rating_received',
  DRIVER_ASSIGNED: 'driver_assigned',
  ORDER_DELIVERED: 'order_delivered',
};
