import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet } from 'react-native';

import ChildPasswordEntry from './src/screens/ChildPasswordEntry';
import ChildDashboard from './src/screens/ChildDashboard';
import ContentBlocked from './src/screens/ContentBlocked';
import VPNAlert from './src/screens/VPNAlert';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator 
        initialRouteName="ChildPasswordEntry"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#2563eb',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="ChildPasswordEntry" 
          component={ChildPasswordEntry}
          options={{ 
            title: 'CITTAA Safe Zone',
            headerShown: false 
          }}
        />
        <Stack.Screen 
          name="ChildDashboard" 
          component={ChildDashboard}
          options={{ 
            title: 'Safe Zone Dashboard',
            headerLeft: () => null,
            gestureEnabled: false
          }}
        />
        <Stack.Screen 
          name="ContentBlocked" 
          component={ContentBlocked}
          options={{ 
            title: 'Content Blocked',
            headerShown: false
          }}
        />
        <Stack.Screen 
          name="VPNAlert" 
          component={VPNAlert}
          options={{ 
            title: 'Security Alert',
            headerShown: false
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
