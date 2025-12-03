"""
Launcher do Chat Local
Inicia o servidor e permite escolher entre GUI ou Web
"""

import subprocess
import sys
import time
import os
import webbrowser

CREATE_NO_WINDOW = 0x08000000 if sys.platform.startswith("win") else 0


def start_server():
    """Inicia o servidor em background"""
    print("🚀 Iniciando servidor...")

    if sys.platform.startswith("win"):
        # Windows - usa pythonw para não mostrar console
        subprocess.Popen(
            ["pythonw", "server.py"],
            creationflags=CREATE_NO_WINDOW
        )
    else:
        # Linux/Mac
        subprocess.Popen(
            ["python3", "server.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    print("✅ Servidor iniciado!")
    time.sleep(2)  # Aguarda servidor iniciar


def start_gui_client():
    """Inicia cliente GUI (CustomTkinter)"""
    print("📱 Iniciando cliente GUI...")

    if sys.platform.startswith("win"):
        subprocess.Popen(
            ["pythonw", "client_gui.py"],
            creationflags=CREATE_NO_WINDOW
        )
    else:
        subprocess.Popen(["python3", "client_gui.py"])

    print("✅ Cliente GUI iniciado!")


def open_web_client():
    """Abre interface web no navegador"""
    print("🌐 Abrindo interface web...")
    time.sleep(1)
    webbrowser.open("http://localhost:8080")
    print("✅ Interface web aberta no navegador!")


def show_menu():
    """Mostra menu de opções"""
    print("\n" + "=" * 50)
    print("💬 CHAT LOCAL - Launcher".center(50))
    print("=" * 50)
    print("\nEscolha uma opção:")
    print("\n1. Iniciar com interface GUI (Desktop)")
    print("2. Iniciar com interface Web (Navegador)")
    print("3. Iniciar ambas (GUI + Web)")
    print("4. Apenas iniciar servidor")
    print("0. Sair")
    print("\n" + "=" * 50)


def main():
    """Menu principal"""

    while True:
        show_menu()
        choice = input("\nOpção: ").strip()

        if choice == "1":
            # GUI apenas
            start_server()
            start_gui_client()
            print("\n✅ Chat iniciado com interface GUI!")
            print("💡 Feche a janela do chat para encerrar.")
            break

        elif choice == "2":
            # Web apenas
            start_server()
            open_web_client()
            print("\n✅ Chat iniciado com interface Web!")
            print("💡 Acesse: http://localhost:8080")
            print("⚠️ Pressione Ctrl+C para encerrar o servidor.")
            try:
                input(
                    "\nPressione Enter para abrir mais clientes web ou Ctrl+C para sair...")
                while True:
                    open_web_client()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n❌ Encerrando...")
                break

        elif choice == "3":
            # Ambos
            start_server()
            start_gui_client()
            time.sleep(0.5)
            open_web_client()
            print("\n✅ Chat iniciado com GUI e Web!")
            print("📱 Cliente GUI: Janela aberta")
            print("🌐 Cliente Web: http://localhost:8080")
            print("\n💡 Você pode abrir mais clientes:")
            print("   - Para GUI: execute client_gui.py")
            print("   - Para Web: abra http://localhost:8080 em outras abas")
            break

        elif choice == "4":
            # Apenas servidor
            start_server()
            print("\n✅ Servidor iniciado!")
            print("\n📱 Para conectar GUI: python client_gui.py")
            print("🌐 Para conectar Web: http://localhost:8080")
            print("\n⚠️ Servidor rodando em background.")
            print("   Use o Gerenciador de Tarefas para encerrar se necessário.")
            break

        elif choice == "0":
            print("\n👋 Até logo!")
            sys.exit(0)

        else:
            print("\n❌ Opção inválida! Tente novamente.")
            time.sleep(1)
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Encerrando...")
        sys.exit(0)
