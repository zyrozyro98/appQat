// src/navigation/AppNavigator.js
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector } from 'react-redux';

// Auth Screens
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// Buyer Screens
import HomeScreen from '../screens/buyer/HomeScreen';
import ProductsScreen from '../screens/buyer/ProductsScreen';
import CartScreen from '../screens/buyer/CartScreen';
import CheckoutScreen from '../screens/buyer/CheckoutScreen';
import OrdersScreen from '../screens/buyer/OrdersScreen';
import WalletScreen from '../screens/buyer/WalletScreen';
import ProfileScreen from '../screens/buyer/ProfileScreen';

// Seller Screens
import SellerDashboard from '../screens/seller/SellerDashboard';
import AddProductScreen from '../screens/seller/AddProductScreen';
import SellerOrdersScreen from '../screens/seller/SellerOrdersScreen';
import SellerWalletScreen from '../screens/seller/SellerWalletScreen';

// Admin Screens
import AdminDashboard from '../screens/admin/AdminDashboard';
import UsersManagement from '../screens/admin/UsersManagement';
import MarketsManagement from '../screens/admin/MarketsManagement';
import WashingShopsManagement from '../screens/admin/WashingShopsManagement';
import DriversManagement from '../screens/admin/DriversManagement';
import AdsManagement from '../screens/admin/AdsManagement';
import AdPackagesScreen from '../screens/admin/AdPackagesScreen';
import TransfersManagement from '../screens/admin/TransfersManagement';
import GiftCardsScreen from '../screens/admin/GiftCardsScreen';

// Common Screens
import ProductDetailsScreen from '../screens/common/ProductDetailsScreen';
import OrderDetailsScreen from '../screens/common/OrderDetailsScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
  const { user, userType } = useSelector((state) => state.auth);

  const getInitialRoute = () => {
    if (!user) return 'Login';
    
    switch (userType) {
      case 'admin':
        return 'AdminDashboard';
      case 'seller':
        return 'SellerDashboard';
      case 'driver':
        return 'DriverDashboard';
      case 'washer':
        return 'WasherDashboard';
      default:
        return 'Home';
    }
  };

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName={getInitialRoute()}
        screenOptions={{
          headerShown: false,
          cardStyle: { backgroundColor: '#F5F5F5' },
        }}
      >
        {/* Auth Stack */}
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Register" component={RegisterScreen} />

        {/* Buyer Stack */}
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Products" component={ProductsScreen} />
        <Stack.Screen name="Cart" component={CartScreen} />
        <Stack.Screen name="Checkout" component={CheckoutScreen} />
        <Stack.Screen name="Orders" component={OrdersScreen} />
        <Stack.Screen name="Wallet" component={WalletScreen} />
        <Stack.Screen name="Profile" component={ProfileScreen} />

        {/* Seller Stack */}
        <Stack.Screen name="SellerDashboard" component={SellerDashboard} />
        <Stack.Screen name="AddProduct" component={AddProductScreen} />
        <Stack.Screen name="SellerOrders" component={SellerOrdersScreen} />
        <Stack.Screen name="SellerWallet" component={SellerWalletScreen} />

        {/* Admin Stack */}
        <Stack.Screen name="AdminDashboard" component={AdminDashboard} />
        <Stack.Screen name="UsersManagement" component={UsersManagement} />
        <Stack.Screen name="MarketsManagement" component={MarketsManagement} />
        <Stack.Screen name="WashingShopsManagement" component={WashingShopsManagement} />
        <Stack.Screen name="DriversManagement" component={DriversManagement} />
        <Stack.Screen name="AdsManagement" component={AdsManagement} />
        <Stack.Screen name="AdPackages" component={AdPackagesScreen} />
        <Stack.Screen name="TransfersManagement" component={TransfersManagement} />
        <Stack.Screen name="GiftCards" component={GiftCardsScreen} />

        {/* Common Screens */}
        <Stack.Screen name="ProductDetails" component={ProductDetailsScreen} />
        <Stack.Screen name="OrderDetails" component={OrderDetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
