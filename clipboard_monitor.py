# clipboard_monitor.py
import threading
import pyperclip
import time


class ClipboardMonitorThread(threading.Thread):
    def __init__(self, app_instance):
        """
        Inicializa a thread de monitoramento do clipboard.
        :param app_instance: A instância da aplicação principal (ColaSequenciaApp).
                             Precisamos dela para acessar/modificar variáveis da app
                             (last_copied_text, ignore_next_clipboard_change)
                             e para usar o app.after() para chamadas thread-safe à GUI.
        """
        super().__init__(daemon=True)  # daemon=True faz a thread fechar com o app
        self.app = app_instance
        # As variáveis self.app.last_copied_text e self.app.ignore_next_clipboard_change
        # são inicializadas e gerenciadas pela instância da app.

    def run(self):
        """
        Este método é executado quando a thread é iniciada.
        Contém o loop principal de monitoramento.
        """
        print("--- Thread de Monitoramento da Área de Transferência Iniciada ---")
        while True:
            try:
                current_clipboard_text = pyperclip.paste()

                if self.app.ignore_next_clipboard_change:
                    # print("Monitor: Ignorando mudança de clipboard (gerada pelo app).") # Log opcional
                    self.app.last_copied_text = current_clipboard_text
                    self.app.ignore_next_clipboard_change = False
                    time.sleep(0.1)  # Pequena pausa
                    continue  # Pula para a próxima iteração

                if current_clipboard_text != self.app.last_copied_text:
                    # print(f"Monitor: Mudança detectada - '{current_clipboard_text[:30]}...'") # Log opcional
                    self.app.last_copied_text = current_clipboard_text
                    # Agenda a chamada para add_item_to_gui_history na thread principal da GUI
                    self.app.after(0, self.app.add_item_to_gui_history, current_clipboard_text)

            except pyperclip.PyperclipException:
                # Ocorre se o conteúdo não for texto (ex: imagem)
                self.app.last_copied_text = ""  # Limpa para evitar repetição do erro
                pass  # Ignora por enquanto
            except Exception as e:
                print(f"Erro na Thread de Monitoramento: {e}")
                # Considerar uma forma de notificar o usuário ou parar graciosamente em caso de erros repetidos.

            time.sleep(0.5)  # Intervalo de verificação