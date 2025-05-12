import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Arete</Text>
      <View style={styles.buttonGroup}>
        <View style={styles.buttonContainer}>
          <Button title="Chat" onPress={() => {}} />
        </View>
        <View style={styles.buttonContainer}>
          <Button title="Story" onPress={() => {}} />
        </View>
        <View style={styles.buttonContainer}>
          <Button title="Phrase" onPress={() => {}} />
        </View>
        <View style={styles.buttonContainer}>
          <Button title="Your Words" onPress={() => {}} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 60,
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 40,
  },
  buttonGroup: {
    width: '80%',
    justifyContent: 'center',
  },
  buttonContainer: {
    marginVertical: 8,
  },
});

