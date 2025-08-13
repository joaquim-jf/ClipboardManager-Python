# main.py
import customtkinter as ctk
import pyperclip
from collections import deque
import keyboard
import os
import json

# Imports dos nossos módulos customizados
from clipboard_monitor import ClipboardMonitorThread
from hotkey_manager import register_snippet_hotkeys
import data_manager

# Configurações Iniciais do CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# --- Classe para o Diálogo de Confirmação de Salvamento usando CTkToplevel ---
class SaveChangesDialog(ctk.CTkToplevel):
    def __init__(self, parent_window, title="Salvar Alterações?",
                 message="Você tem alterações não salvas.\nDeseja salvar antes de sair?"):
        super().__init__(master=parent_window)

        self.title(title)
        self.geometry("420x180")
        self._user_choice = "cancel"

        self.grab_set()
        self.focus_force()
        self.resizable(False, False)
        self.transient(parent_window)

        self.main_label = ctk.CTkLabel(self, text=message, wraplength=380, justify="left", font=ctk.CTkFont(size=14))
        self.main_label.pack(pady=20, padx=20, fill="x", expand=True)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(10, 20), padx=20, fill="x")

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancelar", width=110, command=self._cancel_action,
                                           fg_color="gray50")
        self.cancel_button.pack(side="right", padx=5)

        self.discard_button = ctk.CTkButton(self.button_frame, text="Não Salvar", width=110,
                                            command=self._discard_action)
        self.discard_button.pack(side="right", padx=5)

        self.save_button = ctk.CTkButton(self.button_frame, text="Salvar", width=110, command=self._save_action,
                                         fg_color="green")
        self.save_button.pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self._cancel_action)
        self.after(100, self.lift)

    def _save_action(self):
        self._user_choice = "save"
        self.destroy()

    def _discard_action(self):
        self._user_choice = "discard"
        self.destroy()

    def _cancel_action(self):
        self._user_choice = "cancel"
        self.destroy()

    def get_choice(self):
        self.master.wait_window(self)
        return self._user_choice


# --- Classe Principal da Aplicação ---
class ColaSequenciaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ColaSequência Pro Tabs!")
        self.geometry("750x700")
        self.minsize(650, 500)

        # ---- Configurar Ícone da Janela ----
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "assets", "app_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                print(f"Ícone '{icon_path}' carregado.")
            else:
                print(f"AVISO: Ícone '{icon_path}' não encontrado. Usando ícone padrão.")
        except Exception as e:
            print(f"Erro ao tentar carregar o ícone: {e}")

        # ---- Inicialização dos Dados e Flags ----
        self.clipboard_history = deque(maxlen=20)
        self.last_copied_text = ""
        self.is_history_visible = False
        self.num_slots = 9
        self.initial_default_tab_names = ["Geral", "Trabalho", "Estudos"]
        self.tabs_data = data_manager.load_app_data(self.initial_default_tab_names, self.num_slots)
        self.tab_snippet_textboxes = {}
        self.unsaved_changes = False
        self.is_hotkey_action_in_progress = False
        self.hotkey_debounce_time = 300
        self.ignore_next_clipboard_change = False

        # ---- Configuração da UI ----
        self.main_app_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_app_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_app_frame.grid_columnconfigure(0, weight=1)
        self.main_app_frame.grid_rowconfigure(0, weight=0)
        self.main_app_frame.grid_rowconfigure(1, weight=1)
        self.main_app_frame.grid_rowconfigure(2, weight=0)
        self.main_app_frame.grid_rowconfigure(3, weight=0)

        self.control_buttons_frame = ctk.CTkFrame(self.main_app_frame, fg_color="transparent")
        self.control_buttons_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 10))

        self.add_tab_button = ctk.CTkButton(self.control_buttons_frame, text="Nova Aba (+)",
                                            command=self.ask_new_tab_name, width=130)
        self.add_tab_button.pack(side="left", padx=(0, 5))
        self.remove_tab_button = ctk.CTkButton(self.control_buttons_frame, text="Remover Aba (-)",
                                               command=self.ask_delete_current_tab, width=150)
        self.remove_tab_button.pack(side="left", padx=(0, 5))
        self.toggle_history_button = ctk.CTkButton(self.control_buttons_frame, text="Mostrar Histórico",
                                                   command=self.toggle_history_visibility, width=150)
        self.toggle_history_button.pack(side="left", padx=(0, 5))

        self.tab_view = ctk.CTkTabview(self.main_app_frame)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)
        if not self.tabs_data and self.initial_default_tab_names:
            self.tabs_data = data_manager.load_app_data(self.initial_default_tab_names, self.num_slots)

        for tab_name in list(self.tabs_data.keys()):
            self.create_ui_for_tab(tab_name)
        if list(self.tabs_data.keys()):
            self.tab_view.set(list(self.tabs_data.keys())[0])

        self.history_section_frame = ctk.CTkFrame(self.main_app_frame)
        history_auto_label = ctk.CTkLabel(self.history_section_frame, text="Histórico Automático de Cópia:",
                                          font=ctk.CTkFont(size=14, weight="bold"))
        history_auto_label.pack(pady=5, padx=5, anchor="w")
        self.history_textbox = ctk.CTkTextbox(self.history_section_frame, wrap="word")
        self.history_textbox.pack(fill="both", expand=True, pady=(0, 5), padx=5)
        self.history_textbox.insert("0.0", "Itens copiados recentemente aparecerão aqui...\n")
        self.history_textbox.configure(state="disabled")
        self.toggle_history_visibility(initial_setup=True)

        self.bottom_frame = ctk.CTkFrame(self.main_app_frame, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(10, 0))
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.save_button = ctk.CTkButton(self.bottom_frame, text="Salvar Tudo", command=self.handle_save_button_press,
                                         width=120)
        self.save_button.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.credits_label = ctk.CTkLabel(self.bottom_frame, text="Create by JF_KING_083", font=ctk.CTkFont(size=10),
                                          text_color="gray")
        self.credits_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        print("--- __init__: UI configurada ---")

        # ---- Inicialização dos Módulos de Background ----
        self.start_clipboard_monitoring()
        register_snippet_hotkeys(
            paste_callback_func=self.paste_from_history_via_hotkey,
            num_slots=self.num_slots
        )
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui_for_tab(self, tab_name):
        if tab_name not in self.tab_snippet_textboxes:
            self.tab_snippet_textboxes[tab_name] = []
        else:
            for widget in self.tab_snippet_textboxes[tab_name]: widget.destroy()
            self.tab_snippet_textboxes[tab_name].clear()
        try:
            current_tab_ui_frame = self.tab_view.tab(tab_name)
            for widget in current_tab_ui_frame.winfo_children(): widget.destroy()
        except ValueError:
            current_tab_ui_frame = self.tab_view.add(tab_name)
        scrollable_snippets_frame = ctk.CTkScrollableFrame(current_tab_ui_frame, fg_color="transparent")
        scrollable_snippets_frame.pack(fill="both", expand=True, padx=0, pady=0)
        for i in range(self.num_slots):
            slot_frame = ctk.CTkFrame(scrollable_snippets_frame, fg_color="transparent")
            slot_frame.pack(fill="x", pady=3, padx=5)
            label = ctk.CTkLabel(slot_frame, text=f"{i + 1}:", width=25, anchor="w")
            label.pack(side="left", padx=(0, 5), pady=(5, 0))
            textbox_snippet = ctk.CTkTextbox(slot_frame, height=60, wrap="word", activate_scrollbars=True)
            textbox_snippet.pack(side="left", fill="x", expand=True)
            if tab_name in self.tabs_data and i < len(self.tabs_data[tab_name]):
                textbox_snippet.insert("0.0", self.tabs_data[tab_name][i])
            self.tab_snippet_textboxes[tab_name].append(textbox_snippet)
            textbox_snippet.bind("<FocusOut>",
                                 lambda event, tn=tab_name, si=i, tb=textbox_snippet:
                                 self.snippet_textbox_changed(tn, si, tb))

    def ask_new_tab_name(self):
        dialog = ctk.CTkInputDialog(text="Digite o nome da nova aba:", title="Adicionar Nova Aba")
        new_name_candidate = dialog.get_input()
        if new_name_candidate:
            new_name = new_name_candidate.strip()
            if not new_name: print("Nome da aba não pode ser vazio."); return
            if new_name in self.tabs_data: print(f"Aba '{new_name}' já existe."); return
            self.add_new_tab(new_name)
        else:
            print("Criação de nova aba cancelada.")

    def add_new_tab(self, tab_name):
        if tab_name not in self.tabs_data:
            self.tabs_data[tab_name] = [""] * self.num_slots
            self.create_ui_for_tab(tab_name)
            self.tab_view.set(tab_name)
            self.unsaved_changes = True

    def ask_delete_current_tab(self):
        if len(self.tabs_data) <= 1: print("Não é possível remover a última aba."); return
        current_tab_name = self.tab_view.get()
        if not current_tab_name: print("Nenhuma aba selecionada para remover."); return
        confirm_dialog = ctk.CTkInputDialog(
            text=f"Tem certeza que deseja remover a aba '{current_tab_name}'?\nIsso não pode ser desfeito.\n\nDigite '{current_tab_name}' para confirmar:",
            title="Confirmar Remoção de Aba"
        )
        confirmation_text = confirm_dialog.get_input()
        if confirmation_text == current_tab_name:
            self.delete_tab_action(current_tab_name)
        else:
            print(f"Remoção da aba '{current_tab_name}' cancelada ou confirmação incorreta.")

    def delete_tab_action(self, tab_name_to_delete):
        if tab_name_to_delete not in self.tabs_data: return
        try:
            self.tab_view.delete(tab_name_to_delete)
            if tab_name_to_delete in self.tabs_data: del self.tabs_data[tab_name_to_delete]
            if tab_name_to_delete in self.tab_snippet_textboxes: del self.tab_snippet_textboxes[tab_name_to_delete]
            self.unsaved_changes = True
            print(f"Aba '{tab_name_to_delete}' removida.")
        except Exception as e:
            print(f"Erro ao remover aba '{tab_name_to_delete}': {e}")

    def snippet_textbox_changed(self, tab_name, slot_index, textbox_widget):
        # --- VERSÃO DE DEPURAÇÃO DESTE MÉTODO ---
        print("\n--- Evento FocusOut no snippet detectado! ---")
        new_text = textbox_widget.get("0.0", "end-1c")
        current_saved_text = "ERRO: DADOS INTERNOS NÃO ENCONTRADOS"
        if tab_name in self.tabs_data and 0 <= slot_index < len(self.tabs_data[tab_name]):
            current_saved_text = self.tabs_data[tab_name][slot_index]
        print(f"Texto na UI: '{new_text}'")
        print(f"Texto Salvo: '{current_saved_text}'")
        if new_text != current_saved_text:
            print(">>> VEREDITO: Os textos são DIFERENTES. Marcando como 'não salvo'.")
            self.tabs_data[tab_name][slot_index] = new_text
            self.unsaved_changes = True
        else:
            print(">>> VEREDITO: Os textos são IGUAIS. Nenhuma alteração detectada.")

    def paste_from_history_via_hotkey(self, hotkey_index):
        if self.is_hotkey_action_in_progress: return
        self.is_hotkey_action_in_progress = True
        self.after(self.hotkey_debounce_time, self.reset_hotkey_flag)
        try:
            current_tab_name = self.tab_view.get()
            if not current_tab_name: self.is_hotkey_action_in_progress = False; return
            actual_index = hotkey_index - 1
            if current_tab_name in self.tab_snippet_textboxes and \
                    0 <= actual_index < len(self.tab_snippet_textboxes[current_tab_name]):
                textbox_widget = self.tab_snippet_textboxes[current_tab_name][actual_index]
                item_to_paste = textbox_widget.get("0.0", "end-1c")
                if item_to_paste:
                    self.ignore_next_clipboard_change = True
                    pyperclip.copy(item_to_paste)
                    self.after(50, lambda: keyboard.press_and_release('ctrl+v'))
            # else: logs opcionais
        except Exception as e:
            print(f"Erro no atalho: {e}")
            self.is_hotkey_action_in_progress = False

    def reset_hotkey_flag(self):
        self.is_hotkey_action_in_progress = False

    def add_item_to_gui_history(self, new_text):
        if new_text and (not self.clipboard_history or new_text != self.clipboard_history[0]):
            self.clipboard_history.appendleft(new_text)
            if self.is_history_visible: self.update_automatic_history_textbox()

    def update_automatic_history_textbox(self):
        if not hasattr(self, 'history_textbox') or not self.history_textbox.winfo_exists(): return
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")
        for i, item in enumerate(self.clipboard_history):
            display_text = f"- {item[:150]}{'...' if len(item) > 150 else ''}\n\n"
            self.history_textbox.insert("end", display_text)
        self.history_textbox.configure(state="disabled")

    def toggle_history_visibility(self, initial_setup=False):
        if not initial_setup: self.is_history_visible = not self.is_history_visible
        if self.is_history_visible:
            self.history_section_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5, 0))
            self.main_app_frame.grid_rowconfigure(2, weight=1)
            self.update_automatic_history_textbox()
            self.toggle_history_button.configure(text="Ocultar Histórico")
            if not initial_setup: print("--- Histórico Automático Visível ---")
        else:
            self.history_section_frame.grid_remove()
            self.main_app_frame.grid_rowconfigure(2, weight=0)
            self.toggle_history_button.configure(text="Mostrar Histórico")
            if not initial_setup: print("--- Histórico Automático Oculto ---")

    def start_clipboard_monitoring(self):
        self.monitor_thread = ClipboardMonitorThread(app_instance=self)
        self.monitor_thread.start()

    def handle_save_button_press(self):
        print("--- Botão 'Salvar Tudo' pressionado ---")
        success = data_manager.save_app_data(self.tabs_data)
        if success:
            print("Dados salvos com sucesso pelo botão!")
            self.unsaved_changes = False
        else:
            print("Falha ao salvar os dados pelo botão.")

    def on_closing(self):
        if self.unsaved_changes:
            dialog = SaveChangesDialog(parent_window=self)
            choice = dialog.get_choice()
            if choice == "save":
                self.handle_save_button_press()
                self.destroy()
            elif choice == "discard":
                self.destroy()
            elif choice == "cancel":
                return
        else:
            self.destroy()


# Bloco principal para executar o aplicativo
if __name__ == "__main__":
    print("Criando a instância do app ColaSequência.")
    app = ColaSequenciaApp()
    print("Iniciando o mainloop do ColaSequência.")
    app.mainloop()
    print("Mainloop do ColaSequência finalizado.")