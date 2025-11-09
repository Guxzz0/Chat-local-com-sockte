# Chat Local com Socket

## Descrição do Projeto
O **Chat Local com Socket** é um sistema de comunicação em rede local desenvolvido em **Python**, utilizando a biblioteca **socket** para criar a conexão entre **clientes** e **servidor**.  
O objetivo é permitir que vários usuários troquem mensagens em tempo real dentro de uma rede local (LAN).

---

## Funcionalidades
- Conexão entre múltiplos clientes e um servidor central.  
- Envio e recebimento de mensagens em tempo real.  
- Exibição do nome do usuário nas mensagens.  
- Sistema de salas (opcional).  
- Interface simples por linha de comando (CLI).  
- Tratamento de erros e desconexões.  

---

## Estrutura do Projeto
```
chat_local_socket/
│
├── server.py          # Código do servidor
├── client.py          # Código do cliente
├── utils.py           # Funções auxiliares (mensagens, logs, etc.)
├── requirements.txt   # Dependências do projeto
└── README.md          # Documentação do projeto
```

---

## Tecnologias Utilizadas
- **Python 3.10+**
- **Biblioteca socket** (nativa)
- **threading** (para múltiplas conexões)
- **datetime** (para registro de horários)

---

## Diagrama UML

### Caso de Uso
Representa as ações possíveis do usuário e do servidor.  
*(ver imagem: `UML_Caso_de_Uso.png`)*

### Classes
Mostra a estrutura e relacionamento entre as classes principais.  
*(ver imagem: `UML_Classes.png`)*

---

## Como Executar

### 1Clone o repositório
```bash
git clone https://github.com/seuusuario/chat-local-socket.git
cd chat-local-socket
```

### 2Execute o servidor
```bash
python server.py
```

### 3Execute os clientes
Em outros terminais:
```bash
python client.py
```

### 4Envie mensagens
Cada cliente conectado pode enviar e receber mensagens em tempo real.

---

##  Equipe de Desenvolvimento
| Integrante | Função |
|-------------|--------|
| Gustavo | Líder do Projeto / Back-end |
| Walter | Comunicação Cliente-Servidor |
| Daniel | Testes e Debug |
| Nobre | Documentação e UML |
| Alexandre | Interface e Usabilidade |

---

## Licença
Este projeto é de uso educacional e está sob a licença **MIT**.
