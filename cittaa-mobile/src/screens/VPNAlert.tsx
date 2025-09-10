import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface VPNAlertProps {
  navigation: any;
}

export default function VPNAlert({ navigation }: VPNAlertProps) {
  const handleUnderstandWhy = () => {
    console.log('Showing VPN education...');
  };

  const handleReturnToSafeZone = () => {
    navigation.navigate('ChildDashboard');
  };

  const handleContactParents = () => {
    console.log('Contacting parents...');
  };

  return (
    <ScrollView style={styles.container}>
      <LinearGradient
        colors={['#dc2626', '#ef4444', '#f87171']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.alertIconContainer}>
            <Ionicons name="warning" size={80} color="#fff" />
          </View>
          <Text style={styles.title}>🚨 Security Alert</Text>
          <Text style={styles.subtitle}>VPN Connection Detected and Blocked</Text>
        </View>
      </LinearGradient>

      <View style={styles.content}>
        <View style={styles.alertCard}>
          <View style={styles.alertHeader}>
            <Ionicons name="shield-checkmark" size={32} color="#10b981" />
            <Text style={styles.alertTitle}>Your Safety is Protected</Text>
          </View>
          
          <View style={styles.alertDetails}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Device:</Text>
              <Text style={styles.detailValue}>Aarav's Phone</Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Time:</Text>
              <Text style={styles.detailValue}>Just now</Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>App:</Text>
              <Text style={styles.detailValue}>TurboVPN</Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Status:</Text>
              <Text style={[styles.detailValue, styles.statusBlocked]}>Installation Prevented</Text>
            </View>
          </View>
        </View>

        <View style={styles.notificationCard}>
          <Ionicons name="notifications" size={24} color="#3b82f6" />
          <View style={styles.notificationContent}>
            <Text style={styles.notificationTitle}>Parents Notified</Text>
            <Text style={styles.notificationText}>
              Your parents have been automatically notified via WhatsApp and email about this security event.
            </Text>
          </View>
        </View>

        <View style={styles.educationSection}>
          <Text style={styles.educationTitle}>Why VPNs are Blocked</Text>
          
          <View style={styles.reasonCard}>
            <Ionicons name="eye-off" size={20} color="#8b5cf6" />
            <View style={styles.reasonContent}>
              <Text style={styles.reasonTitle}>Bypass Prevention</Text>
              <Text style={styles.reasonText}>VPNs can bypass safety filters that protect you from harmful content.</Text>
            </View>
          </View>

          <View style={styles.reasonCard}>
            <Ionicons name="location" size={20} color="#f59e0b" />
            <View style={styles.reasonContent}>
              <Text style={styles.reasonTitle}>Location Safety</Text>
              <Text style={styles.reasonText}>VPNs hide your real location, making it harder to keep you safe online.</Text>
            </View>
          </View>

          <View style={styles.reasonCard}>
            <Ionicons name="people" size={20} color="#10b981" />
            <View style={styles.reasonContent}>
              <Text style={styles.reasonTitle}>Family Trust</Text>
              <Text style={styles.reasonText}>Open internet use helps maintain trust between you and your parents.</Text>
            </View>
          </View>
        </View>

        <View style={styles.actionsContainer}>
          <TouchableOpacity style={styles.primaryButton} onPress={handleUnderstandWhy}>
            <Ionicons name="school" size={20} color="#fff" />
            <Text style={styles.primaryButtonText}>Understand Why</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.secondaryButton} onPress={handleReturnToSafeZone}>
            <Ionicons name="home" size={20} color="#2563eb" />
            <Text style={styles.secondaryButtonText}>Return to Safe Zone</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.emergencySection}>
          <Text style={styles.emergencyTitle}>Need to Talk?</Text>
          <TouchableOpacity style={styles.emergencyButton} onPress={handleContactParents}>
            <Ionicons name="call" size={20} color="#dc2626" />
            <Text style={styles.emergencyButtonText}>Contact Parents Now</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.securityStats}>
          <Text style={styles.statsTitle}>Security Protection Today</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>3</Text>
              <Text style={styles.statLabel}>VPN Blocks</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>12</Text>
              <Text style={styles.statLabel}>Content Filters</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>100%</Text>
              <Text style={styles.statLabel}>Protection Rate</Text>
            </View>
          </View>
        </View>

        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>💡 Safe Browsing Tips</Text>
          <View style={styles.tipsList}>
            <Text style={styles.tipItem}>• Use approved educational websites</Text>
            <Text style={styles.tipItem}>• Ask parents before downloading new apps</Text>
            <Text style={styles.tipItem}>• Report suspicious content immediately</Text>
            <Text style={styles.tipItem}>• Keep your device updated and secure</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerContent: {
    alignItems: 'center',
  },
  alertIconContainer: {
    marginBottom: 15,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#fff',
    textAlign: 'center',
    opacity: 0.9,
  },
  content: {
    padding: 20,
  },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  alertTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginLeft: 12,
  },
  alertDetails: {
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    padding: 15,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: 14,
    color: '#1f2937',
    fontWeight: '600',
  },
  statusBlocked: {
    color: '#dc2626',
  },
  notificationCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  notificationContent: {
    flex: 1,
    marginLeft: 15,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 5,
  },
  notificationText: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  educationSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  educationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 15,
    textAlign: 'center',
  },
  reasonCard: {
    flexDirection: 'row',
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
  },
  reasonContent: {
    flex: 1,
    marginLeft: 12,
  },
  reasonTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  reasonText: {
    fontSize: 12,
    color: '#6b7280',
    lineHeight: 16,
  },
  actionsContainer: {
    marginBottom: 20,
  },
  primaryButton: {
    backgroundColor: '#2563eb',
    borderRadius: 12,
    padding: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  secondaryButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#2563eb',
  },
  secondaryButtonText: {
    color: '#2563eb',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  emergencySection: {
    backgroundColor: '#fef2f2',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  emergencyTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 10,
  },
  emergencyButton: {
    backgroundColor: '#dc2626',
    borderRadius: 8,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  emergencyButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  securityStats: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 15,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#dc2626',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  tipsSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 15,
    textAlign: 'center',
  },
  tipsList: {
    paddingLeft: 10,
  },
  tipItem: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 8,
    lineHeight: 20,
  },
});
