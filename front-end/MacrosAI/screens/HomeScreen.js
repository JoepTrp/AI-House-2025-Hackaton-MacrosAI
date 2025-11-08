import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, Image, Alert, TouchableOpacity, Animated, Dimensions } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import { Ionicons } from '@expo/vector-icons';
import { useUser } from '../context/UserContext';

const SCREEN_WIDTH = Dimensions.get('window').width;
const SCREEN_HEIGHT = Dimensions.get('window').height;

export default function HomeScreen({ navigation }) {
  const { user } = useUser();

  const [recipes, setRecipes] = useState([
    { id: '1', name: 'Spaghetti Bolognese' },
    { id: '2', name: 'Lasagna' },
    { id: '3', name: 'Chicken Tikka Masala' },
    { id: '4', name: 'Sushi' },
    { id: '5', name: 'Fried Rice' },
    { id: '6', name: 'Burger' },
    { id: '7', name: 'Tacos' },
    { id: '8', name: 'Salad' },
    { id: '9', name: 'Pizza' },
  ]);

  const ingredientsMap = {
    '1': ['Spaghetti', 'Tomato sauce', 'Ground beef', 'Onion', 'Garlic'],
    '2': ['Lasagna noodles', 'Ricotta', 'Mozzarella', 'Tomato sauce', 'Ground beef'],
    '3': ['Chicken', 'Yogurt', 'Tikka spices', 'Tomato', 'Onion'],
    '4': ['Sushi rice', 'Nori', 'Fish or veg', 'Soy sauce', 'Wasabi'],
    '5': ['Rice', 'Eggs', 'Vegetables', 'Soy sauce', 'Oil'],
    '6': ['Buns', 'Beef patty', 'Cheese', 'Lettuce', 'Tomato'],
    '7': ['Tortilla', 'Chicken', 'Cheese', 'Lettuce', 'Salsa'],
    '8': ['Lettuce', 'Tomato', 'Cucumber', 'Olives', 'Dressing'],
    '9': ['Pizza base', 'Tomato sauce', 'Cheese', 'Pepperoni', 'Olives'],
  };

  const [selectedMeals, setSelectedMeals] = useState([]);
  const swipeX = useRef(new Animated.Value(0)).current;
  const swiperRef = useRef(null);

  const handleSwipeRight = (cardIndex) => {
    const meal = recipes[cardIndex];
    const newSelectedMeals = [...selectedMeals, meal];
    setSelectedMeals(newSelectedMeals);

    if (newSelectedMeals.length === 7) {
      Alert.alert('Meal Selection Complete', 'You have selected 7 meals!', [{ text: 'OK' }]);
    }
  };

  const handleDone = () => {
    if (selectedMeals.length === 0) {
      Alert.alert('No meals selected', 'Please select some meals first.');
      return;
    }
    Alert.alert('Selected Meals', selectedMeals.map((m) => m.name).join('\n'), [{ text: 'OK' }]);
  };

  const handleEdit = () => {
    Alert.alert(
      'Edit Recipes',
      'Swipe a recipe card to delete it or remove from list.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete Top Card',
          onPress: () => {
            if (recipes.length > 0) {
              const newRecipes = [...recipes];
              newRecipes.shift();
              setRecipes(newRecipes);
            }
          },
          style: 'destructive',
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Welcome, {user?.username || 'Guest'} 👋</Text>

        <TouchableOpacity style={styles.iconButton} onPress={() => navigation.navigate('Settings')}>
          <Ionicons name="settings-outline" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* Swiper */}
      <View style={styles.swiperContainer}>
        <Swiper
          ref={swiperRef}
          cards={recipes}
          stackSize={3}
          cardIndex={0}
          verticalSwipe={false}
          onSwiping={(x) => swipeX.setValue(x)}
          onSwipedRight={(cardIndex) => {
            handleSwipeRight(cardIndex);
            swipeX.setValue(0); 
          }}
          onSwipedLeft={() => swipeX.setValue(0)} 
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
                <Image
                  source={{ uri: 'https://via.placeholder.com/300x180' }}
                  style={styles.cardImage}
                  resizeMode="cover"
                />
                <Text style={styles.cardTitle}>{card.name}</Text>
                <Text style={styles.cardIngredients}>
                  {ingredientsMap[card.id].join(', ')}
                </Text>
              </Animated.View>
            );
          }}
        />
      </View>

      {/* Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.editButton}>
          <Text style={styles.buttonText}>Edit</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.doneButton}>
          <Text style={styles.buttonText}>Done</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 60, paddingHorizontal: 20 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  title: { fontSize: 22, fontWeight: '600' },
  iconButton: { padding: 8 },
  swiperContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: {
    width: SCREEN_WIDTH * 0.9,
    height: SCREEN_HEIGHT * 0.6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#ddd',
    justifyContent: 'flex-start',
    alignItems: 'center',
    padding: 20,
    alignSelf: 'center',
    backgroundColor: '#f5f5f5',
    alignSelf: "center"
  },
  cardImage: { width: '100%', height: 200, borderRadius: 10, marginBottom: 15 },
  cardTitle: { fontSize: 22, fontWeight: 'bold', marginBottom: 5, textAlign: 'center' },
  cardIngredients: { fontSize: 16, color: '#555', textAlign: 'center' },
  buttonContainer: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 20 },
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
});
