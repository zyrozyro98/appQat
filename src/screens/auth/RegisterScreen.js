// src/screens/auth/RegisterScreen.js
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
import { Picker } from '@react-native-picker/picker';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const RegisterScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    userType: 'buyer',
    storeName: '',
    vehicleType: '',
    washingShopName: '',
  });

  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  const userTypes = [
    { label: 'مشتري', value: 'buyer' },
    { label: 'بائع', value: 'seller' },
    { label: 'مندوب توصيل', value: 'driver' },
    { label: 'مغسلة قات', value: 'washer' },
  ];

  const validateForm = () => {
    const newErrors = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'الاسم الكامل مطلوب';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'البريد الإلكتروني مطلوب';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'البريد الإلكتروني غير صالح';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'رقم الهاتف مطلوب';
    } else if (!/^(77|71|73|70)\d{7}$/.test(formData.phone)) {
      newErrors.phone = 'رقم الهاتف اليمني غير صالح';
    }

    if (!formData.password) {
      newErrors.password = 'كلمة المرور مطلوبة';
    } else if (formData.password.length < 6) {
      newErrors.password = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'كلمات المرور غير متطابقة';
    }

    if (formData.userType === 'seller' && !formData.storeName.trim()) {
      newErrors.storeName = 'اسم المتجر مطلوب';
    }

    if (formData.userType === 'driver' && !formData.vehicleType.trim()) {
      newErrors.vehicleType = 'نوع المركبة مطلوب';
    }

    if (formData.userType === 'washer' && !formData.washingShopName.trim()) {
      newErrors.washingShopName = 'اسم المغسلة مطلوب';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    try {
      // إرسال بيانات التسجيل
      Alert.alert('نجاح', 'تم إنشاء الحساب بنجاح');
      navigation.navigate('Login');
    } catch (error) {
      Alert.alert('خطأ', 'فشل في إنشاء الحساب');
    }
  };

  const renderAdditionalFields = () => {
    switch (formData.userType) {
      case 'seller':
        return (
          <>
            <View style={styles.inputContainer}>
              <Icon name="store" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="اسم المتجر"
                value={formData.storeName}
                onChangeText={(text) =>
                  setFormData({ ...formData, storeName: text })
                }
              />
            </View>
            {errors.storeName && (
              <Text style={styles.errorText}>{errors.storeName}</Text>
            )}
          </>
        );

      case 'driver':
        return (
          <>
            <View style={styles.inputContainer}>
              <Icon name="car" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="نوع المركبة (دراجة نارية، سيارة)"
                value={formData.vehicleType}
                onChangeText={(text) =>
                  setFormData({ ...formData, vehicleType: text })
                }
              />
            </View>
            {errors.vehicleType && (
              <Text style={styles.errorText}>{errors.vehicleType}</Text>
            )}
          </>
        );

      case 'washer':
        return (
          <>
            <View style={styles.inputContainer}>
              <Icon name="water" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="اسم مغسلة القات"
                value={formData.washingShopName}
                onChangeText={(text) =>
                  setFormData({ ...formData, washingShopName: text })
                }
              />
            </View>
            {errors.washingShopName && (
              <Text style={styles.errorText}>{errors.washingShopName}</Text>
            )}
          </>
        );

      default:
        return null;
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-right" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>إنشاء حساب جديد</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.formContainer}>
        <View style={styles.inputContainer}>
          <Icon name="account" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="الاسم الكامل"
            value={formData.fullName}
            onChangeText={(text) => setFormData({ ...formData, fullName: text })}
          />
        </View>
        {errors.fullName && (
          <Text style={styles.errorText}>{errors.fullName}</Text>
        )}

        <View style={styles.inputContainer}>
          <Icon name="email" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="البريد الإلكتروني"
            value={formData.email}
            onChangeText={(text) => setFormData({ ...formData, email: text })}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </View>
        {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}

        <View style={styles.inputContainer}>
          <Icon name="phone" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="رقم الهاتف (77xxxxxx)"
            value={formData.phone}
            onChangeText={(text) => setFormData({ ...formData, phone: text })}
            keyboardType="phone-pad"
          />
        </View>
        {errors.phone && <Text style={styles.errorText}>{errors.phone}</Text>}

        <View style={styles.inputContainer}>
          <Icon name="lock" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="كلمة المرور"
            value={formData.password}
            onChangeText={(text) => setFormData({ ...formData, password: text })}
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
        {errors.password && (
          <Text style={styles.errorText}>{errors.password}</Text>
        )}

        <View style={styles.inputContainer}>
          <Icon name="lock-check" size={20} color="#666" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="تأكيد كلمة المرور"
            value={formData.confirmPassword}
            onChangeText={(text) =>
              setFormData({ ...formData, confirmPassword: text })
            }
            secureTextEntry={!showPassword}
          />
        </View>
        {errors.confirmPassword && (
          <Text style={styles.errorText}>{errors.confirmPassword}</Text>
        )}

        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>نوع المستخدم:</Text>
          <View style={styles.pickerWrapper}>
            <Picker
              selectedValue={formData.userType}
              onValueChange={(value) =>
                setFormData({ ...formData, userType: value })
              }
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

        {renderAdditionalFields()}

        <TouchableOpacity style={styles.registerButton} onPress={handleRegister}>
          <Text style={styles.registerButtonText}>إنشاء الحساب</Text>
          <Icon name="check-circle" size={20} color="#fff" />
        </TouchableOpacity>

        <View style={styles.termsContainer}>
          <Text style={styles.termsText}>
            بالتسجيل فإنك توافق على{' '}
            <Text style={styles.linkText}>الشروط والأحكام</Text> و{' '}
            <Text style={styles.linkText}>سياسة الخصوصية</Text>
          </Text>
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
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  formContainer: {
    padding: 20,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  inputIcon: {
    marginLeft: 10,
  },
  input: {
    flex: 1,
    height: 50,
    textAlign: 'right',
  },
  eyeIcon: {
    padding: 10,
  },
  pickerContainer: {
    marginBottom: 20,
  },
  pickerLabel: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
  pickerWrapper: {
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  picker: {
    height: 50,
  },
  registerButton: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  registerButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 10,
  },
  errorText: {
    color: '#D32F2F',
    fontSize: 12,
    marginBottom: 10,
    textAlign: 'right',
  },
  termsContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
  },
  termsText: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
  },
  linkText: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
});

export default RegisterScreen;
