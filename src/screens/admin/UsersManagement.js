// src/screens/admin/UsersManagement.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  TextInput,
  Alert,
  Modal,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Picker } from '@react-native-picker/picker';

const UsersManagement = ({ navigation }) => {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUserType, setSelectedUserType] = useState('all');
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userForm, setUserForm] = useState({
    name: '',
    email: '',
    phone: '',
    userType: 'buyer',
    status: 'active',
    balance: '0',
  });

  const userTypes = [
    { label: 'الكل', value: 'all' },
    { label: 'مشتري', value: 'buyer' },
    { label: 'بائع', value: 'seller' },
    { label: 'مندوب توصيل', value: 'driver' },
    { label: 'مغسلة قات', value: 'washer' },
    { label: 'مدير', value: 'admin' },
  ];

  const statusOptions = [
    { label: 'نشط', value: 'active' },
    { label: 'موقوف', value: 'suspended' },
    { label: 'محظور', value: 'banned' },
    { label: 'غير مفعل', value: 'inactive' },
  ];

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [searchQuery, selectedUserType]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      // محاكاة جلب البيانات
      const mockUsers = [
        {
          id: 1,
          name: 'محمد أحمد',
          email: 'mohamed@example.com',
          phone: '771234567',
          userType: 'buyer',
          status: 'active',
          balance: 1500,
          createdAt: '2024-01-15',
          ordersCount: 12,
        },
        // ... مستخدمين آخرين
      ];
      setUsers(mockUsers);
      setFilteredUsers(mockUsers);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في تحميل المستخدمين');
    } finally {
      setLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    if (searchQuery) {
      filtered = filtered.filter(
        (user) =>
          user.name.includes(searchQuery) ||
          user.email.includes(searchQuery) ||
          user.phone.includes(searchQuery)
      );
    }

    if (selectedUserType !== 'all') {
      filtered = filtered.filter((user) => user.userType === selectedUserType);
    }

    setFilteredUsers(filtered);
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setUserForm({
      name: user.name,
      email: user.email,
      phone: user.phone,
      userType: user.userType,
      status: user.status,
      balance: user.balance.toString(),
    });
    setModalVisible(true);
  };

  const handleSaveUser = async () => {
    // حفظ بيانات المستخدم
    Alert.alert('نجاح', 'تم تحديث بيانات المستخدم');
    setModalVisible(false);
    loadUsers();
  };

  const handleDeleteUser = (userId) => {
    Alert.alert(
      'تأكيد الحذف',
      'هل أنت متأكد من حذف هذا المستخدم؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حذف',
          style: 'destructive',
          onPress: async () => {
            // حذف المستخدم
            Alert.alert('نجاح', 'تم حذف المستخدم');
            loadUsers();
          },
        },
      ]
    );
  };

  const handleAddFunds = (userId) => {
    Alert.prompt(
      'إضافة رصيد',
      'أدخل المبلغ المراد إضافته:',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'إضافة',
          onPress: (amount) => {
            if (amount && !isNaN(amount)) {
              // إضافة الرصيد
              Alert.alert('نجاح', `تم إضافة ${amount} ريال`);
            }
          },
        },
      ],
      'plain-text',
      '',
      'numeric'
    );
  };

  const renderUserItem = ({ item }) => (
    <View style={styles.userCard}>
      <View style={styles.userHeader}>
        <View style={styles.userInfo}>
          <Text style={styles.userName}>{item.name}</Text>
          <View style={styles.userMeta}>
            <Text style={styles.userEmail}>{item.email}</Text>
            <Text style={styles.userPhone}>{item.phone}</Text>
          </View>
        </View>
        <View style={styles.userTypeBadge}>
          <Text style={styles.userTypeText}>{getUserTypeLabel(item.userType)}</Text>
        </View>
      </View>

      <View style={styles.userDetails}>
        <View style={styles.detailItem}>
          <Icon name="calendar" size={14} color="#666" />
          <Text style={styles.detailText}>التسجيل: {item.createdAt}</Text>
        </View>
        <View style={styles.detailItem}>
          <Icon name="clipboard-check" size={14} color="#666" />
          <Text style={styles.detailText}>الطلبات: {item.ordersCount}</Text>
        </View>
        <View style={styles.detailItem}>
          <Icon name="wallet" size={14} color="#666" />
          <Text style={styles.detailText}>الرصيد: {item.balance} ريال</Text>
        </View>
      </View>

      <View style={styles.userStatus}>
        <View style={[styles.statusBadge, getStatusStyle(item.status)]}>
          <Text style={styles.statusText}>{getStatusLabel(item.status)}</Text>
        </View>
      </View>

      <View style={styles.userActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => openEditModal(item)}
        >
          <Icon name="pencil" size={18} color="#2196F3" />
          <Text style={styles.actionText}>تعديل</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => handleAddFunds(item.id)}
        >
          <Icon name="cash-plus" size={18} color="#4CAF50" />
          <Text style={styles.actionText}>إضافة رصيد</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('UserOrders', { userId: item.id })}
        >
          <Icon name="clipboard-list" size={18} color="#FF9800" />
          <Text style={styles.actionText}>الطلبات</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => handleDeleteUser(item.id)}
        >
          <Icon name="delete" size={18} color="#D32F2F" />
          <Text style={styles.actionText}>حذف</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const getUserTypeLabel = (type) => {
    const typeMap = {
      buyer: 'مشتري',
      seller: 'بائع',
      driver: 'مندوب',
      washer: 'مغسلة',
      admin: 'مدير',
    };
    return typeMap[type] || type;
  };

  const getStatusLabel = (status) => {
    const statusMap = {
      active: 'نشط',
      suspended: 'موقوف',
      banned: 'محظور',
      inactive: 'غير مفعل',
    };
    return statusMap[status] || status;
  };

  const getStatusStyle = (status) => {
    switch (status) {
      case 'active':
        return { backgroundColor: '#4CAF50' };
      case 'suspended':
        return { backgroundColor: '#FF9800' };
      case 'banned':
        return { backgroundColor: '#D32F2F' };
      case 'inactive':
        return { backgroundColor: '#666' };
      default:
        return { backgroundColor: '#666' };
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-right" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>إدارة المستخدمين</Text>
        <TouchableOpacity onPress={() => setModalVisible(true)}>
          <Icon name="account-plus" size={24} color="#2E7D32" />
        </TouchableOpacity>
      </View>

      <View style={styles.filterSection}>
        <View style={styles.searchContainer}>
          <Icon name="magnify" size={20} color="#666" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="بحث باسم أو بريد أو هاتف..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>

        <View style={styles.pickerContainer}>
          <Picker
            selectedValue={selectedUserType}
            onValueChange={setSelectedUserType}
            style={styles.picker}
          >
            {userTypes.map((type) => (
              <Picker.Item
                key={type.value}
                label={type.label}
                value={type.value}
              />
            ))}
          </Picker>
        </View>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#2E7D32" style={styles.loader} />
      ) : (
        <FlatList
          data={filteredUsers}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderUserItem}
          contentContainerStyle={styles.listContainer}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Icon name="account-group" size={60} color="#E0E0E0" />
              <Text style={styles.emptyText}>لا توجد نتائج</Text>
            </View>
          }
        />
      )}

      {/* Edit/Add User Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {selectedUser ? 'تعديل مستخدم' : 'إضافة مستخدم جديد'}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Icon name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalForm}>
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>الاسم الكامل</Text>
                <TextInput
                  style={styles.formInput}
                  value={userForm.name}
                  onChangeText={(text) => setUserForm({ ...userForm, name: text })}
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>البريد الإلكتروني</Text>
                <TextInput
                  style={styles.formInput}
                  value={userForm.email}
                  onChangeText={(text) => setUserForm({ ...userForm, email: text })}
                  keyboardType="email-address"
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>رقم الهاتف</Text>
                <TextInput
                  style={styles.formInput}
                  value={userForm.phone}
                  onChangeText={(text) => setUserForm({ ...userForm, phone: text })}
                  keyboardType="phone-pad"
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>نوع المستخدم</Text>
                <View style={styles.formPicker}>
                  <Picker
                    selectedValue={userForm.userType}
                    onValueChange={(value) => setUserForm({ ...userForm, userType: value })}
                  >
                    <Picker.Item label="مشتري" value="buyer" />
                    <Picker.Item label="بائع" value="seller" />
                    <Picker.Item label="مندوب توصيل" value="driver" />
                    <Picker.Item label="مغسلة قات" value="washer" />
                    <Picker.Item label="مدير" value="admin" />
                  </Picker>
                </View>
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>الحالة</Text>
                <View style={styles.formPicker}>
                  <Picker
                    selectedValue={userForm.status}
                    onValueChange={(value) => setUserForm({ ...userForm, status: value })}
                  >
                    {statusOptions.map((option) => (
                      <Picker.Item
                        key={option.value}
                        label={option.label}
                        value={option.value}
                      />
                    ))}
                  </Picker>
                </View>
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>الرصيد (ريال)</Text>
                <TextInput
                  style={styles.formInput}
                  value={userForm.balance}
                  onChangeText={(text) => setUserForm({ ...userForm, balance: text })}
                  keyboardType="numeric"
                />
              </View>

              <View style={styles.modalActions}>
                <TouchableOpacity
                  style={[styles.modalButton, styles.cancelButton]}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.cancelButtonText}>إلغاء</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modalButton, styles.saveButton]}
                  onPress={handleSaveUser}
                >
                  <Text style={styles.saveButtonText}>حفظ</Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
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
  filterSection: {
    backgroundColor: '#fff',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 10,
  },
  searchIcon: {
    marginLeft: 10,
  },
  searchInput: {
    flex: 1,
    height: 40,
    textAlign: 'right',
  },
  pickerContainer: {
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    height: 40,
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
  },
  listContainer: {
    padding: 15,
  },
  userCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  userHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  userMeta: {
    flexDirection: 'row',
  },
  userEmail: {
    color: '#666',
    fontSize: 12,
    marginLeft: 10,
  },
  userPhone: {
    color: '#666',
    fontSize: 12,
  },
  userTypeBadge: {
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 10,
    paddingVertical: 2,
    borderRadius: 4,
  },
  userTypeText: {
    color: '#2196F3',
    fontSize: 10,
    fontWeight: '500',
  },
  userDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailText: {
    color: '#666',
    fontSize: 12,
    marginRight: 5,
  },
  userStatus: {
    marginBottom: 10,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  userActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    paddingTop: 10,
  },
  actionButton: {
    alignItems: 'center',
    padding: 5,
  },
  actionText: {
    fontSize: 10,
    marginTop: 2,
    color: '#666',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 50,
  },
  emptyText: {
    color: '#666',
    marginTop: 10,
    fontSize: 16,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 10,
    width: '90%',
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  modalForm: {
    padding: 20,
  },
  formGroup: {
    marginBottom: 15,
  },
  formLabel: {
    color: '#333',
    marginBottom: 5,
    fontWeight: '500',
  },
  formInput: {
    backgroundColor: '#F9F9F9',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 15,
    height: 40,
    textAlign: 'right',
  },
  formPicker: {
    backgroundColor: '#F9F9F9',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    overflow: 'hidden',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  cancelButton: {
    backgroundColor: '#F5F5F5',
  },
  cancelButtonText: {
    color: '#666',
    fontWeight: 'bold',
  },
  saveButton: {
    backgroundColor: '#2E7D32',
  },
  saveButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default UsersManagement;
