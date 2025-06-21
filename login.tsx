import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  Alert,
  TouchableOpacity
} from 'react-native';

export default function Login({ navigation }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');

  const fazerLogin = async () => {
    try {
      const response = await fetch('http://192.168.1.15:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      });

      const data = await response.json();
      if (response.ok) {
        Alert.alert('Login OK', `Bem-vindo(a), ${data.nome}`);
	navigation.navigate('Home', { user_id: data.user_id, nome: data.nome });
        // Aqui você pode navegar para o "dashboard" ou outra tela após login
      } else {
        Alert.alert('Erro', data.detail || 'Falha no login');
      }
    } catch (error: any) {
      Alert.alert('Erro', error.message || 'Erro de conexão');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Tiger Mage - Login</Text>
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        style={styles.input}
      />
      <TextInput
        placeholder="Senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
        style={styles.input}
      />
      <Button title="Entrar" onPress={fazerLogin} />

      <TouchableOpacity onPress={() => navigation.navigate('Cadastro')}>
        <Text style={styles.link}>Não tem conta? Cadastre-se</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  title: { fontSize: 24, marginBottom: 20, textAlign: 'center' },
  input: {
    borderWidth: 1,
    marginBottom: 10,
    padding: 8,
    borderRadius: 4,
    borderColor: '#ccc',
  },
  link: {
    marginTop: 20,
    color: 'blue',
    textAlign: 'center',
    fontSize: 16,
  },
});

