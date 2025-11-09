import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, Image, Alert, TouchableOpacity, Animated, Dimensions, ActivityIndicator, Linking } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import { Ionicons } from '@expo/vector-icons';
import { useUser } from '../context/UserContext';


const SCREEN_WIDTH = Dimensions.get('window').width;
const SCREEN_HEIGHT = Dimensions.get('window').height;

export default function HomeScreen({ navigation }) {
  const { user } = useUser();
  const [likedMeals, setLikedMeals] = useState([]);
  const swippedRef = useRef(0);
  const [recipes, setRecipes] = useState([]);

  const [ingredientsMap, setIngredientsMap] = useState({}
  );

  const isFetchingRef = useRef(false);
  const [isLoading, setIsLoading] = useState(false);

  function chunkArray(arr, chunkSize) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += chunkSize) {
      chunks.push(arr.slice(i, i + chunkSize));
    }
    return chunks;
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
      const json = await res.json();
      console.log('Returned from backend', json);

      const ideas = Array.isArray(json.ideas) ? json.ideas : [];
      const linkChunks = chunkArray(json.links, 4); 
      const parsedLinks = linkChunks.map(chunk => Object.fromEntries(chunk));

      const newRecipes = ideas.map((idea, i) => {
        const link = parsedLinks[i];

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

  const handleDone = () => {
    if (selectedMeals.length === 0) {
      Alert.alert('No meals selected', 'Please select some meals first.');
      return;
    }
    navigation.navigate("OrderSummary", {selectedMeals, ingredientsMap, clearMeals: () => setSelectedMeals([])});
  };

  if (recipes.length === 0) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        {isLoading ? (
          <>
            <ActivityIndicator size="large" color="#FF6B00" />
            <Text style={{ marginTop: 12 }}>Loading recipes…</Text>
          </>
        ) : (
          <>
            <Text style={{ marginBottom: 12 }}>No recipes loaded.</Text>
            <TouchableOpacity
              style={{ backgroundColor: '#FF6B00', padding: 12, borderRadius: 8 }}
              onPress={() => fetchMealBatch()}
            >
              <Text style={{ color: '#fff', fontWeight: '700' }}>Retry</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Welcome back!</Text>

        <TouchableOpacity style={styles.iconButton} onPress={() => navigation.navigate('Settings')}>
          <Ionicons name="cart-outline" size={24} color="#333" />
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
    zIndex: 100,
  },

});
