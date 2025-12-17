// src/screens/buyer/CartScreen.js
import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { removeFromCart, updateCartItem } from '../../store/actions/cartActions';

const CartScreen = ({ navigation }) => {
  const { items } = useSelector((state) => state.cart);
  const { user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();

  const calculateTotal = () => {
    return items.reduce((total, item) => total + item.finalPrice * item.quantity, 0);
  };

  const handleRemoveItem = (itemId) => {
    dispatch(removeFromCart(itemId));
  };

  const handleUpdateQuantity = (itemId, newQuantity) => {
    if (newQuantity < 1) {
      handleRemoveItem(itemId);
      return;
    }
    dispatch(updateCartItem(itemId, newQuantity));
  };

  const handleCheckout = () => {
    if (!user) {
      Alert.alert('تسجيل الدخول', 'يرجى تسجيل الدخول لإتمام الشراء');
      navigation.navigate('Login');
      return;
    }

    if (calculateTotal() > user.balance) {
      Alert.alert('رصيد غير كافي', 'يرجى شحن رصيدك لإتمام الشراء');
      navigation.navigate('Wallet');
      return;
    }

    navigation.navigate('Checkout', { total: calculateTotal() });
  };

  const renderCartItem = ({ item }) => (
    <View style={styles.cartItem}>
      <View style={styles.itemInfo}>
        <Text style={styles.itemName}>{item.name}</Text>
        <Text style={styles.itemSeller}>البائع: {item.seller}</Text>
        
        {item.requiresWashing && (
          <View style={styles.washingBadge}>
            <Icon name="water" size={14} color="#2196F3" />
            <Text style={styles.washingBadgeText}>مع الغسل</Text>
          </View>
        )}
        
        <Text style={styles.itemPrice}>
          {item.finalPrice} ريال × {item.quantity}
        </Text>
        <Text style={styles.itemTotal}>
          الإجمالي: {item.finalPrice * item.quantity} ريال
        </Text>
      </View>

      <View style={styles.itemActions}>
        <View style={styles.quantityControl}>
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => handleUpdateQuantity(item.id, item.quantity - 1)}
          >
            <Text style={styles.quantityButtonText}>-</Text>
          </TouchableOpacity>
          
          <Text style={styles.quantityText}>{item.quantity}</Text>
          
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => handleUpdateQuantity(item.id, item.quantity + 1)}
          >
            <Text style={styles.quantityButtonText}>+</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={styles.removeButton}
          onPress={() => handleRemoveItem(item.id)}
        >
          <Icon name="delete" size={20} color="#D32F2F" />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-right" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>سلة التسوق</Text>
        <View style={{ width: 24 }} />
      </View>

      {items.length === 0 ? (
        <View style={styles.emptyCart}>
          <Icon name="cart-off" size={80} color="#E0E0E0" />
          <Text style={styles.emptyCartText}>سلة التسوق فارغة</Text>
          <TouchableOpacity
            style={styles.shopButton}
            onPress={() => navigation.navigate('Products')}
          >
            <Text style={styles.shopButtonText}>تصفح المنتجات</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          <FlatList
            data={items}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderCartItem}
            contentContainerStyle={styles.cartList}
          />

          <View style={styles.summary}>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>المجموع الفرعي:</Text>
              <Text style={styles.summaryValue}>
                {calculateTotal()} ريال
              </Text>
            </View>
            
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>رسوم التوصيل:</Text>
              <Text style={styles.summaryValue}>10 ريال</Text>
            </View>
            
            <View style={[styles.summaryRow, styles.totalRow]}>
              <Text style={styles.totalLabel}>المجموع الكلي:</Text>
              <Text style={styles.totalValue}>
                {calculateTotal() + 10} ريال
              </Text>
            </View>

            <View style={styles.balanceRow}>
              <Text style={styles.balanceLabel}>رصيدك الحالي:</Text>
              <Text style={styles.balanceValue}>{user?.balance || 0} ريال</Text>
            </View>

            <TouchableOpacity style={styles.checkoutButton} onPress={handleCheckout}>
              <Text style={styles.checkoutButtonText}>إتمام الشراء</Text>
              <Icon name="arrow-left" size={20} color="#fff" />
            </TouchableOpacity>

            {user && calculateTotal() > user.balance && (
              <TouchableOpacity
                style={styles.topupButton}
                onPress={() => navigation.navigate('Wallet')}
              >
                <Text style={styles.topupButtonText}>شحن الرصيد</Text>
                <Icon name="credit-card-plus" size={20} color="#2E7D32" />
              </TouchableOpacity>
            )}
          </View>
        </>
      )}
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
  emptyCart: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyCartText: {
    fontSize: 18,
    color: '#666',
    marginTop: 20,
    marginBottom: 30,
  },
  shopButton: {
    backgroundColor: '#2E7D32',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cartList: {
    padding: 15,
  },
  cartItem: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  itemSeller: {
    color: '#666',
    fontSize: 12,
    marginBottom: 5,
  },
  washingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginBottom: 5,
  },
  washingBadgeText: {
    color: '#2196F3',
    fontSize: 10,
    marginRight: 5,
  },
  itemPrice: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: 2,
  },
  itemTotal: {
    color: '#666',
    fontSize: 12,
  },
  itemActions: {
    alignItems: 'center',
  },
  quantityControl: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  quantityButton: {
    width: 30,
    height: 30,
    backgroundColor: '#F5F5F5',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantityButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  quantityText: {
    marginHorizontal: 10,
    fontSize: 16,
    fontWeight: 'bold',
  },
  removeButton: {
    padding: 5,
  },
  summary: {
    backgroundColor: '#fff',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  summaryLabel: {
    color: '#666',
  },
  summaryValue: {
    color: '#333',
    fontWeight: '500',
  },
  totalRow: {
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    paddingTop: 10,
    marginTop: 10,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  totalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  balanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  balanceLabel: {
    color: '#666',
  },
  balanceValue: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  checkoutButton: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  checkoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  topupButton: {
    borderWidth: 2,
    borderColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  topupButtonText: {
    color: '#2E7D32',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});

export default CartScreen;
