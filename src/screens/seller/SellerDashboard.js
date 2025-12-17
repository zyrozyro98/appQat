// src/screens/seller/SellerDashboard.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const SellerDashboard = ({ navigation }) => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    pendingOrders: 0,
    totalEarnings: 0,
    todayEarnings: 0,
  });
  const [recentOrders, setRecentOrders] = useState([]);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    loadSellerData();
  }, []);

  const loadSellerData = async () => {
    // جلب بيانات البائع
    setStats({
      totalProducts: 15,
      totalOrders: 48,
      pendingOrders: 3,
      totalEarnings: 12500,
      todayEarnings: 350,
    });

    setRecentOrders([
      {
        id: 1,
        customer: 'محمد أحمد',
        amount: 145,
        status: 'pending',
        time: '10:30',
        requiresWashing: true,
      },
      // ... طلبات أخرى
    ]);
  };

  const quickActions = [
    {
      title: 'إضافة منتج',
      icon: 'plus-circle',
      screen: 'AddProduct',
      color: '#2E7D32',
    },
    {
      title: 'الطلبات',
      icon: 'clipboard-list',
      screen: 'SellerOrders',
      color: '#2196F3',
    },
    {
      title: 'المحفظة',
      icon: 'wallet',
      screen: 'SellerWallet',
      color: '#FF9800',
    },
    {
      title: 'الإحصائيات',
      icon: 'chart-bar',
      screen: 'SellerStats',
      color: '#9C27B0',
    },
    {
      title: 'تقييمات',
      icon: 'star',
      screen: 'SellerReviews',
      color: '#FFC107',
    },
    {
      title: 'الإعلانات',
      icon: 'bullhorn',
      screen: 'SellerAds',
      color: '#E91E63',
    },
  ];

  const renderOrderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.orderCard}
      onPress={() => navigation.navigate('OrderDetails', { orderId: item.id })}
    >
      <View style={styles.orderHeader}>
        <Text style={styles.orderCustomer}>{item.customer}</Text>
        <View style={styles.orderStatus}>
          <Text style={[
            styles.statusText,
            item.status === 'pending' && styles.statusPending,
            item.status === 'preparing' && styles.statusPreparing,
            item.status === 'delivered' && styles.statusDelivered,
          ]}>
            {getStatusText(item.status)}
          </Text>
        </View>
      </View>
      
      <View style={styles.orderDetails}>
        <Text style={styles.orderAmount}>{item.amount} ريال</Text>
        <Text style={styles.orderTime}>{item.time}</Text>
        {item.requiresWashing && (
          <View style={styles.washingIndicator}>
            <Icon name="water" size={14} color="#2196F3" />
            <Text style={styles.washingText}>مع الغسل</Text>
          </View>
        )}
      </View>
      
      <TouchableOpacity style={styles.orderAction}>
        <Text style={styles.orderActionText}>عرض التفاصيل</Text>
        <Icon name="chevron-left" size={16} color="#2E7D32" />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const getStatusText = (status) => {
    const statusMap = {
      pending: 'قيد الانتظار',
      preparing: 'قيد التحضير',
      washing: 'في المغسلة',
      delivering: 'قيد التوصيل',
      delivered: 'تم التوصيل',
    };
    return statusMap[status] || status;
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.userInfo}>
          <Text style={styles.welcomeText}>مرحباً بك،</Text>
          <Text style={styles.userName}>{user?.name}</Text>
          <Text style={styles.storeName}>متجر: {user?.storeName}</Text>
        </View>
        <TouchableOpacity style={styles.notificationButton}>
          <Icon name="bell" size={24} color="#333" />
          <View style={styles.notificationBadge}>
            <Text style={styles.notificationCount}>3</Text>
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Icon name="package-variant" size={24} color="#2E7D32" />
          <Text style={styles.statNumber}>{stats.totalProducts}</Text>
          <Text style={styles.statLabel}>المنتجات</Text>
        </View>
        
        <View style={styles.statCard}>
          <Icon name="clipboard-check" size={24} color="#2196F3" />
          <Text style={styles.statNumber}>{stats.totalOrders}</Text>
          <Text style={styles.statLabel}>الطلبات</Text>
        </View>
        
        <View style={styles.statCard}>
          <Icon name="clock" size={24} color="#FF9800" />
          <Text style={styles.statNumber}>{stats.pendingOrders}</Text>
          <Text style={styles.statLabel}>قيد الانتظار</Text>
        </View>
        
        <View style={styles.statCard}>
          <Icon name="cash" size={24} color="#4CAF50" />
          <Text style={styles.statNumber}>{stats.todayEarnings}</Text>
          <Text style={styles.statLabel}>مبيعات اليوم</Text>
        </View>
      </View>

      <View style={styles.balanceCard}>
        <View style={styles.balanceInfo}>
          <Text style={styles.balanceLabel}>إجمالي الأرباح</Text>
          <Text style={styles.balanceAmount}>{stats.totalEarnings} ريال</Text>
        </View>
        <TouchableOpacity style={styles.withdrawButton}>
          <Text style={styles.withdrawButtonText}>سحب الأرباح</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>الطلبات الحديثة</Text>
          <TouchableOpacity onPress={() => navigation.navigate('SellerOrders')}>
            <Text style={styles.seeAllText}>عرض الكل</Text>
          </TouchableOpacity>
        </View>
        <FlatList
          data={recentOrders}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderOrderItem}
          horizontal
          showsHorizontalScrollIndicator={false}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>الإجراءات السريعة</Text>
        <View style={styles.quickActionsGrid}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={styles.quickActionButton}
              onPress={() => navigation.navigate(action.screen)}
            >
              <View style={[styles.actionIcon, { backgroundColor: action.color }]}>
                <Icon name={action.icon} size={24} color="#fff" />
              </View>
              <Text style={styles.actionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.marketSection}>
        <Text style={styles.sectionTitle}>الأسواق المتاحة</Text>
        <View style={styles.marketsList}>
          <View style={styles.marketItem}>
            <Icon name="storefront" size={20} color="#2E7D32" />
            <Text style={styles.marketName}>سوق التحرير</Text>
            <Text style={styles.marketStatus}>نشط</Text>
          </View>
          <View style={styles.marketItem}>
            <Icon name="storefront" size={20} color="#2E7D32" />
            <Text style={styles.marketName}>سوق الثورة</Text>
            <Text style={styles.marketStatus}>نشط</Text>
          </View>
          <View style={styles.marketItem}>
            <Icon name="storefront" size={20} color="#2E7D32" />
            <Text style={styles.marketName}>سوق الحديدة</Text>
            <Text style={styles.marketStatus}>متوقف</Text>
          </View>
        </View>
      </View>
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
  userInfo: {
    flex: 1,
  },
  welcomeText: {
    color: '#666',
    fontSize: 14,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 2,
  },
  storeName: {
    color: '#2E7D32',
    fontSize: 12,
    marginTop: 2,
  },
  notificationButton: {
    padding: 5,
    position: 'relative',
  },
  notificationBadge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: '#D32F2F',
    borderRadius: 10,
    width: 16,
    height: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationCount: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    margin: '1%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  statLabel: {
    color: '#666',
    marginTop: 5,
  },
  balanceCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  balanceInfo: {
    flex: 1,
  },
  balanceLabel: {
    color: '#666',
    fontSize: 14,
  },
  balanceAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginTop: 5,
  },
  withdrawButton: {
    backgroundColor: '#2E7D32',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  withdrawButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 10,
    padding: 15,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  seeAllText: {
    color: '#2E7D32',
    fontSize: 14,
  },
  orderCard: {
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    padding: 15,
    marginRight: 10,
    width: 250,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  orderCustomer: {
    fontWeight: 'bold',
    color: '#333',
    fontSize: 14,
  },
  orderStatus: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    backgroundColor: '#FFF3CD',
  },
  statusText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  statusPending: {
    color: '#856404',
  },
  statusPreparing: {
    color: '#0C5460',
  },
  statusDelivered: {
    color: '#155724',
  },
  orderDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  orderAmount: {
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  orderTime: {
    color: '#666',
    fontSize: 12,
  },
  washingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  washingText: {
    color: '#2196F3',
    fontSize: 10,
    marginRight: 5,
  },
  orderAction: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  orderActionText: {
    color: '#2E7D32',
    fontSize: 12,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    width: '48%',
    backgroundColor: '#F9F9F9',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
  },
  actionIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  actionTitle: {
    color: '#333',
    fontWeight: '500',
  },
  marketSection: {
    backgroundColor: '#fff',
    marginTop: 10,
    padding: 15,
    marginBottom: 20,
  },
  marketsList: {
    marginTop: 10,
  },
  marketItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    marginBottom: 8,
  },
  marketName: {
    flex: 1,
    marginRight: 10,
    color: '#333',
  },
  marketStatus: {
    color: '#2E7D32',
    fontSize: 12,
    fontWeight: '500',
  },
});

export default SellerDashboard;
