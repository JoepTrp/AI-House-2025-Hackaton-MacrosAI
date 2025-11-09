import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, Image, Alert, TouchableOpacity, Animated, Dimensions, ActivityIndicator, Linking } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import { Ionicons } from '@expo/vector-icons';
import { useUser } from '../context/UserContext';
import * as Notifications from 'expo-notifications'


const SCREEN_WIDTH = Dimensions.get('window').width;
const SCREEN_HEIGHT = Dimensions.get('window').height;

// HomeScreen.js - top of component
  const [isOrdering, setIsOrdering] = useState(false); // Add this
  const [selectedMeals, setSelectedMeals] = useState([]);

export default function HomeScreen({ navigation }) {
  const { user } = useUser();
  const [likedMeals, setLikedMeals] = useState([]);
  const swippedRef = useRef(0);
  const [recipes, setRecipes] = useState([]);
  const [obtainedCards, setObtainedCards] = useState([]);
  const [ingredientsMap, setIngredientsMap] = useState({});

  const isFetchingRef = useRef(false);
  const [isLoading, setIsLoading] = useState(false);

  function chunkArray(arr, chunkSize) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += chunkSize) {
      chunks.push(arr.slice(i, i + chunkSize));
    }
    return chunks;
  }

  const triggerReminderNotification = async (reminder) => {
      try {
        await Notifications.scheduleNotificationAsync({
          content: {
            title: "Restock Reminder",
            body: "You may need to buy " + reminder.item_name + " (last purchased " + reminder.last_purchased_days_ago + " days ago)",
            sound: "default",
            data: { screen: "Home" },
          },
          trigger: { seconds: 0 },
        });
        console.log("Notification scheduled");
      } catch (e) {
        console.error("Error scheduling notification:", e);
      }
    };

  async function fetchReminders() {
    const res = await fetch("http://0.0.0.0:8000/get-reminders");
    const json = await res.json();
    console.log("Reminders happening.", json);
    
    json.reminders.forEach(reminder => {
      triggerReminderNotification(reminder);
    });
  }


  const fetchMealBatch = async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
    setIsLoading(true);

    try {
      console.log('fetchMealBatch: requesting backend.');
      const res = await fetch('http://0.0.0.0:8000/get-meal-batch', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
// HomeScreen.js - inside fetchMealBatch
      const json = await res.json();
      console.log('Returned from backend', json);
      const ideas = Array.isArray(json.ideas) ? json.ideas : [];
      // json.links is now the clean array of recipe objects
      const parsedLinks = Array.isArray(json.links) ? json.links : []; 
      console.log(parsedLinks);
      setObtainedCards(prev => [...prev, ...parsedLinks]); // Store the full objects
      
      const newRecipes = ideas.map((idea, i) => {
        const link = parsedLinks[i]; // link is now the full RecipeLink object
        if (!link) return null; // Safety check

        return {
          id: `${Date.now()}-${i}`,
          name: link.title || idea.recipe_title || `Recipe ${i + 1}`,
          image: '', 
          ingredients: Array.isArray(link.ingredients_per_portion)
            ? link.ingredients_per_portion.map(item => item.name)
            : [],
          link: link.url || '',
          source: link.source || '',
        };
      });

      if (newRecipes.length) {
        setRecipes(prev => [...prev, ...newRecipes]);

        setIngredientsMap(prev => {
          const copy = { ...prev };
          newRecipes.forEach(r => { copy[r.id] = r.ingredients || []; });
          return copy;
        });
      }
    } catch (err) {
      console.error('Error fetching meal batch:', err);
    } finally {
      isFetchingRef.current = false;
      setIsLoading(false);
      
    }
  };

  // initial fetch
  useEffect(() => {
    fetchMealBatch();
    fetchReminders();
  }, []);

  const [selectedMeals, setSelectedMeals] = useState([]);
  const swipeX = useRef(new Animated.Value(0)).current;
  const swiperRef = useRef(null);

  const handleSwipeRight = (cardIndex) => {
    const meal = recipes[cardIndex];
    const newSelectedMeals = [...selectedMeals, meal];
    setSelectedMeals(newSelectedMeals);

    if (newSelectedMeals.length === 7) {
      Alert.alert('Meal Selection Complete', 'You have selected 7 meals! You can proceed with ordering or remove a meal you do not like!', [{ text: 'OK' }]);
    }
  };

  const handleSwipeUp = (cardIndex) => {
    const meal = recipes[cardIndex];// avoid duplicates
    setLikedMeals((prev) => {
     if (prev.find((m) => m.id === meal.id)) return prev;
      return [...prev, meal];
    });
    Alert.alert('Saved', `${meal.name} added to liked meals`);
  };

// HomeScreen.js - replace the old handleDone function
  const handleDone = async () => {
    if (selectedMeals.length === 0) {
      Alert.alert('No meals selected', 'Please select some meals first.');
      return;
    }
    if (isOrdering) return; // Prevent double-taps

    setIsOrdering(true);

    try {
      // Find the full RecipeLink objects that correspond to the simplified selectedMeals
      const selectedFullLinks = selectedMeals.map(selectedMeal => {
        // Find the index of this meal in the 'recipes' array to find its full data
        const index = recipes.findIndex(r => r.id === selectedMeal.id);
        if (index > -1) {
          return obtainedCards[index]; // Return the full data object from obtainedCards
        }
        return null;
      }).filter(Boolean); // Filter out any nulls

      // This is the payload your endpoint expects: { "links": [...] }
      const payload = {
        links: selectedFullLinks
      };

      console.log("Calling /get-grocery-items with:", JSON.stringify(payload));

      // Call the API
      const res = await fetch('http://0.0.0.0:8000/get-grocery-items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error('Failed to get grocery list from backend.');
      }

      const groceryList = await res.json();
      console.log('Got grocery list:', groceryList);

      // Now navigate to the OrderSummary screen, passing the AI-generated list
      navigation.navigate("OrderSummary", {
        // Pass the new groceryList. Your OrderSummary screen will need to be
        // updated to display this data instead of selectedMeals/ingredientsMap
        groceryList: groceryList, 
        
        // Pass these for continuity, though OrderSummary may not need them now
        selectedMeals: selectedMeals, 
        clearMeals: () => setSelectedMeals([]),
      });

    } catch (err) {
      console.error('Error during ordering:', err);
      Alert.alert('Order Failed', err.message || 'Could not connect to the server.');
    } finally {
      setIsOrdering(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Welcome back!</Text>

        <TouchableOpacity 
          style={[styles.doneButton, isOrdering && styles.disabledButton]} 
          onPress={handleDone}
          disabled={isOrdering}
        >
          {isOrdering ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Order</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Swiper */}
      <View style={styles.swiperContainer}>
        <Swiper
          ref={swiperRef}
          key={recipes.length}
          cards={recipes}
          stackSize={3}
          cardIndex={0}
          verticalSwipe={true}
          onSwiping={(x) => swipeX.setValue(x)}
          onSwipedRight={(cardIndex) => {
            handleSwipeRight(cardIndex);
            swipeX.setValue(0);
            swippedRef.current += 1;
            const remaining = recipes.length - (cardIndex + 1);
            if (remaining < 3) fetchMealBatch();
          }}
          onSwipedLeft={(cardIndex) => {
            swipeX.setValue(0);
            swippedRef.current += 1;
            const remaining = recipes.length - (cardIndex + 1);
            if (remaining < 3) fetchMealBatch();
          }}
          onSwipedTop={(cardIndex) => {
            handleSwipeUp(cardIndex);
            swipeX.setValue(0);
            swippedRef.current += 1;
            const remaining = recipes.length - (cardIndex + 1);
            if (remaining < 3) fetchMealBatch();
          }}
          backgroundColor="transparent"
          animateCardOpacity
          cardHorizontalMargin={0}
          renderCard={(card) => {
            const backgroundColor = swipeX.interpolate({
              inputRange: [-SCREEN_WIDTH / 2, 0, SCREEN_WIDTH / 2],
              outputRange: ['rgba(255,0,0,0.3)', 'transparent', 'rgba(0,255,0,0.3)'],
              extrapolate: 'clamp',
            });

            return (
              <Animated.View style={[styles.card, { backgroundColor }]}>
                    {/* Image takes 3/4 of card */}
                    <Image
                        source={{uri: card.image || "https://placehold.co/600x400"}}
                        style={styles.cardImage}
                        resizeMode="cover"
                    />

                    {/* Bottom info area */}
                    <View style={styles.infoContainer}>
                        <Text style={styles.cardTitle}>{card.name}</Text>
                        <Text style={styles.cardIngredients}>
                        {ingredientsMap[card.id].join(', ')}
                        </Text>
                        <TouchableOpacity onPress={() => Linking.openURL(card.link)}>
                          <Text style={{fontSize: 16, color: '#45b6fe', marginBottom:10}}>{card.source}</Text>
                      </TouchableOpacity>
                    </View>
                </Animated.View>

            );
          }}
        />
        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#FF6B00" />
            <Text style={{ marginTop: 8, color: '#333' }}>Loading more recipes…</Text>
          </View>
        )}

      </View>

      {/* Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.editButton} onPress={() => navigation.navigate('EditRecipes', { selectedMeals })}>
          <Text style={styles.buttonText}>Edit</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.doneButton} onPress={() => handleDone()}>
          <Text style={styles.buttonText} >Order</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 60, paddingHorizontal: 20 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  title: { fontSize: 30, fontWeight: '600' },
  iconButton: { padding: 8 },
  swiperContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: {
    width: SCREEN_WIDTH * 0.9,
    height: SCREEN_HEIGHT * 0.6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#ddd',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    alignSelf: 'center',
    backgroundColor: '#fff',
    alignSelf: "center",
    marginRight:35,
  },
  // HomeScreen.js - in StyleSheet.create
  doneButton: { ... },
  disabledButton: {
    backgroundColor: '#FFB073', // A lighter/faded color
  },
  editButton: { ... },
  cardImage: { width: '100%', height: 200, borderRadius: 10, marginBottom: 15 },
  cardTitle: { fontSize: 22, fontWeight: 'bold', marginBottom: 5, textAlign: 'left' },
  cardIngredients: { fontSize: 16, color: '#555', marginBottom:10},
  infoContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
    overflow: 'hidden'
    },
  buttonContainer: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 20, zIndex:10, paddingBottom:50 },
  doneButton: {
    backgroundColor: '#FF6B00',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    marginLeft: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  editButton: {
    backgroundColor: '#888',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    marginRight: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  buttonText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255,255,255,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10000,
  },

});
