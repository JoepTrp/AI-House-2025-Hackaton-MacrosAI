import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

export default function OrderSummaryScreen({ navigation, route }) {
  const { selectedMeals, ingredientsMap, clearMeals } = route.params;

  // Count ingredients
  const ingredientCount = {};
  selectedMeals.forEach(meal => {
    const ingredients = ingredientsMap[meal.id] || [];
    ingredients.forEach(ingredient => {
      if (ingredientCount[ingredient]) {
        ingredientCount[ingredient] += 1;
      } else {
        ingredientCount[ingredient] = 1;
      }
    });
  });

  const mealsList = selectedMeals.map(m => m.name).join(', ');
  const ingredientsList = Object.entries(ingredientCount)
    .map(([ingredient, count]) => (count > 1 ? `${count}x ${ingredient}` : ingredient))
    .join('\n');

  return (
    <View style={styles.container}>
        <View style={styles.header}>
            <Text style={styles.title}>Order Summary</Text>
        </View>
      <ScrollView style={styles.scrollContainer}>
        <Text style={styles.heading}>MEALS</Text>
        <Text style={styles.text}>{mealsList}</Text>

        <Text style={[styles.heading, { marginTop: 20 }]}>INGREDIENTS</Text>
        <Text style={styles.text}>{ingredientsList}</Text>
      </ScrollView>

      {/* Buttons at the bottom */}
      <View style={styles.buttonsContainer}>
        <TouchableOpacity
          style={[styles.button, styles.cancelButton]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.buttonText}>Cancel</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.confirmButton]}
          onPress={() => {
            alert('Order Confirmed!');
            clearMeals();
            navigation.goBack();
          }}
        >
          <Text style={styles.buttonText}>Confirm</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 60, paddingHorizontal: 20 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  title: { fontSize: 30, fontWeight: '600' },
  scrollContainer: { flex: 1, padding: 20 },
  heading: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  text: { fontSize: 16, lineHeight: 24 },
  buttonsContainer: { flexDirection: 'row', padding: 20, justifyContent: 'space-between' },
  button: { flex: 1, padding: 15, borderRadius: 10, alignItems: 'center', marginHorizontal: 5 },
  cancelButton: { backgroundColor: 'gray' },
  confirmButton: { backgroundColor: '#FF6B00' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
