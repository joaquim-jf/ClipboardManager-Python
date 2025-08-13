# data_manager.py
import json
import os

DATA_FILENAME = ".venv/colasquencia_data.json"  # Nome do arquivo de dados


def load_app_data(initial_default_tab_names, num_slots_per_tab):
    """
    Carrega os dados das abas e snippets do arquivo JSON.
    Prioriza dados do arquivo, mas garante que as abas padrão existam
    e que todas as abas tenham o número correto de slots.
    """
    print(f"--- [Data Manager] Tentando carregar dados de {DATA_FILENAME} ---")
    loaded_data_from_file = {}
    file_was_read_successfully = False

    if os.path.exists(DATA_FILENAME):
        try:
            with open(DATA_FILENAME, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                loaded_data_from_file = data
                file_was_read_successfully = True
                print(f"--- [Data Manager] Dados carregados do arquivo: {list(loaded_data_from_file.keys())}")
            else:
                print(f"--- [Data Manager] Erro: Formato de dados inválido no arquivo JSON. Esperado um dicionário.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"--- [Data Manager] Erro ao ler/decodificar {DATA_FILENAME}: {e}.")
        except Exception as e:
            print(f"--- [Data Manager] Erro inesperado ao carregar {DATA_FILENAME}: {e}.")
    else:
        print(f"--- [Data Manager] Arquivo {DATA_FILENAME} não encontrado.")

    # Começa com os dados carregados do arquivo (se houver e forem válidos)
    # ou um dicionário vazio caso contrário.
    final_tabs_data = loaded_data_from_file if file_was_read_successfully else {}

    # Garante que todas as abas padrão (`initial_default_tab_names`) estejam presentes.
    # Se uma aba padrão não estiver nos dados carregados, ela é adicionada com snippets vazios.
    for tab_name in initial_default_tab_names:
        if tab_name not in final_tabs_data:
            print(f"--- [Data Manager] Aba padrão '{tab_name}' não encontrada. Adicionando com snippets vazios.")
            final_tabs_data[tab_name] = [""] * num_slots_per_tab

    # Agora, verifica todas as abas em final_tabs_data (tanto as do arquivo quanto as padrões adicionadas)
    # para garantir que tenham o número correto de slots e o formato correto.
    # Iteramos sobre uma cópia das chaves se formos modificar o dicionário (adicionar/remover chaves),
    # mas aqui estamos apenas modificando os valores (listas de snippets) ou garantindo que existam.
    all_tab_names_to_ensure = list(final_tabs_data.keys())  # Pega todas as chaves atuais
    if not all_tab_names_to_ensure and initial_default_tab_names:  # Se o arquivo estava vazio ou corrupto e temos padrões
        all_tab_names_to_ensure = list(initial_default_tab_names)
        for tab_name in all_tab_names_to_ensure:  # Recria a estrutura base
            final_tabs_data[tab_name] = [""] * num_slots_per_tab

    for tab_name in all_tab_names_to_ensure:
        # Se a aba veio do arquivo mas está malformada ou com número errado de slots
        if not isinstance(final_tabs_data.get(tab_name), list) or len(final_tabs_data[tab_name]) != num_slots_per_tab:
            print(
                f"--- [Data Manager] Aba '{tab_name}' com dados malformados ou número incorreto de slots. Padronizando.")
            final_tabs_data[tab_name] = [""] * num_slots_per_tab

    print(f"--- [Data Manager] Carga de dados finalizada. Abas processadas: {list(final_tabs_data.keys())}")
    return final_tabs_data


def save_app_data(tabs_data_to_save):
    """
    Salva o dicionário de dados das abas (tabs_data) em um arquivo JSON.
    """
    print(f"--- [Data Manager] Tentando salvar dados em {DATA_FILENAME} ---")
    try:
        with open(DATA_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(tabs_data_to_save, f, ensure_ascii=False, indent=4)
        print(f"--- [Data Manager] Dados ({len(tabs_data_to_save)} abas) salvos com sucesso em {DATA_FILENAME}!")
        return True
    except IOError as e:
        print(f"--- [Data Manager] Erro de I/O ao salvar dados em {DATA_FILENAME}: {e}")
    except Exception as e:
        print(f"--- [Data Manager] Erro inesperado ao salvar dados: {e}")
    return False