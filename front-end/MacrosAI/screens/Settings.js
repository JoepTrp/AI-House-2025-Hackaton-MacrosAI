import React from 'react';
import {
  SafeAreaView,
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { useUser } from '../context/UserContext';

export default function Settings({ navigation }) {
  const { logout, orders, setOrders } = useUser(); 

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
              navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
            },
          },
        ]),
    },
  ];

  const renderSetting = ({ item }) => (
    <TouchableOpacity
      style={styles.row}
      onPress={item.action ?? (() => Alert.alert(item.title, 'Not implemented yet'))}
    >
      <Text style={styles.rowText}>{item.title}</Text>
      <Text style={styles.chev}>›</Text>
    </TouchableOpacity>
  );

  const renderOrder = ({ item }) => {
  const deliveryDate = new Date(item.deliveryTime);
  const now = new Date();

  // Compare dates
  const isDelivered = deliveryDate < now;
  const isUpcoming = deliveryDate.toDateString() !== now.toDateString();

  // Determine color for delivery status
  const deliveryColor = isDelivered ? 'green' : isUpcoming ? 'gold' : 'gray';

  // Handle cancel
  const handleCancel = () => {
      Alert.alert(
        'Cancel Order',
        'Are you sure you want to cancel this order?',
        [
          { text: 'No', style: 'cancel' },
          {
            text: 'Yes, cancel',
            style: 'destructive',
            onPress: () => {
              setOrders(prev =>
                prev.map(o =>
                  o.id === item.id ? { ...o, canceled: true } : o
                )
              );
            },
          },
        ]
      );
    };

    return (
      <TouchableOpacity
        style={[styles.row, item.canceled && { backgroundColor: '#ffeaea' }]}
        onLongPress={handleCancel} // user can cancel by long press
      >
        <View style={{ flex: 1 }}>
          <Text
            style={[
              styles.rowText,
              item.canceled && { color: 'red', fontWeight: '700' },
            ]}
          >
            Order #{item.id.slice(-4)} {item.canceled && '(Canceled)'}
          </Text>
          <Text style={styles.subText}>
            Order date: {new Date(item.createdAt).toLocaleDateString()} •{' '}
            {item.meals?.length ?? 0} meals
          </Text>
        </View>

        <View style={{ alignItems: 'flex-end' }}>
          <Text style={[styles.subText, { color: deliveryColor }]}>
            {isDelivered ? 'Delivered' : 'Delivery'}
          </Text>
          <Text style={[styles.rowText, { color: deliveryColor, fontWeight: '600' }]}>
            {deliveryDate.toLocaleDateString()}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };


  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.headerContainer}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text>Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={styles.rightPlaceholder} />
      </View>

      <FlatList
        ListHeaderComponent={
          <>
            <Text style={styles.sectionHeader}>Your Orders</Text>
            {orders.length === 0 && (
              <Text style={styles.emptyText}>No orders yet.</Text>
            )}
            <FlatList
              data={orders}
              keyExtractor={(item) => item.id}
              renderItem={renderOrder}
              ItemSeparatorComponent={() => <View style={styles.separator} />}
              scrollEnabled={false}
            />
            <Text style={styles.sectionHeader}>App Settings</Text>
          </>
        }
        data={settingsData}
        keyExtractor={(item) => item.id}
        renderItem={renderSetting}
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
  sectionHeader: { fontSize: 18, fontWeight: '600', marginTop: 10, marginBottom: 8, color: '#333' },
  emptyText: { color: '#777', fontStyle: 'italic', marginBottom: 8 },
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
  subText: { fontSize: 14, color: '#666', marginTop: 2 },
  chev: { fontSize: 20, color: '#999' },
  separator: { height: 10 },
});
