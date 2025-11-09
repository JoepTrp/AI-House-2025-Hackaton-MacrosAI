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
import * as Notifications from 'expo-notifications';
import { useEffect } from 'react';

// iOS: show notifications even in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

async function registerForPushNotificationsAsync() {
  let token;
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    alert('Failed to get push token!');
    return;
  }

  token = (await Notifications.getExpoPushTokenAsync()).data;
  console.log('Expo Push Token:', token);

  // Send the token to your server
  // await fetch('https://your-server.com/api/save-token', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ token }),
  // });

  return token;
}


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
  useEffect(() => {
    registerForPushNotificationsAsync();
  }, []);

  useEffect(() => {
  const notificationListener = Notifications.addNotificationReceivedListener(notification => {
    console.log('Notification received in foreground:', notification);
  });

  const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
    console.log('User tapped notification:', response);
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
