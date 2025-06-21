import socket

HOST = input("IP do servidor (ex: 192.168.0.10): ")
PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("✅ Conectado ao servidor!")

    buffer = ""
    while True:
        data = s.recv(4096)
        if not data:
            print("❌ Conexão encerrada pelo servidor.")
            break

        buffer += data.decode()
        while '\n' in buffer:
            mensagem, buffer = buffer.split('\n', 1)
            mensagem = mensagem.strip()
            if mensagem:
                print(mensagem)
                if any(mensagem.lower().endswith(sufixo) for sufixo in [":", "?)", ">", "->"]):
                    resposta = input("👉 ")
                    s.sendall((resposta.strip() + '\n').encode())

