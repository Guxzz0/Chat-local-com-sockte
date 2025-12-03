
import socket
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

HOST = '127.0.0.1'
TCP_PORT = 5050
HTTP_PORT = 8080

tcp_clients = []
tcp_nicknames = []
web_clients = {}
web_client_counter = 0
lock = threading.Lock()


def log(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")


def get_all_users():
    with lock:
        web_users = [client['username'] for client in web_clients.values()]
    return tcp_nicknames + web_users


def broadcast_tcp(message, sender_socket=None):
    for client in tcp_clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                remove_tcp_client(client)


def broadcast_web(message):
    with lock:
        msg_data = parse_message(message)
        for client_id in web_clients:
            web_clients[client_id]['messages'].append(msg_data)


def broadcast_all(message, sender_socket=None):
    broadcast_tcp(message, sender_socket)
    broadcast_web(message.decode('utf-8')
                  if isinstance(message, bytes) else message)


def parse_message(message):
    if "entrou no chat!" in message:
        parts = message.split(" entrou no chat!")
        username = parts[0].strip()
        return {
            'type': 'user_joined',
            'username': username,
            'content': message
        }
    elif "saiu do chat." in message:
        parts = message.split(" saiu do chat.")
        username = parts[0].strip()
        return {
            'type': 'user_left',
            'username': username,
            'content': message
        }
    elif ": " in message:
        parts = message.split(": ", 1)
        username = parts[0].strip()
        content = parts[1] if len(parts) > 1 else ""
        return {
            'type': 'message',
            'username': username,
            'content': content
        }
    else:
        return {
            'type': 'system',
            'content': message
        }


def remove_tcp_client(client_socket):
    if client_socket in tcp_clients:
        index = tcp_clients.index(client_socket)
        tcp_clients.remove(client_socket)
        nickname = tcp_nicknames[index]
        tcp_nicknames.remove(nickname)

        log(f"❌ Cliente TCP {nickname} desconectado")
        broadcast_all(f"{nickname} saiu do chat.".encode('utf-8'))


def handle_tcp_client(client_socket, address):
    try:
        # Recebe nome de usuário
        client_socket.send('NICK'.encode('utf-8'))
        nickname = client_socket.recv(1024).decode('utf-8')

        # Adiciona às listas
        tcp_clients.append(client_socket)
        tcp_nicknames.append(nickname)

        log(f"✅ Cliente TCP: {nickname} ({address[0]}:{address[1]})")

        # Mensagem de boas-vindas
        client_socket.send('Conectado ao servidor!'.encode('utf-8'))
        broadcast_all(f"{nickname} entrou no chat!".encode('utf-8'))

        # Loop de mensagens
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break

                log(f"💬 {nickname}: {message.decode('utf-8')}")
                broadcast_all(message)

            except:
                break

    except Exception as e:
        log(f"⚠️ Erro TCP: {e}")
    finally:
        remove_tcp_client(client_socket)
        client_socket.close()


class ChatHTTPHandler(BaseHTTPRequestHandler):
    """Handler para interface web"""

    def log_message(self, format, *args):
        """Suprime logs HTTP"""
        pass

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)

        # Serve interface web
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(get_html_content().encode('utf-8'))
            return

        # Polling de mensagens
        elif parsed_path.path == '/poll':
            query = parse_qs(parsed_path.query)
            client_id = query.get('client_id', [None])[0]

            if client_id and client_id in web_clients:
                with lock:
                    messages = web_clients[client_id]['messages'].copy()
                    web_clients[client_id]['messages'].clear()

                self.send_response(200)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'messages': messages,
                    'users': get_all_users()
                }).encode())
            else:
                self.send_response(404)
                self._set_cors_headers()
                self.end_headers()
            return

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global web_client_counter

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body)

        # Conectar novo cliente web
        if self.path == '/connect':
            username = data.get('username')

            if not username:
                self.send_response(400)
                self._set_cors_headers()
                self.end_headers()
                return

            with lock:
                web_client_counter += 1
                client_id = str(web_client_counter)
                web_clients[client_id] = {
                    'username': username,
                    'messages': []
                }

            log(f"✅ Cliente WEB: {username} (ID: {client_id})")

            # Notifica todos
            broadcast_all(f"{username} entrou no chat!".encode('utf-8'))

            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'client_id': client_id,
                'username': username
            }).encode())
            return

        # Enviar mensagem
        elif self.path == '/send':
            client_id = data.get('client_id')
            message = data.get('message')

            if client_id in web_clients:
                username = web_clients[client_id]['username']
                formatted_message = f"{username}: {message}"

                log(f"💬 {username} (web): {message}")

                # Envia para todos (TCP + Web)
                broadcast_all(formatted_message.encode('utf-8'))

                self.send_response(200)
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'sent'}).encode())
            else:
                self.send_response(404)
                self._set_cors_headers()
                self.end_headers()
            return

        # Desconectar
        elif self.path == '/disconnect':
            client_id = data.get('client_id')

            if client_id in web_clients:
                with lock:
                    username = web_clients[client_id]['username']
                    del web_clients[client_id]

                log(f"❌ Cliente WEB {username} desconectado")
                broadcast_all(f"{username} saiu do chat.".encode('utf-8'))

                self.send_response(200)
                self._set_cors_headers()
                self.end_headers()
            return

        self.send_response(404)
        self.end_headers()


def get_html_content():
    """Retorna o HTML da interface web moderna"""
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Local - Web</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        .login-container h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .login-container p {
            color: #666;
            margin-bottom: 30px;
        }
        .login-container input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
            outline: none;
        }
        .login-container input:focus { border-color: #667eea; }
        .login-container button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .login-container button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .login-container button:disabled { opacity: 0.6; cursor: not-allowed; }
        .chat-container {
            width: 100%;
            max-width: 900px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: none;
            flex-direction: column;
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 20px 20px 0 0;
        }
        .chat-header h2 { font-size: 18px; }
        .disconnect-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f5f7fb;
        }
        .message {
            display: flex;
            margin-bottom: 15px;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.sent { justify-content: flex-end; }
        .message-wrapper { max-width: 70%; }
        .message-header {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
            padding: 0 4px;
            font-weight: 600;
        }
        .message-content {
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.received .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        .message.sent .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message-time {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 5px;
            display: block;
        }
        .system-message {
            text-align: center;
            color: #999;
            font-size: 13px;
            margin: 15px 0;
            padding: 8px;
            background: rgba(0, 0, 0, 0.03);
            border-radius: 8px;
            font-style: italic;
        }
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            border-radius: 0 0 20px 20px;
        }
        .chat-input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .chat-input:focus { border-color: #667eea; }
        .send-button {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-size: 18px;
        }
        .send-button:hover:not(:disabled) { transform: scale(1.1); }
        .error-message {
            color: #e74c3c;
            font-size: 14px;
            margin-top: 10px;
            display: none;
            padding: 10px;
            background: #ffe5e5;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="login-container" id="loginContainer">
        <h1>💬 Chat Local</h1>
        <p>Versão Web</p>
        <input type="text" id="usernameInput" placeholder="Digite seu nickname..." maxlength="20">
        <button id="connectBtn" onclick="connectToServer()">Entrar no Chat</button>
        <div class="error-message" id="errorMessage"></div>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="chat-header">
            <h2>💬 Chat Local - <span id="currentUsername"></span></h2>
            <button class="disconnect-btn" onclick="disconnect()">Desconectar</button>
        </div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-input-container">
            <input type="text" class="chat-input" id="messageInput" placeholder="Digite sua mensagem...">
            <button class="send-button" onclick="sendMessage()">➤</button>
        </div>
    </div>

    <script>
        let clientId = null;
        let username = '';
        let pollingInterval = null;

        async function connectToServer() {
            const usernameInput = document.getElementById('usernameInput').value.trim();
            if (!usernameInput || usernameInput.length < 2) {
                showError('Digite um nickname válido (mínimo 2 caracteres)');
                return;
            }
            username = usernameInput;
            const connectBtn = document.getElementById('connectBtn');
            connectBtn.disabled = true;
            connectBtn.textContent = 'Conectando...';
            
            try {
                const response = await fetch('/connect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: username })
                });
                if (!response.ok) throw new Error('Erro ao conectar');
                const data = await response.json();
                clientId = data.client_id;
                showChatInterface();
                startPolling();
            } catch (error) {
                showError(error.message);
                connectBtn.disabled = false;
                connectBtn.textContent = 'Entrar no Chat';
            }
        }

        function startPolling() {
            pollingInterval = setInterval(async () => {
                if (!clientId) return;
                try {
                    const response = await fetch('/poll?client_id=' + clientId);
                    if (!response.ok) return;
                    const data = await response.json();
                    if (data.messages && data.messages.length > 0) {
                        data.messages.forEach(msg => processMessage(msg));
                    }
                } catch (error) {
                    console.error('Erro no polling:', error);
                }
            }, 500);
        }

        function processMessage(message) {
            if (message.type === 'message') {
                const isSent = message.username === username;
                addMessage(message.username, message.content, isSent);
            } else {
                addSystemMessage(message.content);
            }
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message || !clientId) return;
            
            try {
                await fetch('/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ client_id: clientId, message: message })
                });
                input.value = '';
            } catch (error) {
                showError('Erro ao enviar mensagem');
            }
        }

        async function disconnect() {
            if (pollingInterval) clearInterval(pollingInterval);
            if (clientId) {
                await fetch('/disconnect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ client_id: clientId })
                });
            }
            document.getElementById('loginContainer').style.display = 'block';
            document.getElementById('chatContainer').style.display = 'none';
            document.getElementById('chatMessages').innerHTML = '';
            document.getElementById('usernameInput').value = '';
            document.getElementById('connectBtn').disabled = false;
            document.getElementById('connectBtn').textContent = 'Entrar no Chat';
        }

        function showChatInterface() {
            document.getElementById('loginContainer').style.display = 'none';
            document.getElementById('chatContainer').style.display = 'flex';
            document.getElementById('currentUsername').textContent = username;
            document.getElementById('messageInput').focus();
        }

        function addMessage(user, text, isSent) {
            const container = document.getElementById('chatMessages');
            const div = document.createElement('div');
            div.className = 'message ' + (isSent ? 'sent' : 'received');
            const time = new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
            div.innerHTML = `
                <div class="message-wrapper">
                    <div class="message-header">${isSent ? 'Você' : escapeHtml(user)}</div>
                    <div class="message-content">
                        ${escapeHtml(text)}
                        <span class="message-time">${time}</span>
                    </div>
                </div>
            `;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function addSystemMessage(text) {
            const container = document.getElementById('chatMessages');
            const div = document.createElement('div');
            div.className = 'system-message';
            div.textContent = text;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => errorDiv.style.display = 'none', 5000);
        }

        document.getElementById('usernameInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') connectToServer();
        });
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        window.addEventListener('beforeunload', () => {
            if (clientId) {
                navigator.sendBeacon('/disconnect', JSON.stringify({ client_id: clientId }));
            }
        });
    </script>
</body>
</html>"""


def start_tcp_server():
    """Inicia servidor TCP para clientes GUI/CLI"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, TCP_PORT))
    server.listen()

    log(f"✅ Servidor TCP rodando em {HOST}:{TCP_PORT}")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(
            target=handle_tcp_client,
            args=(client_socket, address),
            daemon=True
        )
        thread.start()


def start_http_server():
    """Inicia servidor HTTP para interface web"""
    server = HTTPServer(('0.0.0.0', HTTP_PORT), ChatHTTPHandler)
    log(f"🌐 Interface Web rodando em http://localhost:{HTTP_PORT}")
    server.serve_forever()


def main():
    """Inicia ambos os servidores"""
    print("\n" + "=" * 70)
    print("🚀 CHAT LOCAL - Servidor Completo".center(70))
    print("=" * 70)

    # Inicia servidor TCP em thread
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Info
    print(f"\n📱 Clientes GUI/CLI: python client_gui.py ou python client.py")
    print(f"🌐 Interface Web: http://localhost:{HTTP_PORT}")
    print(f"\n💡 Dica: Você pode usar GUI e Web ao mesmo tempo!")
    print("=" * 70 + "\n")

    try:
        start_http_server()
    except KeyboardInterrupt:
        log("\n❌ Servidor encerrado")


if __name__ == "__main__":
    main()
