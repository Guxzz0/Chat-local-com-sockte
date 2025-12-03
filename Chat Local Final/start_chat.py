"""
Launcher do Chat Local - Inicia automaticamente no navegador
"""

import subprocess
import sys
import time
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


def open_web_client():
    """Abre interface web no navegador"""
    print("🌐 Abrindo interface web no navegador...")
    time.sleep(1)
    webbrowser.open("http://localhost:8080")
    print("✅ Chat aberto no navegador!")


def main():
    """Inicia servidor e abre navegador automaticamente"""
    print("\n" + "=" * 60)
    print("💬 CHAT LOCAL - Iniciando...".center(60))
    print("=" * 60 + "\n")

    # Inicia servidor
    start_server()

    # Abre navegador
    open_web_client()

    print("\n" + "=" * 60)
    print("✅ Chat iniciado com sucesso!".center(60))
    print("=" * 60)
    print("\n🌐 Interface Web: http://localhost:8080")
    print("\n💡 Dicas:")
    print("   • Abra mais abas para adicionar usuários")
    print("   • Compartilhe o link na rede local")
    print("   • O servidor está rodando em background")
    print("\n⚠️  Para encerrar completamente:")
    print("   Windows: Abra o Gerenciador de Tarefas e finalize 'python.exe'")
    print("   Linux/Mac: Use 'pkill -f server.py' no terminal")
    print("\n" + "=" * 60)

    # Mantém a janela aberta
    input("\n✨ Pressione Enter para abrir mais clientes ou Ctrl+C para fechar este launcher...\n")

    # Loop para abrir mais janelas se quiser
    while True:
        try:
            input("Pressione Enter para abrir outra janela do chat...\n")
            open_web_client()
            print("✅ Nova janela aberta!\n")
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando launcher...")
            print("⚠️  Servidor continua rodando em background!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
        sys.exit(0)
