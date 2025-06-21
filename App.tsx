import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import Login from './login';
import Cadastro from './cadastro';
import Home from './Home';
import Deck from './Deck';
import Cartas from './Cartas';
import Batalha from './Batalha';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={Login} options={{ title: 'Tiger Mage - Login' }} />
        <Stack.Screen name="Cadastro" component={Cadastro} options={{ title: 'Cadastro' }} />
        <Stack.Screen name="Home" component={Home} options={{ title: 'Página Principal' }} />
        <Stack.Screen name="Deck" component={Deck} options={{ title: 'Meu Deck' }} />
        <Stack.Screen name="Cartas" component={Cartas} options={{ title: 'Escolher Cartas' }} />
        <Stack.Screen name="Batalha" component={Batalha} options={{ title: 'Batalha' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

