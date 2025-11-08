import React from 'react';
import { SafeAreaView, View, Text, FlatList, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useUser } from '../context/UserContext';

export default function Settings({ navigation }) {
  const { logout } = useUser();

  const settingsData = [
    { id: '1', title: 'Account' },
    { id: '2', title: 'Notifications' },
    { id: '3', title: 'Privacy' },
    { id: '4', title: 'Display' },
    { id: '5', title: 'About' },
    { id: '6', title: 'Help' },
    {
      id: '7',
      title: 'Log out',
      action: () =>
        Alert.alert('Log out', 'Are you sure you want to log out?', [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Log out',
            style: 'destructive',
            onPress: () => {
              logout();
              // reset navigation to Login screen (replace with your auth flow route)
              navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
            },
          },
        ]),
    },
  ];

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.row}
      onPress={() => {
        if (item.action) {
          item.action();
        } else {
          Alert.alert(item.title);
        }
      }}
    >
      <Text style={styles.rowText}>{item.title}</Text>
      <Text style={styles.chev}>›</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.headerContainer}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text>Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={styles.rightPlaceholder} />
      </View>

      <FlatList
        data={settingsData}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  headerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingVertical: 14,
  },
  headerTitle: { fontSize: 22, fontWeight: '700' },
  header: { fontSize: 22, fontWeight: '700', paddingHorizontal: 16, paddingVertical: 18 },
  rightPlaceholder: { width: 40 },
  list: { paddingHorizontal: 16 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 12,
    backgroundColor: '#f9f9fb',
    borderRadius: 10,
  },
  backButton: {
    padding: 8,
    borderRadius: 20,
  },
  rowText: { fontSize: 16, color: '#111' },
  chev: { fontSize: 20, color: '#999' },
  separator: { height: 12 },
});