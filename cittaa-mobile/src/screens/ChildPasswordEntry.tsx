import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as LocalAuthentication from 'expo-local-authentication';
import { useNavigation } from '@react-navigation/native';

const { width, height } = Dimensions.get('window');

interface ChildPasswordEntryProps {
  navigation: any;
}

export default function ChildPasswordEntry({ navigation }: ChildPasswordEntryProps) {
  const [password, setPassword] = useState('');
  const [language, setLanguage] = useState('english');
  const [isLoading, setIsLoading] = useState(false);
  const [biometricVerified, setBiometricVerified] = useState(false);

  const translations = {
    english: {
      title: 'CITTAA Safe Zone Activation',
      subtitle: 'Enter Your Secure Password:',
      biometric: 'Biometric Scan',
      activate: 'Activate Safe Zone',
      language: 'Language:',
      emergency: 'Emergency Parent Call'
    },
    hindi: {
      title: 'सिट्टा सुरक्षित क्षेत्र सक्रियण',
      subtitle: 'अपना सुरक्षित पासवर्ड दर्ज करें:',
      biometric: 'बायोमेट्रिक स्कैन',
      activate: 'सुरक्षित क्षेत्र सक्रिय करें',
      language: 'भाषा:',
      emergency: 'आपातकालीन माता-पिता कॉल'
    }
  };

  const t = translations[language as keyof typeof translations];

  const handleBiometricScan = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      if (!hasHardware) {
        Alert.alert('Error', 'Biometric hardware not available');
        return;
      }

      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      if (!isEnrolled) {
        Alert.alert('Error', 'No biometric data enrolled');
        return;
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Verify your identity',
        fallbackLabel: 'Use password instead',
      });

      if (result.success) {
        setBiometricVerified(true);
        Alert.alert('Success', 'Biometric verification successful!');
      }
    } catch (error) {
      Alert.alert('Error', 'Biometric authentication failed');
    }
  };

  const handlePasswordSubmit = async () => {
    if (!password) {
      Alert.alert('Error', 'Please enter your password');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/child-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          password: password,
          biometric_data: biometricVerified ? 'fingerprint_verified' : null
        }),
      });

      if (response.ok) {
        const userData = await response.json();
        navigation.navigate('ChildDashboard', { childData: userData.data });
      } else {
        Alert.alert('Error', 'Invalid password. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Connection error. Please check your internet connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmergencyCall = () => {
    Alert.alert(
      'Emergency Call',
      'This will call your parents immediately. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Call Now', onPress: () => Alert.alert('Calling...', 'Contacting parents...') }
      ]
    );
  };

  return (
    <LinearGradient
      colors={['#2563eb', '#7c3aed', '#4338ca']}
      style={styles.container}
    >
      <View style={styles.content}>
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Ionicons name="shield-checkmark" size={60} color="#fff" />
          </View>
          <Text style={styles.title}>{t.title}</Text>
        </View>

        <View style={styles.formContainer}>
          <View style={styles.avatarContainer}>
            <View style={styles.avatar}>
              <Text style={styles.avatarEmoji}>👦</Text>
            </View>
          </View>

          <Text style={styles.subtitle}>{t.subtitle}</Text>
          
          <TextInput
            style={styles.passwordInput}
            value={password}
            onChangeText={setPassword}
            placeholder="●●●●●●●●●●●●●●●●●●●●●●●"
            placeholderTextColor="#999"
            secureTextEntry
            autoCapitalize="none"
          />

          <TouchableOpacity
            style={[
              styles.biometricButton,
              biometricVerified && styles.biometricButtonVerified
            ]}
            onPress={handleBiometricScan}
          >
            <Ionicons 
              name="finger-print" 
              size={24} 
              color={biometricVerified ? "#059669" : "#666"} 
            />
            <Text style={[
              styles.biometricText,
              biometricVerified && styles.biometricTextVerified
            ]}>
              {t.biometric}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.activateButton, !password && styles.activateButtonDisabled]}
            onPress={handlePasswordSubmit}
            disabled={isLoading || !password}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.activateButtonText}>{t.activate}</Text>
            )}
          </TouchableOpacity>

          <View style={styles.languageContainer}>
            <Text style={styles.languageLabel}>{t.language}</Text>
            <TouchableOpacity
              style={[styles.languageButton, language === 'hindi' && styles.languageButtonActive]}
              onPress={() => setLanguage('hindi')}
            >
              <Text style={[styles.languageButtonText, language === 'hindi' && styles.languageButtonTextActive]}>
                हिंदी
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.languageButton, language === 'english' && styles.languageButtonActive]}
              onPress={() => setLanguage('english')}
            >
              <Text style={[styles.languageButtonText, language === 'english' && styles.languageButtonTextActive]}>
                English
              </Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.emergencyButton} onPress={handleEmergencyCall}>
            <Text style={styles.emergencyEmoji}>🆘</Text>
            <Text style={styles.emergencyText}>{t.emergency}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  formContainer: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 30,
    width: width * 0.9,
    maxWidth: 400,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  avatarContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f97316',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarEmoji: {
    fontSize: 40,
  },
  subtitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 15,
    textAlign: 'center',
  },
  passwordInput: {
    borderWidth: 2,
    borderColor: '#d1d5db',
    borderRadius: 12,
    padding: 15,
    fontSize: 18,
    marginBottom: 20,
    textAlign: 'center',
    letterSpacing: 2,
  },
  biometricButton: {
    borderWidth: 2,
    borderColor: '#d1d5db',
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  biometricButtonVerified: {
    borderColor: '#059669',
    backgroundColor: '#f0fdf4',
  },
  biometricText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
  },
  biometricTextVerified: {
    color: '#059669',
  },
  activateButton: {
    backgroundColor: '#2563eb',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginBottom: 20,
  },
  activateButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  activateButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  languageContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  languageLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginRight: 10,
  },
  languageButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    marginHorizontal: 5,
  },
  languageButtonActive: {
    backgroundColor: '#dbeafe',
  },
  languageButtonText: {
    fontSize: 14,
    color: '#6b7280',
  },
  languageButtonTextActive: {
    color: '#2563eb',
    fontWeight: '600',
  },
  emergencyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
  },
  emergencyEmoji: {
    fontSize: 20,
    marginRight: 8,
  },
  emergencyText: {
    color: '#dc2626',
    fontSize: 16,
    fontWeight: '600',
  },
});
