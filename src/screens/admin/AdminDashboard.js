// src/screens/admin/AdminDashboard.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { logout } from '../../store/actions/authActions';

const AdminDashboard = ({ navigation }) => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalSellers: 0,
    totalDrivers: 0,
    totalWashers: 0,
    totalOrders: 0,
    pendingOrders: 0,
    totalRevenue: 0,
    todayRevenue: 0,
    pendingWithdrawals: 0,
    activeAds: 0,
  });
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // محاكاة جلب البيانات
      setTimeout(() => {
        setStats({
          totalUsers: 1248,
          totalSellers: 156,
          totalDrivers: 28,
          totalWashers: 15,
          totalOrders: 2847,
          pendingOrders: 23,
          totalRevenue: 124500,
          todayRevenue: 3250,
          pendingWithdrawals: 8,
          activeAds: 12,
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في تحميل البيانات');
      setLoading(false);
    }
  };

  const adminActions = [
    {
      title: 'إدارة المستخدمين',
      icon: 'account-group',
      screen: 'UsersManagement',
      color: '#2196F3',
      description: 'عرض وتعديل وحذف حسابات المستخدمين',
    },
    {
      title: 'إدارة البائعين',
      icon: 'store',
      screen: 'SellersManagement',
      color: '#4CAF50',
      description: 'التحقق من البائعين وإدارة متاجرهم',
    },
    {
      title: 'إدارة الطلبات',
      icon: 'clipboard-list',
      screen: 'OrdersManagement',
      color: '#FF9800',
      description: 'متابعة جميع الطلبات وتغيير حالتها',
    },
    {
      title: 'إدارة الأسواق',
      icon: 'storefront',
      screen: 'MarketsManagement',
      color: '#9C27B0',
      description: 'إضافة وتعديل وحذف الأسواق',
    },
    {
      title: 'إدارة المغاسل',
      icon: 'water',
      screen: 'WashingShopsManagement',
      color: '#00BCD4',
      description: 'إدارة مغاسل القات في الأسواق',
    },
    {
      title: 'إدارة المندوبين',
      icon: 'truck-delivery',
      screen: 'DriversManagement',
      color: '#795548',
      description: 'تسجيل وتوزيع المندوبين',
    },
    {
      title: 'الإعلانات',
      icon: 'bullhorn',
      screen: 'AdsManagement',
      color: '#E91E63',
      description: 'إنشاء وإدارة الإعلانات',
    },
    {
      title: 'الباقات الإعلانية',
      icon: 'package-variant',
      screen: 'AdPackages',
      color: '#FF5722',
      description: 'تصميم باقات إعلانية للبائعين',
    },
    {
      title: 'التحويلات',
      icon: 'bank-transfer',
      screen: 'TransfersManagement',
      color: '#607D8B',
      description: 'متابعة طلبات سحب الأموال',
    },
    {
      title: 'الكروت الهدايا',
      icon: 'gift',
      screen: 'GiftCards',
      color: '#9C27B0',
      description: 'إنشاء وإدارة كروت الهدايا',
    },
    {
      title: 'الإحصائيات',
      icon: 'chart-bar',
      screen: 'Statistics',
      color: '#3F51B5',
      description: 'تقارير وإحصائيات مفصلة',
    },
    {
      title: 'إعدادات النظام',
      icon: 'cog',
      screen: 'Settings',
      color: '#666',
      description: 'تخصيص إعدادات التطبيق',
    },
  ];

  const handleLogout = () => {
    Alert.alert(
      'تأكيد',
      'هل أنت متأكد من تسجيل الخروج؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'نعم',
          onPress: () => {
            dispatch(logout());
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  const renderStatCard = (title, value, icon, color) => (
    <View style={styles.statCard}>
      <View style={[styles.statIcon, { backgroundColor: `${color}20` }]}>
        <Icon name={icon} size={24} color={color} />
      </View>
      <Text style={styles.statValue}>{value.toLocaleString()}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.userInfo}>
            <Icon name="shield-account" size={30} color="#2E7D32" />
            <View style={styles.userText}>
              <Text style={styles.welcomeText}>مدير النظام</Text>
              <Text style={styles.userName}>{user?.name}</Text>
            </View>
          </View>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Icon name="logout" size={24} color="#D32F2F" />
            <Text style={styles.logoutText}>خروج</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>نظرة سريعة</Text>
        {loading ? (
          <ActivityIndicator size="large" color="#2E7D32" style={styles.loader} />
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.statsScroll}>
            <View style={styles.statsRow}>
              {renderStatCard('المستخدمين', stats.totalUsers, 'account', '#2196F3')}
              {renderStatCard('البائعين', stats.totalSellers, 'store', '#4CAF50')}
              {renderStatCard('الطلبات', stats.totalOrders, 'clipboard-check', '#FF9800')}
              {renderStatCard('الإيرادات', stats.totalRevenue, 'cash', '#2E7D32')}
            </View>
          </ScrollView>
        )}
      </View>

      {/* Today's Stats */}
      <View style={styles.todayStats}>
        <Text style={styles.sectionTitle}>إحصائيات اليوم</Text>
        <View style={styles.todayStatsGrid}>
          <View style={styles.todayStat}>
            <Icon name="currency-usd" size={20} color="#4CAF50" />
            <Text style={styles.todayStatValue}>{stats.todayRevenue.toLocaleString()} ريال</Text>
            <Text style={styles.todayStatLabel}>إيرادات اليوم</Text>
          </View>
          <View style={styles.todayStat}>
            <Icon name="clock" size={20} color="#FF9800" />
            <Text style={styles.todayStatValue}>{stats.pendingOrders}</Text>
            <Text style={styles.todayStatLabel}>طلبات قيد الانتظار</Text>
          </View>
          <View style={styles.todayStat}>
            <Icon name="alert-circle" size={20} color="#D32F2F" />
            <Text style={styles.todayStatValue}>{stats.pendingWithdrawals}</Text>
            <Text style={styles.todayStatLabel}>طلبات سحب</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsSection}>
        <Text style={styles.sectionTitle}>الإجراءات السريعة</Text>
        <View style={styles.quickActions}>
          <TouchableOpacity 
            style={[styles.quickAction, { backgroundColor: '#4CAF50' }]}
            onPress={() => navigation.navigate('UsersManagement')}
          >
            <Icon name="account-plus" size={24} color="#fff" />
            <Text style={styles.quickActionText}>إضافة مستخدم</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.quickAction, { backgroundColor: '#2196F3' }]}
            onPress={() => navigation.navigate('AdsManagement')}
          >
            <Icon name="bullhorn" size={24} color="#fff" />
            <Text style={styles.quickActionText}>إعلان جديد</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.quickAction, { backgroundColor: '#9C27B0' }]}
            onPress={() => navigation.navigate('TransfersManagement')}
          >
            <Icon name="bank-transfer" size={24} color="#fff" />
            <Text style={styles.quickActionText}>التحويلات</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.quickAction, { backgroundColor: '#FF5722' }]}
            onPress={() => navigation.navigate('Settings')}
          >
            <Icon name="cog" size={24} color="#fff" />
            <Text style={styles.quickActionText}>الإعدادات</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* All Admin Features */}
      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>جميع الميزات الإدارية</Text>
        <View style={styles.featuresGrid}>
          {adminActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={styles.featureCard}
              onPress={() => navigation.navigate(action.screen)}
            >
              <View style={[styles.featureIcon, { backgroundColor: action.color }]}>
                <Icon name={action.icon} size={24} color="#fff" />
              </View>
              <Text style={styles.featureTitle}>{action.title}</Text>
              <Text style={styles.featureDescription}>{action.description}</Text>
              <View style={styles.featureArrow}>
                <Icon name="chevron-left" size={20} color="#666" />
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Activities */}
      <View style={styles.activitiesSection}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>أحدث الأنشطة</Text>
          <TouchableOpacity>
            <Text style={styles.seeAllText}>عرض الكل</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.activitiesList}>
          {[
            { id: 1, text: 'تم تسجيل بائع جديد: أحمد محمد', time: 'قبل 5 دقائق' },
            { id: 2, text: 'تم إنشاء طلب جديد #2847', time: 'قبل 15 دقيقة' },
            { id: 3, text: 'تم سحب رصيد بقيمة 500 ريال', time: 'قبل 30 دقيقة' },
            { id: 4, text: 'تم إضافة إعلان جديد', time: 'قبل ساعة' },
          ].map((activity) => (
            <View key={activity.id} style={styles.activityItem}>
              <View style={styles.activityDot} />
              <View style={styles.activityContent}>
                <Text style={styles.activityText}>{activity.text}</Text>
                <Text style={styles.activityTime}>{activity.time}</Text>
              </View>
            </View>
          ))}
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
    backgroundColor: '#fff',
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userText: {
    marginRight: 10,
  },
  welcomeText: {
    color: '#666',
    fontSize: 12,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 2,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
  },
  logoutText: {
    color: '#D32F2F',
    marginRight: 5,
    fontSize: 12,
  },
  statsSection: {
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  loader: {
    padding: 30,
  },
  statsScroll: {
    flexDirection: 'row',
  },
  statsRow: {
    flexDirection: 'row',
  },
  statCard: {
    alignItems: 'center',
    padding: 15,
    marginRight: 10,
    minWidth: 120,
  },
  statIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  statValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  statTitle: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
  },
  todayStats: {
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10,
  },
  todayStatsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  todayStat: {
    alignItems: 'center',
    flex: 1,
    padding: 10,
  },
  todayStatValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 5,
    marginBottom: 2,
  },
  todayStatLabel: {
    color: '#666',
    fontSize: 11,
    textAlign: 'center',
  },
  actionsSection: {
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10,
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    width: '48%',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10,
  },
  quickActionText: {
    color: '#fff',
    fontWeight: 'bold',
    marginTop: 5,
    fontSize: 12,
  },
  featuresSection: {
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  featureCard: {
    width: '48%',
    backgroundColor: '#F9F9F9',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    position: 'relative',
  },
  featureIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  featureTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  featureDescription: {
    color: '#666',
    fontSize: 10,
    lineHeight: 14,
    marginBottom: 10,
  },
  featureArrow: {
    position: 'absolute',
    left: 10,
    bottom: 10,
  },
  activitiesSection: {
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10,
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  seeAllText: {
    color: '#2E7D32',
    fontSize: 12,
  },
  activitiesList: {
    backgroundColor: '#F9F9F9',
    borderRadius: 10,
    padding: 15,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#2E7D32',
    marginTop: 5,
    marginLeft: 10,
  },
  activityContent: {
    flex: 1,
  },
  activityText: {
    color: '#333',
    fontSize: 13,
    marginBottom: 2,
  },
  activityTime: {
    color: '#666',
    fontSize: 10,
  },
});

export default AdminDashboard;
