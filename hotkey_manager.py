# hotkey_manager.py
import keyboard  # Certifique-se de que 'keyboard' está no topo dos imports aqui também


def register_snippet_hotkeys(paste_callback_func, num_slots=9):
    """
    Registra os atalhos globais para colar snippets.
    :param paste_callback_func: A função a ser chamada quando um atalho é pressionado
                                (ex: app.paste_from_history_via_hotkey).
    :param num_slots: Quantidade de slots/atalhos a registrar.
    """
    print("--- Configurando Atalhos Globais para Snippets ---")
    try:
        for i in range(1, num_slots + 1):  # Para Shift+Ctrl+1 até Shift+Ctrl+num_slots
            # A lambda captura o valor de 'i' no momento da criação do atalho
            keyboard.add_hotkey(
                f'shift+ctrl+{i}',
                lambda index=i: paste_callback_func(index)
            )

        print(f"Atalhos Shift+Ctrl+1 a Shift+Ctrl+{num_slots} configurados.")
        print("Lembrete: Se os atalhos não funcionarem, pode ser necessário executar como administrador.")
    except Exception as e:
        print(f"Erro ao configurar atalhos globais: {e}")
        print("IMPORTANTE: Pode ser necessário executar este programa como administrador/root.")

# Você pode adicionar outras funções para registrar diferentes tipos de atalhos aqui no futuro.