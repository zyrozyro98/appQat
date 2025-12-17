// src/screens/buyer/CheckoutScreen.js
import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { clearCart } from '../../store/actions/cartActions';
import { updateBalance } from '../../store/actions/authActions';

const CheckoutScreen = ({ navigation, route }) => {
  const { total } = route.params;
  const { items } = useSelector((state) => state.cart);
  const { user } = useSelector((state) => state.auth);
  const [address, setAddress] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('balance');
  const [deliveryTime, setDeliveryTime] = useState('asap');
  const dispatch = useDispatch();

  const paymentMethods = [
    { id: 'balance', name: 'رصيد الحساب', icon: 'wallet' },
    { id: 'jib', name: 'محفظة جيب', icon: 'cellphone' },
    { id: 'jawaly', name: 'محفظة جوالي', icon: 'cellphone' },
    { id: 'mobi', name: 'محفظة موبايل موني', icon: 'cellphone' },
    { id: 'shamel', name: 'محفظة الشامل موني', icon: 'cellphone' },
    { id: 'fuloos', name: 'محفظة فلوسك', icon: 'cellphone' },
  ];

  const deliveryTimes = [
    { id: 'asap', name: 'أسرع وقت ممكن' },
    { id: '30min', name: 'خلال 30 دقيقة' },
    { id: '1hour', name: 'خلال ساعة' },
    { id: '2hour', name: 'خلال ساعتين' },
  ];

  const handlePlaceOrder = async () => {
    if (!address.trim()) {
      Alert.alert('خطأ', 'يرجى إدخال عنوان التوصيل');
      return;
    }

    try {
      // إنشاء الطلب
      const orderData = {
        userId: user.id,
        items,
        total: total + 10, // + رسوم التوصيل
        address,
        paymentMethod,
        deliveryTime,
        requiresWashing: items.some(item => item.requiresWashing),
      };

      // خصم المبلغ من رصيد المشتري
      if (paymentMethod === 'balance') {
        const newBalance = user.balance - (total + 10);
        dispatch(updateBalance(newBalance));
      }

      // إضافة المبلغ إلى حساب البائع
      // إرسال الإشعارات
      
      // تفريغ السلة
      dispatch(clearCart());

      // إنشاء رمز البيع
      const saleCode = generateSaleCode();

      Alert.alert(
        'تم إنشاء الطلب',
        `تم إنشاء طلبك بنجاح!\n\nرمز البيع: ${saleCode}\nسيتم توصيل الطلب خلال ${getDeliveryTimeText(deliveryTime)}`,
        [
          {
            text: 'موافق',
            onPress: () => {
              // إرسال الإشعارات
              sendNotifications(orderData, saleCode);
              navigation.navigate('Orders');
            },
          },
        ]
      );

    } catch (error) {
      Alert.alert('خطأ', 'فشل في إنشاء الطلب');
    }
  };

  const generateSaleCode = () => {
    return 'QAT-' + Math.random().toString(36).substr(2, 8).toUpperCase();
  };

  const getDeliveryTimeText = (timeId) => {
    const time = deliveryTimes.find(t => t.id === timeId);
    return time ? time.name : 'أسرع وقت ممكن';
  };

  const sendNotifications = (orderData, saleCode) => {
    // إشعار البائع
    // إشعار مغسلة القات
    // إشعار مندوب التوصيل
    // إشعار المدير
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-right" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>إتمام الشراء</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>عنوان التوصيل</Text>
        <View style={styles.inputContainer}>
          <Icon name="map-marker" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="أدخل العنوان الكامل"
            value={address}
            onChangeText={setAddress}
            multiline
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>وقت التوصيل</Text>
        <View style={styles.deliveryTimes}>
          {deliveryTimes.map((time) => (
            <TouchableOpacity
              key={time.id}
              style={[
                styles.deliveryTimeButton,
                deliveryTime === time.id && styles.deliveryTimeButtonActive,
              ]}
              onPress={() => setDeliveryTime(time.id)}
            >
              <Text
                style={[
                  styles.deliveryTimeText,
                  deliveryTime === time.id && styles.deliveryTimeTextActive,
                ]}
              >
                {time.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>طريقة الدفع</Text>
        <View style={styles.paymentMethods}>
          {paymentMethods.map((method) => (
            <TouchableOpacity
              key={method.id}
              style={[
                styles.paymentMethodButton,
                paymentMethod === method.id && styles.paymentMethodButtonActive,
              ]}
              onPress={() => setPaymentMethod(method.id)}
            >
              <Icon
                name={method.icon}
                size={20}
                color={paymentMethod === method.id ? '#fff' : '#666'}
              />
              <Text
                style={[
                  styles.paymentMethodText,
                  paymentMethod === method.id && styles.paymentMethodTextActive,
                ]}
              >
                {method.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>ملخص الطلب</Text>
        <View style={styles.orderSummary}>
          {items.map((item) => (
            <View key={item.id} style={styles.orderItem}>
              <Text style={styles.orderItemName}>{item.name}</Text>
              <Text style={styles.orderItemPrice}>
                {item.quantity} × {item.finalPrice} ريال
              </Text>
            </View>
          ))}
          
          <View style={styles.orderTotal}>
            <Text style={styles.orderTotalLabel}>المجموع:</Text>
            <Text style={styles.orderTotalValue}>{total} ريال</Text>
          </View>
          
          <View style={styles.orderTotal}>
            <Text style={styles.orderTotalLabel}>رسوم التوصيل:</Text>
            <Text style={styles.orderTotalValue}>10 ريال</Text>
          </View>
          
          <View style={[styles.orderTotal, styles.grandTotal]}>
            <Text style={styles.grandTotalLabel}>المجموع الكلي:</Text>
            <Text style={styles.grandTotalValue}>{total + 10} ريال</Text>
          </View>
        </View>
      </View>

      <View style={styles.noteSection}>
        <Icon name="information" size={20} color="#FF9800" />
        <Text style={styles.noteText}>
          بعد تأكيد الطلب:
          {'\n'}• سيتم خصم المبلغ من رصيدك
          {'\n'}• سيصل إشعار للبائع ومغسلة القات
          {'\n'}• سيتم إنشاء رمز بيع لتتبع الطلب
          {'\n'}• سيتم تعيين مندوب توصيل تلقائياً
        </Text>
      </View>

      <TouchableOpacity style={styles.confirmButton} onPress={handlePlaceOrder}>
        <Text style={styles.confirmButtonText}>تأكيد الطلب</Text>
        <Icon name="check-circle" size={20} color="#fff" />
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  section: {
    backgroundColor: '#fff',
    marginBottom: 10,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 15,
  },
  inputIcon: {
    marginLeft: 10,
  },
  input: {
    flex: 1,
    height: 100,
    textAlignVertical: 'top',
    textAlign: 'right',
  },
  deliveryTimes: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  deliveryTimeButton: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginRight: 10,
    marginBottom: 10,
  },
  deliveryTimeButtonActive: {
    borderColor: '#2E7D32',
    backgroundColor: '#E8F5E8',
  },
  deliveryTimeText: {
    color: '#666',
  },
  deliveryTimeTextActive: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  paymentMethods: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  paymentMethodButton: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginRight: 10,
    marginBottom: 10,
  },
  paymentMethodButtonActive: {
    borderColor: '#2E7D32',
    backgroundColor: '#2E7D32',
  },
  paymentMethodText: {
    marginRight: 5,
    color: '#666',
  },
  paymentMethodTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  orderSummary: {
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    padding: 15,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  orderItemName: {
    color: '#333',
    flex: 1,
    marginRight: 10,
  },
  orderItemPrice: {
    color: '#2E7D32',
    fontWeight: '500',
  },
  orderTotal: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 5,
  },
  orderTotalLabel: {
    color: '#666',
  },
  orderTotalValue: {
    color: '#333',
    fontWeight: '500',
  },
  grandTotal: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  grandTotalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  grandTotalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  noteSection: {
    flexDirection: 'row',
    backgroundColor: '#FFF3E0',
    padding: 15,
    margin: 20,
    borderRadius: 8,
  },
  noteText: {
    flex: 1,
    marginRight: 10,
    color: '#666',
    fontSize: 12,
    lineHeight: 18,
  },
  confirmButton: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    margin: 20,
    borderRadius: 8,
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});

export default CheckoutScreen;
