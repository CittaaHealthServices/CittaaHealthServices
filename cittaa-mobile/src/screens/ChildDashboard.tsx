import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface ChildDashboardProps {
  route: any;
  navigation: any;
}

export default function ChildDashboard({ route, navigation }: ChildDashboardProps) {
  const [childData, setChildData] = useState(route.params?.childData || {});
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const learningGoals = [
    { subject: 'Math Practice', target: 30, completed: 30, unit: 'mins' },
    { subject: 'Science Reading', target: 45, completed: 20, unit: 'mins' },
    { subject: 'English Writing', target: 20, completed: 0, unit: 'mins' },
  ];

  const recommendedContent = [
    { title: 'NCERT Math', icon: '📚', color: '#3b82f6' },
    { title: 'Khan Academy', icon: '🎓', color: '#10b981' },
    { title: "Byju's", icon: '📖', color: '#8b5cf6' },
  ];

  const handleEmergencyCall = () => {
    Alert.alert(
      'Emergency Call',
      'This will immediately contact your parents. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Call Now', onPress: () => Alert.alert('Calling...', 'Contacting parents...') }
      ]
    );
  };

  const getProgressColor = (completed: number, target: number) => {
    const percentage = (completed / target) * 100;
    if (percentage >= 100) return '#10b981';
    if (percentage >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <ScrollView style={styles.container}>
      <LinearGradient
        colors={['#2563eb', '#3b82f6']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.welcomeSection}>
            <View style={styles.avatarContainer}>
              <Text style={styles.avatarEmoji}>👦</Text>
            </View>
            <View>
              <Text style={styles.welcomeText}>Welcome Aarav! 📚</Text>
              <View style={styles.statusContainer}>
                <View style={styles.statusDot} />
                <Text style={styles.statusText}>Safe Zone ON</Text>
              </View>
            </View>
          </View>
          <Text style={styles.timeText}>
            {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </Text>
        </View>
      </LinearGradient>

      <View style={styles.content}>
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="trophy" size={24} color="#2563eb" />
            <Text style={styles.sectionTitle}>Today's Learning Goals</Text>
          </View>
          
          {learningGoals.map((goal, index) => (
            <View key={index} style={styles.goalItem}>
              <View style={styles.goalHeader}>
                <Text style={styles.goalSubject}>{goal.subject}</Text>
                <Text style={styles.goalProgress}>
                  {goal.completed}/{goal.target} {goal.unit}
                  {goal.completed >= goal.target && ' ✓'}
                </Text>
              </View>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    {
                      width: `${Math.min((goal.completed / goal.target) * 100, 100)}%`,
                      backgroundColor: getProgressColor(goal.completed, goal.target),
                    },
                  ]}
                />
              </View>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="book" size={24} color="#8b5cf6" />
            <Text style={styles.sectionTitle}>Recommended Content</Text>
          </View>
          
          <View style={styles.contentGrid}>
            {recommendedContent.map((content, index) => (
              <TouchableOpacity key={index} style={[styles.contentCard, { borderLeftColor: content.color }]}>
                <Text style={styles.contentIcon}>{content.icon}</Text>
                <Text style={styles.contentTitle}>{content.title}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="game-controller-outline" size={24} color="#f59e0b" />
            <Text style={styles.sectionTitle}>Approved Games</Text>
          </View>
          
          <View style={styles.gamesContainer}>
            <Text style={styles.gamesText}>🎮 2 hours left today</Text>
            <TouchableOpacity style={styles.gamesButton}>
              <Text style={styles.gamesButtonText}>View Games</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="musical-notes" size={24} color="#10b981" />
            <Text style={styles.sectionTitle}>Music & Stories</Text>
          </View>
          
          <TouchableOpacity style={styles.musicButton}>
            <Ionicons name="play-circle" size={32} color="#10b981" />
            <Text style={styles.musicText}>Listen to Stories</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.emergencyButton} onPress={handleEmergencyCall}>
          <Text style={styles.emergencyEmoji}>🆘</Text>
          <Text style={styles.emergencyText}>Emergency Parent Call</Text>
        </TouchableOpacity>

        <View style={styles.languageSelector}>
          <TouchableOpacity style={styles.languageButton}>
            <Text style={styles.languageText}>हिंदी</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.languageButton, styles.languageButtonActive]}>
            <Text style={[styles.languageText, styles.languageTextActive]}>English</Text>
          </TouchableOpacity>
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
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  welcomeSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  avatarEmoji: {
    fontSize: 24,
  },
  welcomeText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#10b981',
    marginRight: 8,
  },
  statusText: {
    color: '#fff',
    fontSize: 14,
  },
  timeText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  content: {
    padding: 20,
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
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginLeft: 10,
  },
  goalItem: {
    marginBottom: 15,
  },
  goalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  goalSubject: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  goalProgress: {
    fontSize: 14,
    color: '#6b7280',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  contentGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  contentCard: {
    flex: 1,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    padding: 15,
    marginHorizontal: 5,
    alignItems: 'center',
    borderLeftWidth: 4,
  },
  contentIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  contentTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
  },
  gamesContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  gamesText: {
    fontSize: 16,
    color: '#374151',
  },
  gamesButton: {
    backgroundColor: '#f59e0b',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
  },
  gamesButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  musicButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f0fdf4',
    padding: 15,
    borderRadius: 8,
  },
  musicText: {
    fontSize: 16,
    color: '#10b981',
    fontWeight: '600',
    marginLeft: 10,
  },
  emergencyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fef2f2',
    padding: 15,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  emergencyEmoji: {
    fontSize: 24,
    marginRight: 10,
  },
  emergencyText: {
    color: '#dc2626',
    fontSize: 16,
    fontWeight: 'bold',
  },
  languageSelector: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 20,
  },
  languageButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    marginHorizontal: 5,
    backgroundColor: '#f3f4f6',
  },
  languageButtonActive: {
    backgroundColor: '#dbeafe',
  },
  languageText: {
    fontSize: 14,
    color: '#6b7280',
  },
  languageTextActive: {
    color: '#2563eb',
    fontWeight: '600',
  },
});
