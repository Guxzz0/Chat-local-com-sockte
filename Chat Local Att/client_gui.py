import socket
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import time

# Server settings (match your server)
HOST = '127.0.0.1'
PORT = 5050

ctk.set_appearance_mode('Light')  # Light theme chosen
ctk.set_default_color_theme('blue')  # blue accent

class ChatClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Chat Local - Tema Claro Moderno')
        self.geometry('760x520')
        self.resizable(False, False)

        self.socket = None
        self.nickname = None
        self.running = False

        # Top frame for connection
        self.top_frame = ctk.CTkFrame(self, corner_radius=12)
        self.top_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.16)

        self.lbl_title = ctk.CTkLabel(self.top_frame, text='Chat Local', font=ctk.CTkFont(size=18, weight='bold'))
        self.lbl_title.place(relx=0.02, rely=0.08)

        self.lbl_status = ctk.CTkLabel(self.top_frame, text='Status: Desconectado', anchor='w')
        self.lbl_status.place(relx=0.02, rely=0.55)

        self.entry_nick = ctk.CTkEntry(self.top_frame, placeholder_text='Digite seu nickname...')
        self.entry_nick.place(relx=0.36, rely=0.08, relwidth=0.38)

        self.btn_connect = ctk.CTkButton(self.top_frame, text='Conectar', command=self.connect_to_server)
        self.btn_connect.place(relx=0.80, rely=0.08, relwidth=0.16)

        # Middle frame - messages and users
        self.middle_frame = ctk.CTkFrame(self, corner_radius=12)
        self.middle_frame.place(relx=0.02, rely=0.20, relwidth=0.96, relheight=0.66)

        # Messages area
        self.messages_area = scrolledtext.ScrolledText(self.middle_frame, wrap=tk.WORD, state='disabled', font=('Segoe UI', 11))
        self.messages_area.place(relx=0.01, rely=0.02, relwidth=0.74, relheight=0.86)
        self.messages_area.configure(background='#ffffff', relief='flat', bd=0)

        # Users list
        self.users_label = ctk.CTkLabel(self.middle_frame, text='Usuários (clique para privado)', anchor='w')
        self.users_label.place(relx=0.77, rely=0.02, relwidth=0.22)

        self.users_listbox = tk.Listbox(self.middle_frame, bd=0, highlightthickness=0, font=('Segoe UI', 10))
        self.users_listbox.place(relx=0.77, rely=0.07, relwidth=0.22, relheight=0.78)
        self.users_listbox.insert(tk.END, 'Todos (Público)')
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)

        # Bottom frame - entry and send
        self.bottom_frame = ctk.CTkFrame(self, corner_radius=12)
        self.bottom_frame.place(relx=0.02, rely=0.88, relwidth=0.96, relheight=0.10)

        self.entry_msg = ctk.CTkEntry(self.bottom_frame, placeholder_text='Escreva uma mensagem...')
        self.entry_msg.place(relx=0.01, rely=0.12, relwidth=0.78, relheight=0.75)
        self.entry_msg.bind('<Return>', lambda e: self.send_message())

        self.btn_send = ctk.CTkButton(self.bottom_frame, text='Enviar', command=self.send_message)
        self.btn_send.place(relx=0.81, rely=0.12, relwidth=0.18, relheight=0.75)

        # Selected user for private messages (None = public)
        self.selected_user = None

        # Protocol to close gracefully
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def connect_to_server(self):
        if self.socket and self.running:
            self.append_system('Já conectado.')
            return
        nick = self.entry_nick.get().strip()
        if not nick:
            messagebox.showwarning('Nickname', 'Digite um nickname antes de conectar.')
            return
        self.nickname = nick
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((HOST, PORT))
            self.socket.settimeout(None)
            self.running = True
            self.lbl_status.configure(text=f'Status: Conectado como {self.nickname}')
            # Start receiving thread
            threading.Thread(target=self.receive_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível conectar: {e}')
            self.running = False
            if self.socket:
                self.socket.close()
                self.socket = None
            return

    def receive_loop(self):
        try:
            while self.running:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                # server asks for NICK during handshake
                if message == 'NICK':
                    self.socket.send(self.nickname.encode('utf-8'))
                    continue
                # display normal messages
                self.append_message(message)
        except Exception as e:
            # display error and stop
            self.append_system('Conexão perdida.')
        finally:
            self.running = False
            try:
                if self.socket:
                    self.socket.close()
            except:
                pass
            self.lbl_status.configure(text='Status: Desconectado')

    def append_message(self, text):
        # Thread-safe append
        def inner():
            self.messages_area.configure(state='normal')
            self.messages_area.insert(tk.END, text + '\n')
            self.messages_area.see(tk.END)
            self.messages_area.configure(state='disabled')
        self.after(0, inner)

    def append_system(self, text):
        self.append_message(f'[Sistema] {text}')

    def send_message(self):
        if not self.running or not self.socket:
            messagebox.showwarning('Não conectado', 'Conecte-se ao servidor antes de enviar mensagens.')
            return
        text = self.entry_msg.get().strip()
        if not text:
            return
        try:
            to_send = f'{self.nickname}: {text}'
            self.socket.send(to_send.encode('utf-8'))
            self.entry_msg.delete(0, tk.END)
        except Exception as e:
            self.append_system('Erro ao enviar mensagem.')
            self.running = False

    def on_user_select(self, event):
        try:
            idx = self.users_listbox.curselection()[0]
            value = self.users_listbox.get(idx)
            if value == 'Todos (Público)':
                self.selected_user = None
                self.append_system('Modo público ativado.')
            else:
                self.selected_user = value
                self.append_system(f'Modo privado selecionado: {value} (Aviso: servidor atual envia mensagens para todos)')
        except IndexError:
            pass

    def on_close(self):
        try:
            self.running = False
            if self.socket:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                except:
                    pass
        finally:
            self.destroy()

if __name__ == '__main__':
    app = ChatClientApp()
    app.mainloop()
