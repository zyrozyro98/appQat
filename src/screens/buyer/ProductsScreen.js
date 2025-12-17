// src/screens/buyer/ProductsScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  Image,
  TouchableOpacity,
  StyleSheet,
  Alert,
  TextInput,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { addToCart } from '../../store/actions/cartActions';

const ProductsScreen = ({ navigation }) => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [washingOption, setWashingOption] = useState(false);
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const categories = [
    { id: 'all', name: 'الكل' },
    { id: 'premium', name: 'فاخر' },
    { id: 'medium', name: 'متوسط' },
    { id: 'economic', name: 'اقتصادي' },
  ];

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    filterProducts();
  }, [searchQuery, selectedCategory]);

  const loadProducts = async () => {
    // جلب المنتجات من API
    const sampleProducts = [
      {
        id: 1,
        name: 'قات يمني ممتاز',
        description: 'أجود أنواع القات اليمني من أفضل المزارع',
        price: 45,
        category: 'premium',
        image: 'https://via.placeholder.com/300x200/4CAF50/FFFFFF',
        seller: 'مزرعة الأخضر',
        sellerRating: 4.8,
        stock: 10,
        market: 'سوق التحرير',
        washingAvailable: true,
        washingPrice: 100,
      },
      // ... منتجات أخرى
    ];
    setProducts(sampleProducts);
    setFilteredProducts(sampleProducts);
  };

  const filterProducts = () => {
    let filtered = products;

    if (searchQuery) {
      filtered = filtered.filter(
        (product) =>
          product.name.includes(searchQuery) ||
          product.description.includes(searchQuery) ||
          product.seller.includes(searchQuery)
      );
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(
        (product) => product.category === selectedCategory
      );
    }

    setFilteredProducts(filtered);
  };

  const handleAddToCart = (product) => {
    const finalPrice = washingOption
      ? product.price + product.washingPrice
      : product.price;

    const cartItem = {
      ...product,
      requiresWashing: washingOption,
      finalPrice,
      quantity: 1,
    };

    dispatch(addToCart(cartItem));
    Alert.alert('تمت الإضافة', 'تم إضافة المنتج إلى السلة');
  };

  const renderProductItem = ({ item }) => (
    <TouchableOpacity
      style={styles.productCard}
      onPress={() => navigation.navigate('ProductDetails', { product: item })}
    >
      <Image source={{ uri: item.image }} style={styles.productImage} />
      <View style={styles.productInfo}>
        <View style={styles.productHeader}>
          <Text style={styles.productName}>{item.name}</Text>
          <View style={styles.ratingContainer}>
            <Icon name="star" size={16} color="#FFC107" />
            <Text style={styles.ratingText}>{item.sellerRating}</Text>
          </View>
        </View>

        <Text style={styles.productDescription} numberOfLines={2}>
          {item.description}
        </Text>

        <View style={styles.sellerInfo}>
          <Icon name="store" size={14} color="#666" />
          <Text style={styles.sellerText}>{item.seller}</Text>
        </View>

        <View style={styles.marketInfo}>
          <Icon name="map-marker" size={14} color="#666" />
          <Text style={styles.marketText}>{item.market}</Text>
        </View>

        <View style={styles.priceContainer}>
          <Text style={styles.priceText}>{item.price} ريال</Text>
          {item.washingAvailable && (
            <View style={styles.washingOption}>
              <Icon name="water" size={16} color="#2196F3" />
              <Text style={styles.washingText}>غسل متاح (+100 ريال)</Text>
            </View>
          )}
        </View>

        <TouchableOpacity
          style={styles.addButton}
          onPress={() => handleAddToCart(item)}
        >
          <Text style={styles.addButtonText}>إضافة إلى السلة</Text>
          <Icon name="cart-plus" size={18} color="#fff" />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TextInput
          style={styles.searchInput}
          placeholder="ابحث عن منتج..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <TouchableOpacity
          style={styles.cartButton}
          onPress={() => navigation.navigate('Cart')}
        >
          <Icon name="cart" size={24} color="#2E7D32" />
        </TouchableOpacity>
      </View>

      <View style={styles.washingToggle}>
        <Text style={styles.washingLabel}>خدمة غسل القات:</Text>
        <TouchableOpacity
          style={[
            styles.toggleButton,
            washingOption && styles.toggleButtonActive,
          ]}
          onPress={() => setWashingOption(!washingOption)}
        >
          <Text
            style={[
              styles.toggleText,
              washingOption && styles.toggleTextActive,
            ]}
          >
            {washingOption ? 'مفعلة (+100 ريال)' : 'معطلة'}
          </Text>
          <Icon
            name={washingOption ? 'toggle-switch' : 'toggle-switch-off'}
            size={24}
            color={washingOption ? '#2E7D32' : '#666'}
          />
        </TouchableOpacity>
      </View>

      <View style={styles.categoriesContainer}>
        <FlatList
          horizontal
          data={categories}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.categoryButton,
                selectedCategory === item.id && styles.categoryButtonActive,
              ]}
              onPress={() => setSelectedCategory(item.id)}
            >
              <Text
                style={[
                  styles.categoryText,
                  selectedCategory === item.id && styles.categoryTextActive,
                ]}
              >
                {item.name}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>

      <FlatList
        data={filteredProducts}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderProductItem}
        contentContainerStyle={styles.productsList}
      />
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
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#fff',
  },
  searchInput: {
    flex: 1,
    height: 40,
    backgroundColor: '#F9F9F9',
    borderRadius: 20,
    paddingHorizontal: 15,
    marginRight: 10,
    textAlign: 'right',
  },
  cartButton: {
    padding: 5,
  },
  washingToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#fff',
    marginTop: 5,
  },
  washingLabel: {
    fontSize: 16,
    color: '#333',
  },
  toggleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    borderRadius: 20,
    backgroundColor: '#F5F5F5',
  },
  toggleButtonActive: {
    backgroundColor: '#E8F5E8',
  },
  toggleText: {
    marginRight: 5,
    color: '#666',
  },
  toggleTextActive: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  categoriesContainer: {
    backgroundColor: '#fff',
    paddingVertical: 10,
  },
  categoryButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    marginHorizontal: 5,
    borderRadius: 20,
    backgroundColor: '#F5F5F5',
  },
  categoryButtonActive: {
    backgroundColor: '#2E7D32',
  },
  categoryText: {
    color: '#666',
  },
  categoryTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  productsList: {
    padding: 10,
  },
  productCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  productImage: {
    width: '100%',
    height: 200,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  productInfo: {
    padding: 15,
  },
  productHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  productName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    marginLeft: 5,
    color: '#FFC107',
    fontWeight: 'bold',
  },
  productDescription: {
    color: '#666',
    marginBottom: 10,
    textAlign: 'right',
  },
  sellerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  sellerText: {
    marginRight: 5,
    color: '#666',
    fontSize: 12,
  },
  marketInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  marketText: {
    marginRight: 5,
    color: '#666',
    fontSize: 12,
  },
  priceContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  priceText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  washingOption: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  washingText: {
    marginRight: 5,
    color: '#2196F3',
    fontSize: 12,
  },
  addButton: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
  },
  addButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    marginRight: 10,
  },
});

export default ProductsScreen;
