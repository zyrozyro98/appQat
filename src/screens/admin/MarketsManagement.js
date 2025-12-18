// src/screens/admin/MarketsManagement.js
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
  ScrollView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import MapView, { Marker } from 'react-native-maps';

const MarketsManagement = ({ navigation }) => {
  const [markets, setMarkets] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [mapModalVisible, setMapModalVisible] = useState(false);
  const [selectedMarket, setSelectedMarket] = useState(null);
  const [marketForm, setMarketForm] = useState({
    name: '',
    location: '',
    city: '',
    description: '',
    status: 'active',
    lat: 15.3694,
    lng: 44.1910,
    washingShopsCount: 0,
    sellersCount: 0,
    openingHours: '08:00 - 23:00',
  });

  useEffect(() => {
    loadMarkets();
  }, []);

  const loadMarkets = async () => {
    const mockMarkets = [
      {
        id: 1,
        name: 'سوق التحرير',
        location: 'صنعاء - التحرير',
        city: 'صنعاء',
        description: 'أكبر سوق للقات في صنعاء',
        status: 'active',
        lat: 15.3694,
        lng: 44.1910,
        washingShopsCount: 5,
        sellersCount: 45,
        openingHours: '08:00 - 23:00',
        createdAt: '2023-01-15',
      },
      {
        id: 2,
        name: 'سوق الثورة',
        location: 'صنعاء - الثورة',
        city: 'صنعاء',
        description: 'سوق حديث للقات',
        status: 'active',
        lat: 15.3722,
        lng: 44.2010,
        washingShopsCount: 3,
        sellersCount: 28,
        openingHours: '07:00 - 22:00',
        createdAt: '2023-02-20',
      },
      {
        id: 3,
        name: 'سوق الحديدة',
        location: 'الحديدة - المدينة',
        city: 'الحديدة',
        description: 'سوق رئيسي في الحديدة',
        status: 'inactive',
        lat: 14.8022,
        lng: 42.9511,
        washingShopsCount: 2,
        sellersCount: 15,
        openingHours: '09:00 - 21:00',
        createdAt: '2023-03-10',
      },
    ];
    setMarkets(mockMarkets);
  };

  const handleSaveMarket = async () => {
    if (!marketForm.name || !marketForm.location || !marketForm.city) {
      Alert.alert('خطأ', 'يرجى ملء جميع الحقول المطلوبة');
      return;
    }

    if (selectedMarket) {
      // تحديث السوق
      Alert.alert('نجاح', 'تم تحديث بيانات السوق');
    } else {
      // إضافة سوق جديد
      Alert.alert('نجاح', 'تم إضافة السوق بنجاح');
    }
    setModalVisible(false);
    loadMarkets();
  };

  const handleDeleteMarket = (marketId) => {
    Alert.alert(
      'تأكيد الحذف',
      'هل أنت متأكد من حذف هذا السوق؟ سيتم حذف جميع البائعين والمغاسل المرتبطة به.',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حذف',
          style: 'destructive',
          onPress: async () => {
            Alert.alert('نجاح', 'تم حذف السوق');
            loadMarkets();
          },
        },
      ]
    );
  };

  const openMarketDetails = (market) => {
    navigation.navigate('MarketDetails', { marketId: market.id });
  };

  const renderMarketItem = ({ item }) => (
    <View style={styles.marketCard}>
      <View style={styles.marketHeader}>
        <View style={styles.marketInfo}>
          <Text style={styles.marketName}>{item.name}</Text>
          <Text style={styles.marketLocation}>{item.location}</Text>
          <Text style={styles.marketCity}>{item.city}</Text>
        </View>
        <View style={[styles.statusBadge, getStatusStyle(item.status)]}>
          <Text style={styles.statusText}>{getStatusLabel(item.status)}</Text>
        </View>
      </View>

      <Text style={styles.marketDescription}>{item.description}</Text>

      <View style={styles.marketStats}>
        <View style={styles.statItem}>
          <Icon name="store" size={16} color="#4CAF50" />
          <Text style={styles.statText}>{item.sellersCount} بائع</Text>
        </View>
        <View style={styles.statItem}>
          <Icon name="water" size={16} color="#2196F3" />
          <Text style={styles.statText}>{item.washingShopsCount} مغسلة</Text>
        </View>
        <View style={styles.statItem}>
          <Icon name="clock" size={16} color="#FF9800" />
          <Text style={styles.statText}>{item.openingHours}</Text>
        </View>
      </View>

      <View style={styles.marketActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => openMarketDetails(item)}
        >
          <Icon name="information" size={18} color="#2196F3" />
          <Text style={styles.actionText}>تفاصيل</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {
            setSelectedMarket(item);
            setMarketForm(item);
            setModalVisible(true);
          }}
        >
          <Icon name="pencil" size={18} color="#4CAF50" />
          <Text style={styles.actionText}>تعديل</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('MarketSellers', { marketId: item.id })}
        >
          <Icon name="account-group" size={18} color="#FF9800" />
          <Text style={styles.actionText}>البائعين</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => handleDeleteMarket(item.id)}
        >
          <Icon name="delete" size={18} color="#D32F2F" />
          <Text style={styles.actionText}>حذف</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const getStatusLabel = (status) => {
    const statusMap = {
      active: 'نشط',
      inactive: 'غير نشط',
      maintenance: 'صيانة',
      closed: 'مغلق',
    };
    return statusMap[status] || status;
  };

  const getStatusStyle = (status) => {
    switch (status) {
      case 'active':
        return { backgroundColor: '#4CAF50' };
      case 'inactive':
        return { backgroundColor: '#666' };
      case 'maintenance':
        return { backgroundColor: '#FF9800' };
      case 'closed':
        return { backgroundColor: '#D32F2F' };
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
        <Text style={styles.headerTitle}>إدارة الأسواق</Text>
        <TouchableOpacity onPress={() => {
          setSelectedMarket(null);
          setMarketForm({
            name: '',
            location: '',
            city: '',
            description: '',
            status: 'active',
            lat: 15.3694,
            lng: 44.1910,
            washingShopsCount: 0,
            sellersCount: 0,
            openingHours: '08:00 - 23:00',
          });
          setModalVisible(true);
        }}>
          <Icon name="plus-circle" size={24} color="#2E7D32" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={markets}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderMarketItem}
        contentContainerStyle={styles.listContainer}
      />

      {/* Add/Edit Market Modal */}
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
                {selectedMarket ? 'تعديل سوق' : 'إضافة سوق جديد'}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Icon name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalForm}>
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>اسم السوق *</Text>
                <TextInput
                  style={styles.formInput}
                  value={marketForm.name}
                  onChangeText={(text) => setMarketForm({ ...marketForm, name: text })}
                  placeholder="أدخل اسم السوق"
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>الموقع *</Text>
                <TextInput
                  style={styles.formInput}
                  value={marketForm.location}
                  onChangeText={(text) => setMarketForm({ ...marketForm, location: text })}
                  placeholder="الموقع التفصيلي"
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>المدينة *</Text>
                <TextInput
                  style={styles.formInput}
                  value={marketForm.city}
                  onChangeText={(text) => setMarketForm({ ...marketForm, city: text })}
                  placeholder="اسم المدينة"
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>الوصف</Text>
                <TextInput
                  style={[styles.formInput, styles.textArea]}
                  value={marketForm.description}
                  onChangeText={(text) => setMarketForm({ ...marketForm, description: text })}
                  placeholder="وصف مختصر عن السوق"
                  multiline
                  numberOfLines={3}
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>ساعات العمل</Text>
                <TextInput
                  style={styles.formInput}
                  value={marketForm.openingHours}
                  onChangeText={(text) => setMarketForm({ ...marketForm, openingHours: text })}
                  placeholder="مثال: 08:00 - 23:00"
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>إحداثيات الموقع</Text>
                <TouchableOpacity
                  style={styles.mapButton}
                  onPress={() => setMapModalVisible(true)}
                >
                  <Icon name="map-marker" size={20} color="#666" />
                  <Text style={styles.mapButtonText}>
                    {marketForm.lat.toFixed(4)}, {marketForm.lng.toFixed(4)}
                  </Text>
                  <Text style={styles.mapChangeText}>تغيير الموقع</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.statsPreview}>
                <Text style={styles.statsTitle}>إحصائيات السوق:</Text>
                <View style={styles.statsRow}>
                  <View style={styles.statPreview}>
                    <Icon name="store" size={16} color="#4CAF50" />
                    <Text style={styles.statPreviewText}>
                      {marketForm.sellersCount} بائع
                    </Text>
                  </View>
                  <View style={styles.statPreview}>
                    <Icon name="water" size={16} color="#2196F3" />
                    <Text style={styles.statPreviewText}>
                      {marketForm.washingShopsCount} مغسلة
                    </Text>
                  </View>
                </View>
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
                  onPress={handleSaveMarket}
                >
                  <Text style={styles.saveButtonText}>
                    {selectedMarket ? 'تحديث' : 'إضافة'}
                  </Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Map Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={mapModalVisible}
        onRequestClose={() => setMapModalVisible(false)}
      >
        <View style={styles.mapModalContainer}>
          <View style={styles.mapModalContent}>
            <View style={styles.mapModalHeader}>
              <Text style={styles.mapModalTitle}>اختر موقع السوق على الخريطة</Text>
              <TouchableOpacity onPress={() => setMapModalVisible(false)}>
                <Icon name="close" size={24} color="#333" />
              </TouchableOpacity>
            </View>
            
            <MapView
              style={styles.map}
              initialRegion={{
                latitude: marketForm.lat,
                longitude: marketForm.lng,
                latitudeDelta: 0.01,
                longitudeDelta: 0.01,
              }}
              onPress={(e) => {
                setMarketForm({
                  ...marketForm,
                  lat: e.nativeEvent.coordinate.latitude,
                  lng: e.nativeEvent.coordinate.longitude,
                });
              }}
            >
              <Marker
                coordinate={{
                  latitude: marketForm.lat,
                  longitude: marketForm.lng,
                }}
                title={marketForm.name || 'موقع السوق'}
                description="اضغط على الخريطة لتغيير الموقع"
              />
            </MapView>

            <View style={styles.mapCoordinates}>
              <Text style={styles.coordinatesText}>
                خط العرض: {marketForm.lat.toFixed(6)}
              </Text>
              <Text style={styles.coordinatesText}>
                خط الطول: {marketForm.lng.toFixed(6)}
              </Text>
            </View>

            <TouchableOpacity
              style={styles.confirmLocationButton}
              onPress={() => setMapModalVisible(false)}
            >
              <Text style={styles.confirmLocationText}>تأكيد الموقع</Text>
            </TouchableOpacity>
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
  listContainer: {
    padding: 15,
  },
  marketCard: {
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
  marketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  marketInfo: {
    flex: 1,
  },
  marketName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  marketLocation: {
    color: '#666',
    fontSize: 12,
    marginBottom: 2,
  },
  marketCity: {
    color: '#2196F3',
    fontSize: 11,
    fontWeight: '500',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  marketDescription: {
    color: '#666',
    fontSize: 12,
    marginBottom: 10,
    lineHeight: 16,
  },
  marketStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
    marginBottom: 10,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    color: '#666',
    fontSize: 11,
    marginRight: 5,
  },
  marketActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
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
  textArea: {
    height: 80,
    textAlignVertical: 'top',
    paddingTop: 10,
  },
  mapButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9F9F9',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 15,
    height: 40,
    justifyContent: 'space-between',
  },
  mapButtonText: {
    color: '#666',
    flex: 1,
    textAlign: 'right',
    marginRight: 10,
  },
  mapChangeText: {
    color: '#2196F3',
    fontSize: 12,
  },
  statsPreview: {
    backgroundColor: '#F5F5F5',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10,
  },
  statsTitle: {
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statPreview: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statPreviewText: {
    color: '#666',
    fontSize: 12,
    marginRight: 5,
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
  mapModalContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  mapModalContent: {
    flex: 1,
  },
  mapModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  mapModalTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    marginRight: 10,
  },
  map: {
    flex: 1,
  },
  mapCoordinates: {
    padding: 15,
    backgroundColor: '#F9F9F9',
  },
  coordinatesText: {
    color: '#333',
    fontSize: 12,
    marginBottom: 5,
  },
  confirmLocationButton: {
    backgroundColor: '#2E7D32',
    padding: 15,
    alignItems: 'center',
  },
  confirmLocationText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default MarketsManagement;
