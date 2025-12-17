// src/screens/auth/LoginScreen.js
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser } from '../../store/actions/authActions';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('خطأ', 'يرجى إدخال البريد الإلكتروني وكلمة المرور');
      return;
    }

    dispatch(loginUser({ email, password }));
  };

  const handleRegister = () => {
    navigation.navigate('Register');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.logoContainer}>
        <Icon name="leaf" size={80} color="#2E7D32" />
        <Text style={styles.appName}>تطبيق قات</Text>
        <Text style={styles.tagline}>منصة بيع وتوصيل القات</Text>
      </View>

      <View style={styles.formContainer}>
        <Text style={styles.title}>تسجيل الدخول</Text>

        {error && (
          <View style={styles.errorContainer}>
            <Icon name="alert-circle" size={20} color="#D32F2F" />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        <View style={styles.inputContainer}>
          <Icon name="email" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="البريد الإلكتروني"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputContainer}>
          <Icon name="lock" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="كلمة المرور"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
          />
          <TouchableOpacity
            onPress={() => setShowPassword(!showPassword)}
            style={styles.eyeIcon}
          >
            <Icon
              name={showPassword ? 'eye-off' : 'eye'}
              size={20}
              color="#666"
            />
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.forgotPassword}>
          <Text style={styles.forgotPasswordText}>نسيت كلمة المرور؟</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.loginButton, loading && styles.disabledButton]}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Text style={styles.loginButtonText}>تسجيل الدخول</Text>
              <Icon name="login" size={20} color="#fff" />
            </>
          )}
        </TouchableOpacity>

        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>أو</Text>
          <View style={styles.dividerLine} />
        </View>

        <TouchableOpacity
          style={styles.registerButton}
          onPress={handleRegister}
        >
          <Text style={styles.registerButtonText}>إنشاء حساب جديد</Text>
          <Icon name="account-plus" size={20} color="#2E7D32" />
        </TouchableOpacity>

        <View style={styles.userTypes}>
          <Text style={styles.userTypesTitle}>أنواع الحسابات:</Text>
          <View style={styles.userTypeItem}>
            <Icon name="account" size={16} color="#2E7D32" />
            <Text style={styles.userTypeText}>مشتري - شراء وتقييم المنتجات</Text>
          </View>
          <View style={styles.userTypeItem}>
            <Icon name="store" size={16} color="#2E7D32" />
            <Text style={styles.userTypeText}>بائع - عرض وبيع المنتجات</Text>
          </View>
          <View style={styles.userTypeItem}>
            <Icon name="truck-delivery" size={16} color="#2E7D32" />
            <Text style={styles.userTypeText}>مندوب توصيل</Text>
          </View>
          <View style={styles.userTypeItem}>
            <Icon name="water" size={16} color="#2E7D32" />
            <Text style={styles.userTypeText}>مغسلة قات</Text>
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
  logoContainer: {
    alignItems: 'center',
    marginTop: 60,
    marginBottom: 40,
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginTop: 10,
  },
  tagline: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  formContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    marginBottom: 15,
    paddingHorizontal: 10,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    height: 50,
    textAlign: 'right',
  },
  eyeIcon: {
    padding: 10,
  },
  forgotPassword: {
    alignSelf: 'flex-start',
    marginBottom: 20,
  },
  forgotPasswordText: {
    color: '#2E7D32',
    fontSize: 14,
  },
  loginButton: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
  },
  disabledButton: {
    opacity: 0.7,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 10,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E0E0E0',
  },
  dividerText: {
    marginHorizontal: 10,
    color: '#666',
  },
  registerButton: {
    borderWidth: 2,
    borderColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
  },
  registerButtonText: {
    color: '#2E7D32',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 10,
  },
  userTypes: {
    marginTop: 30,
    padding: 15,
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
  },
  userTypesTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  userTypeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  userTypeText: {
    marginRight: 8,
    color: '#666',
  },
});

export default LoginScreen;
