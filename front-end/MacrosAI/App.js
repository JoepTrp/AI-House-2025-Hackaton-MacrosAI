import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import {createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { UserProvider, useUser } from './context/UserContext';
import LoginScreen from './screens/LoginScreen';
import OnboardingScreenOne from './screens/onboarding/OnboardingScreen1';
import HomeScreen from './screens/HomeScreen';
import  SettingsScreen  from './screens/Settings';
import EditRecipesScreen from './screens/EditScreen';
import OrderSummaryScreen from './screens/OrderSummaryScreen';
import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';
import { useEffect, useState } from 'react';


const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();



// function MainTabs() {
//   return (
//     <Tab.Navigator
//       screenOptions={({ route }) => ({
//         headerShown: false,
//         tabBarIcon: ({ color, size }) => {
//           if (route.name === 'Home') {
//             return <Ionicons name="home-outline" size={size} color={color} />;
//           }
//           if (route.name === 'Pantry') {
//             return <Ionicons name="bag-check-outline" size={size} color={color} />;
//           }
//           return null;
//         },
//         tabBarActiveTintColor: '#0066CC',
//         tabBarInactiveTintColor: 'gray',
//       })}
//     >
//       <Tab.Screen name="Home" component={HomeScreen} />
//       <Tab.Screen name="Pantry" component={PantryScreen} />
//     </Tab.Navigator>
//   );
// }

function RootNavigator() {
  const { user } = useUser();
  const [expoPushToken, setExpoPushToken] = useState('');
  const [notification, setNotification] = useState(false);

  console.log(user);

  useEffect(() => {
    // Register device and get token
    registerForPushNotificationsAsync().then(token => setExpoPushToken(token));

    // Listen for incoming notifications when app is foregrounded
    const notificationListener = Notifications.addNotificationReceivedListener(notification => {
      setNotification(notification);
      console.log('Notification Received:', notification);
    });
    //Listen for notifications 
    const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
      console.log('Notification Response:', response);
      // Navigate or handle based on response.notification.request.content.data
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }, []);

  
  return (
    <Stack.Navigator screenOptions={{headerShown:false}}>
      {user ? (
        <>
        {/* <Stack.Screen name="Main" component={MainTabs} /> */}
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Settings" component={SettingsScreen}/>
        <Stack.Screen name="EditRecipes" component={EditRecipesScreen}/>
        <Stack.Screen name="OrderSummary" component={OrderSummaryScreen}/>
        </>
      ) : (
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={OnboardingScreenOne} />
        </>
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <UserProvider>
      <NavigationContainer>
        <RootNavigator />
      </NavigationContainer>
    </UserProvider>
  );
}
