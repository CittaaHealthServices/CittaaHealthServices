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

interface ContentBlockedProps {
  navigation: any;
}

export default function ContentBlocked({ navigation }: ContentBlockedProps) {
  const alternativeContent = [
    { title: 'Educational Videos', icon: 'play-circle', color: '#3b82f6' },
    { title: 'Study Materials', icon: 'book', color: '#10b981' },
    { title: 'Creative Activities', icon: 'brush', color: '#8b5cf6' },
    { title: 'Approved Games', icon: 'game-controller', color: '#f59e0b' },
  ];

  const handleRequestReview = () => {
    navigation.navigate('ChildDashboard');
  };

  const handleBackToSafeZone = () => {
    navigation.navigate('ChildDashboard');
  };

  const handleContactSupport = () => {
    console.log('Contacting support...');
  };

  return (
    <ScrollView style={styles.container}>
      <LinearGradient
        colors={['#dc2626', '#ef4444']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.iconContainer}>
            <Ionicons name="shield-outline" size={80} color="#fff" />
            <View style={styles.blockIcon}>
              <Ionicons name="close" size={40} color="#dc2626" />
            </View>
          </View>
          <Text style={styles.title}>🛡️ Content Blocked</Text>
        </View>
      </LinearGradient>

      <View style={styles.content}>
        <View style={styles.messageContainer}>
          <Text style={styles.messageTitle}>This content is not suitable for your age group.</Text>
          <Text style={styles.messageSubtitle}>
            Your safety is our priority. This content has been blocked to protect you.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Instead, try these:</Text>
          
          <View style={styles.alternativesGrid}>
            {alternativeContent.map((item, index) => (
              <TouchableOpacity key={index} style={[styles.alternativeCard, { borderLeftColor: item.color }]}>
                <Ionicons name={item.icon as any} size={32} color={item.color} />
                <Text style={styles.alternativeTitle}>{item.title}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.actionsContainer}>
          <TouchableOpacity style={styles.primaryButton} onPress={handleRequestReview}>
            <Ionicons name="person" size={20} color="#fff" />
            <Text style={styles.primaryButtonText}>Request Parent Review</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.secondaryButton} onPress={handleBackToSafeZone}>
            <Ionicons name="home" size={20} color="#2563eb" />
            <Text style={styles.secondaryButtonText}>Back to Safe Zone</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.supportSection}>
          <Text style={styles.supportText}>Need help?</Text>
          <TouchableOpacity style={styles.supportButton} onPress={handleContactSupport}>
            <Ionicons name="chatbubble-ellipses" size={16} color="#6b7280" />
            <Text style={styles.supportButtonText}>Contact Support</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoSection}>
          <View style={styles.infoCard}>
            <Ionicons name="information-circle" size={24} color="#3b82f6" />
            <View style={styles.infoContent}>
              <Text style={styles.infoTitle}>Why was this blocked?</Text>
              <Text style={styles.infoText}>
                Our AI system detected content that may not be appropriate for children. 
                This helps keep you safe while browsing.
              </Text>
            </View>
          </View>

          <View style={styles.infoCard}>
            <Ionicons name="time" size={24} color="#10b981" />
            <View style={styles.infoContent}>
              <Text style={styles.infoTitle}>What happens next?</Text>
              <Text style={styles.infoText}>
                Your parents have been notified. You can continue using approved content 
                or request a review if you think this was a mistake.
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.statsContainer}>
          <Text style={styles.statsTitle}>Your Safety Stats Today</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>12</Text>
              <Text style={styles.statLabel}>Sites Protected</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>3h 45m</Text>
              <Text style={styles.statLabel}>Safe Browsing</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>100%</Text>
              <Text style={styles.statLabel}>Protection Rate</Text>
            </View>
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
  iconContainer: {
    position: 'relative',
    marginBottom: 20,
  },
  blockIcon: {
    position: 'absolute',
    bottom: -10,
    right: -10,
    backgroundColor: '#fff',
    borderRadius: 25,
    padding: 5,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  content: {
    padding: 20,
  },
  messageContainer: {
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
  messageTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 10,
  },
  messageSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  section: {
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
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 15,
    textAlign: 'center',
  },
  alternativesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  alternativeCard: {
    width: '48%',
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
    borderLeftWidth: 4,
  },
  alternativeTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
    marginTop: 8,
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
  supportSection: {
    alignItems: 'center',
    marginBottom: 20,
  },
  supportText: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  supportButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
  },
  supportButtonText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 5,
  },
  infoSection: {
    marginBottom: 20,
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  infoContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 12,
    color: '#6b7280',
    lineHeight: 16,
  },
  statsContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
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
  statCard: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 10,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
});
