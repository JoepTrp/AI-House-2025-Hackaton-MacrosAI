import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Button, StyleSheet, ScrollView } from 'react-native';
import { useUser } from '../../context/UserContext';

const activityLevels = ['Sedentary', 'Light', 'Moderate', 'Active'];
const goals = ['Lose Weight', 'Gain Muscle', 'Maintain'];

export default function OnboardingScreenOne({ navigation }) {
  const { register } = useUser();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [gender, setGender] = useState('');
  const [age, setAge] = useState('');
  const [weight, setWeight] = useState('');
  const [activityLevel, setActivityLevel] = useState('');
  const [goal, setGoal] = useState('');
  const [height, setHeight] = useState('');

  const handleRegister = async () => {
    const payload = {
      email,
      password,
      username,
      gender,
      age: Number(age),
      height: Number(height),
      weight: Number(weight),
      goal: goal ? goal.toLowerCase() : undefined,
      activityLevel: activityLevel ? activityLevel.toLowerCase() : undefined,
    };
    console.log('register payload', payload);
    const result = await register(payload);
    console.log('register result', result);
  };

  const renderOptionButtons = (options, selected, setSelected) => {
    return options.map((opt) => (
      <TouchableOpacity
        key={opt}
        style={[
          styles.optionButton,
          selected === opt && styles.optionButtonSelected,
        ]}
        onPress={() => setSelected(opt)}
      >
        <Text
          style={[
            styles.optionText,
            selected === opt && styles.optionTextSelected,
          ]}
        >
          {opt}
        </Text>
      </TouchableOpacity>
    ));
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Register</Text>

      <TextInput
        placeholder="Email"
        style={styles.input}
        onChangeText={setEmail}
        value={email}
        keyboardType="email-address"
      />
      <TextInput
        placeholder="Username"
        style={styles.input}
        onChangeText={setUsername}
        value={username}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        style={styles.input}
        onChangeText={setPassword}
        value={password}
      />

      <TextInput
        placeholder="Gender"
        style={styles.input}
        onChangeText={setGender}
        value={gender}
      />
      <TextInput
        placeholder="Age"
        style={styles.input}
        onChangeText={setAge}
        value={age}
        keyboardType="numeric"
      />
      
      <TextInput
        placeholder="Weight (kg)"
        style={styles.input}
        onChangeText={setWeight}
        value={weight}
        keyboardType="numeric"
      />
      <TextInput
        placeholder="Height (cm)"
        style={styles.input}
        onChangeText={setHeight}
        value={height}
        keyboardType="numeric"
      />

      <Text style={styles.label}>Activity Level</Text>
      <View style={styles.optionsRow}>
        {renderOptionButtons(activityLevels, activityLevel, setActivityLevel)}
      </View>

      <Text style={styles.label}>Goal</Text>
      <View style={styles.optionsRow}>
        {renderOptionButtons(goals, goal, setGoal)}
      </View>

      <TouchableOpacity style={styles.registerButton} onPress={handleRegister}>
        <Text style={styles.registerButtonText}>Register</Text>
      </TouchableOpacity>

      <Button title="Go to Login" onPress={() => navigation.navigate('Login')} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 12,
    marginBottom: 12,
    borderRadius: 8,
    fontSize: 16,
  },
  label: { fontSize: 16, fontWeight: '600', marginBottom: 8 },
  optionsRow: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 16 },
  optionButton: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginRight: 10,
    marginBottom: 10,
  },
  optionButtonSelected: { backgroundColor: '#ff9800', borderColor: '#ff9800' },
  optionText: { color: '#333', fontSize: 14 },
  optionTextSelected: { color: '#fff', fontWeight: '600' },
  registerButton: {
    backgroundColor: '#ff9800',
    paddingVertical: 14,
    borderRadius: 25,
    marginBottom: 10,
    alignItems: 'center',
  },
  registerButtonText: { color: '#fff', fontSize: 18, fontWeight: '600' },
});
