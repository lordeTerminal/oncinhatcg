import TcpSocket from 'react-native-tcp-socket';

const client = TcpSocket.createConnection({ port: 5555, host: 'SEU_IP' }, () => {
  client.write("1\n"); // exemplo de envio do ID
});

client.on('data', function(data) {
  console.log('Recebido do servidor: ' + data.toString());
});

client.on('error', function(error) {
  console.log('Erro: ' + error);
});

client.on('close', function() {
  console.log('Conexão encerrada');
});

