import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert } from 'react-native';
import axios from 'axios';

export default function Cadastro() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');

  const handleCadastro = async () => {
    try {
      const resposta = await axios.post('http://192.168.1.15:8000/api/registrar', {
        nome,
        email,
        senha
      });
      Alert.alert('Sucesso', resposta.data.msg);
    } catch (err) {
      console.error(err);
      Alert.alert('Erro', err.response?.data?.detail || 'Erro desconhecido');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, marginBottom: 10 }}>Cadastro</Text>
      <TextInput
        placeholder="Nome"
        value={nome}
        onChangeText={setNome}
        style={{ marginBottom: 10, borderWidth: 1, padding: 8 }}
      />
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        style={{ marginBottom: 10, borderWidth: 1, padding: 8 }}
      />
      <TextInput
        placeholder="Senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
        style={{ marginBottom: 20, borderWidth: 1, padding: 8 }}
      />
      <Button title="Cadastrar" onPress={handleCadastro} />
    </View>
  );
}

