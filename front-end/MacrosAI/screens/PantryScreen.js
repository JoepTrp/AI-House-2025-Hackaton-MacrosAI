import React, { useState } from 'react';
import { SafeAreaView, View, Text, FlatList, StyleSheet, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useUser } from '../context/UserContext';

export default function PantryScreen() {
  const { pantryItems, addPantryItem, removePantryItem } = useUser();

  const [newItem, setNewItem] = useState('');

  const addItem = () => {
    if (!newItem.trim()) return;
    const id = Date.now().toString();
    addPantryItem({ id, name: newItem });
    setNewItem('');
  };

  const confirmRemove = (id, name) => {
    Alert.alert('Remove item', `Remove "${name}" from pantry?`, [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Remove', style: 'destructive', onPress: () => removePantryItem(id) },
    ]);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Pantry</Text>

      <FlatList
        data={pantryItems}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text style={styles.rowText}>{item.name}</Text>
            <TouchableOpacity onPress={() => confirmRemove(item.id, item.name)}>
              <Text style={{ color: 'red', fontWeight: '700' }}>Delete</Text>
            </TouchableOpacity>
          </View>
        )}
        contentContainerStyle={styles.list}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inputContainerWrapper}
      >
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="Add new item..."
            value={newItem}
            onChangeText={setNewItem}
          />
          <TouchableOpacity style={styles.addButton} onPress={addItem}>
            <Text style={styles.addButtonText}>Add</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 60, paddingHorizontal: 20},
  title: { fontSize: 30, fontWeight: '600', marginBottom: 16 },
  list: { paddingBottom: 100, padding:10 },
  row: {
    paddingVertical: 14,
    paddingHorizontal: 12,
    backgroundColor: '#f0f0f7',
    borderRadius: 10,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  rowText: { fontSize: 16 },
  inputContainerWrapper: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
  },
  inputContainer: {
    flexDirection: 'row',
    backgroundColor: '#f7f7fb',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 6,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  input: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 6,
  },
  addButton: {
    backgroundColor: '#ff9500',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 14,
    marginLeft: 8,
  },
  addButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
});
