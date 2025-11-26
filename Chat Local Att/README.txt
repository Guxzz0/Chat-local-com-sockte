Chat Local - Tema Claro Moderno (GUI)
-----------------------------------
Arquivos incluídos:
- server.py        (seu servidor original)
- client_gui.py    (novo cliente usando customtkinter)
- start_chat.py    (script que abre o servidor e 2 clientes em terminais separados)

Requisitos:
- Python 3.8+
- customtkinter (pip install customtkinter)

Como rodar:
1) Instale a lib: pip install customtkinter
2) Abra um terminal e execute: python server.py
3) Em outro terminal execute: python client_gui.py
   (ou use python start_chat.py para abrir servidor + 2 clientes automaticamente)

Observações:
- O cliente faz handshake com o servidor: quando o servidor enviar 'NICK', o cliente responde com o nickname.
- O servidor atual é simples e broadcasta as mensagens para todos clientes conectados.
