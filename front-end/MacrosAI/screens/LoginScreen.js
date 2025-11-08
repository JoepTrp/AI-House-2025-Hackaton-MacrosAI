// ...existing code...
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Platform, KeyboardAvoidingView, Image } from 'react-native';
import { useUser } from '../context/UserContext';

export default function LoginScreen({ navigation }) {
  const { login } = useUser();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.inner}>
        <Text style={styles.title}>Login</Text>
        <Image 
        source={require("../assets/logo.png")}
        resizeMode="contain"
        style={styles.logo}
        />
        <Text style={styles.subtitle}>
          Hi, Welcome to your health boosting joruney!
        </Text>
        

        <TextInput
          placeholder="Email"
          style={styles.input}
          onChangeText={setEmail}
          value={email}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TextInput
          placeholder="Password"
          secureTextEntry
          style={styles.input}
          onChangeText={setPassword}
          value={password}
        />

        <TouchableOpacity style={styles.primaryButton} onPress={() => login(email, password)}>
          <Text style={styles.primaryButtonText}>Continue</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton} onPress={() => navigation.navigate('Register')}>
          <Text style={styles.secondaryButtonText}>Go to Register</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  inner: { flex: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 36, fontWeight: '800', textAlign: 'center', marginBottom: 0 },
  subtitle: { fontSize: 16, textAlign: 'center', color: '#444', marginBottom: 24 },
  logo: { width: 400, height: 400, alignSelf: 'center', marginBottom: 8 },
  input: { borderWidth: 1, padding: 14, marginBottom: 12, borderRadius: 8, borderColor: '#ccc' },
  primaryButton: { backgroundColor: '#0066CC', paddingVertical: 14, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  primaryButtonText: { color: '#fff', fontSize: 18, fontWeight: '600' },
  secondaryButton: { paddingVertical: 12, borderRadius: 8, alignItems: 'center', marginTop: 10 },
  secondaryButtonText: { color: '#0066CC', fontSize: 16 },
});