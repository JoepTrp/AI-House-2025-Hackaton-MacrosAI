import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';

export default function OrderSummaryScreen({ navigation, route }) {
  const { selectedMeals, ingredientsMap, clearMeals } = route.params;

  // Count ingredients
  const ingredientCount = {};
  selectedMeals.forEach(meal => {
    (ingredientsMap[meal.id] || []).forEach(ingredient => {
      ingredientCount[ingredient] = (ingredientCount[ingredient] || 0) + 1;
    });
  });

  const [ingredientsState, setIngredientsState] = useState(
    Object.entries(ingredientCount).map(([name, count]) => ({ name, count }))
  );

  const [searchQuery, setSearchQuery] = useState('');

  const removeIngredient = (name) => {
    Alert.alert('Remove', `Remove "${name}" from the list?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: () => setIngredientsState(prev => prev.filter(i => i.name !== name)),
      },
    ]);
  };

  const addProductToIngredients = (product) => {
    setIngredientsState(prev => {
      const idx = prev.findIndex(i => i.name === product.name);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = { ...copy[idx], count: copy[idx].count + 1 };
        return copy;
      }
      return [...prev, { name: product.name, count: 1 }];
    });
  };

  const suggestedProducts = [
    { id: 'p1', name: 'Extra Virgin Olive Oil (500ml)', category: 'Pantry' },
    { id: 'p2', name: 'Sea Salt (500g)', category: 'Pantry' },
    { id: 'p3', name: 'Black Pepper (ground)', category: 'Pantry' },
    { id: 'p4', name: 'Long Grain Rice (1 kg)', category: 'Pantry' },
    { id: 'p5', name: 'Pasta (spaghetti, 500g)', category: 'Pantry' },
    { id: 'p6', name: 'Canned Tomatoes (400g)', category: 'Pantry' },
    { id: 'p7', name: 'Chicken Breast (fresh, 500g)', category: 'Protein' },
    { id: 'p8', name: 'Eggs (dozen)', category: 'Dairy' },
    { id: 'p9', name: 'Greek Yogurt (500g)', category: 'Dairy' },
    { id: 'p10', name: 'Milk (1 L)', category: 'Dairy' },
  ];

  // Filter suggested products based on search query
  const filteredProducts = useMemo(
    () => suggestedProducts.filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase())
    ),
    [searchQuery]
  );

  const mealsList = selectedMeals.map(m => m.name).join(', ');

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Order Summary</Text>

      <Text style={styles.heading}>Meals</Text>
      <Text style={styles.text}>{mealsList}</Text>

      <Text style={[styles.heading, { marginTop: 20 }]}>Ingredients</Text>

      {/* Ingredients List with independent scroll */}
      <FlatList
        data={ingredientsState}
        keyExtractor={(item) => item.name}
        style={styles.ingredientsList}
        renderItem={({ item }) => (
          <View style={styles.ingredientRow}>
            <Text style={styles.text}>
              {item.count > 1 ? `${item.count}x ${item.name}` : item.name}
            </Text>
            <TouchableOpacity onPress={() => removeIngredient(item.name)}>
              <Text style={{ color: '#c00', fontWeight: '700' }}>Remove</Text>
            </TouchableOpacity>
          </View>
        )}
        ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
      />

      {/* Suggested products with search bar */}
      <Text style={[styles.heading, { marginTop: 20 }]}>Suggested products</Text>

      <TextInput
        style={styles.searchInput}
        placeholder="Search products..."
        value={searchQuery}
        onChangeText={setSearchQuery}
      />

      <FlatList
        data={filteredProducts}
        keyExtractor={i => i.id}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.productList}
        renderItem={({ item }) => (
          <View style={styles.productTile}>
            <Text style={styles.productName} numberOfLines={2}>{item.name}</Text>
            <TouchableOpacity
              style={styles.addButton}
              onPress={() => {
                addProductToIngredients(item);
                Alert.alert('Added', `${item.name} added to ingredients`);
              }}
            >
              <Text style={styles.addButtonText}>+ Add</Text>
            </TouchableOpacity>
          </View>
        )}
      />

      {/* Bottom Buttons */}
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
            Alert.alert('Order Confirmed!');
            clearMeals();
            navigation.goBack();
          }}
        >
          <Text style={styles.buttonText}>Confirm</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 60, padding:20 },
  title: { fontSize: 28, fontWeight: '600', marginBottom: 10 },
  heading: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  text: { fontSize: 16, lineHeight: 22 },
  searchInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 8,
    marginBottom: 8,
  },
  ingredientsList: {
    maxHeight: 250, 
    marginBottom: 16,
  },
  ingredientRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#f7f7fb',
    borderRadius: 8,
  },
  productList: { paddingVertical: 8 },
  productTile: {
    width: 160,
    padding: 12,
    marginRight: 10,
    backgroundColor: '#fff',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#eee',
    justifyContent: 'space-between',
  },
  productName: { fontSize: 14, marginBottom: 8 },
  addButton: {
    backgroundColor: '#0066CC',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  addButtonText: { color: '#fff', fontSize: 14, fontWeight: '600' },
  buttonsContainer: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 20 },
  button: { flex: 1, padding: 15, borderRadius: 10, alignItems: 'center', marginHorizontal: 5 },
  cancelButton: { backgroundColor: 'gray' },
  confirmButton: { backgroundColor: '#FF6B00' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
