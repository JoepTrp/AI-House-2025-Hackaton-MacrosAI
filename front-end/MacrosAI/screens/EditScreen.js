import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Dimensions, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SCREEN_WIDTH = Dimensions.get('window').width;
const SCREEN_HEIGHT = Dimensions.get('window').height;

export default function EditRecipesScreen({ navigation, route }) {
  const { selectedMeals } = route.params; // passed from previous screen
  const [meals, setMeals] = useState(selectedMeals);

  const deleteMeal = (id) => {
    setMeals((prevMeals) => prevMeals.filter((meal) => meal.id !== id));
  };

  const renderItem = ({ item }) => (
    <View style={styles.itemContainer}>
      {/* Meal Image */}
      <Image source={{ uri: item.image }} style={styles.image} />

      {/* Meal Name */}
      <Text style={styles.name}>{item.name}</Text>

      {/* Delete Button */}
      <TouchableOpacity onPress={() => deleteMeal(item.id)} style={styles.deleteButton}>
        <Ionicons name="trash" size={24} color="white" />
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text>Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Edit Meals</Text>
        <View style={{ width: 28 }} />
      </View>

      {meals.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No meals selected!</Text>
        </View>
      ) : (
        <FlatList
          data={meals}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 60, paddingHorizontal: 20 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  title: { fontSize: 22, fontWeight: '600' },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { fontSize: 18, color: '#888' },
  itemContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderColor: '#eee',
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 10,
  },
  image: { width: 50, height: 50, borderRadius: 5, marginRight: 15 },
  name: { flex: 1, fontSize: 16 },
  deleteButton: {
    backgroundColor: 'red',
    padding: 8,
    borderRadius: 5,
  },
});
