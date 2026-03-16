## ColaSequência Pro Tabs! Clipboard Manager 📋

Um gerenciador de área de transferência avançado, feito em Python com CustomTkinter, projetado para aumentar a produtividade ao salvar, organizar e colar snippets de texto rapidamente através de abas e atalhos globais.

## 🖼️

![Animação](https://github.com/user-attachments/assets/e9413766-72ac-4982-9896-204e48e183c9)

## 📖 Índice

* [Visão Geral](#-visão-geral)
* [Principais Funcionalidades](#-principais-funcionalidades)
* [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
* [Como Usar (Para Desenvolvedores)](#-como-usar-para-desenvolvedores)
  * [Pré-requisitos](#pré-requisitos)
  * [Instalação](#instalação)
  * [Executando a Aplicação](#executando-a-aplicação)
* [Próximos Passos](#-próximos-passos)
* [Autor](#️-autor)
* [Licença](#-licença)

-----

## 💡 Visão Geral

**ColaSequência Pro Tabs\!** é mais do que um simples histórico de "copiar e colar". É uma ferramenta de produtividade que permite ao usuário salvar textos e comandos usados com frequência em "gavetas" (snippets) organizadas por abas. Com atalhos de teclado globais, você pode colar qualquer um desses snippets em qualquer aplicativo, agilizando seu fluxo de trabalho.

Além disso, a aplicação mantém um histórico automático e opcional de tudo que é copiado para a área de transferência, garantindo que você nunca perca um item importante.

-----

## ✨ Principais Funcionalidades

  * **Snippets Manuais Editáveis:** 9 espaços por aba para você salvar e editar textos multi-linha.
  * **Abas Organizacionais:** Crie e remova abas para organizar seus snippets por contexto (Trabalho, Estudos, Geral, etc.).
  * **Persistência de Dados:** Todos os seus snippets e abas são salvos em um arquivo `JSON` e recarregados automaticamente quando o aplicativo é iniciado.
  * **Atalhos Globais:** Use `Shift` + `Ctrl` + `[1-9]` para colar instantaneamente o snippet correspondente da aba ativa em qualquer programa.
  * **Histórico Automático Opcional:** Uma seção separada e colapsável que exibe um histórico dos últimos 20 itens copiados.
  * **Interface Moderna:** Construído com a biblioteca CustomTkinter para um visual agradável e moderno.

-----

## 🛠️ Tecnologias Utilizadas

  * **Python 3**
  * **CustomTkinter:** Para a criação da interface gráfica.
  * **Pyperclip:** Para interagir com a área de transferência do sistema.
  * **Keyboard:** Para registrar e gerenciar os atalhos de teclado globais.

-----

## 🚀 Como Usar (Para Desenvolvedores)

Se você deseja executar este projeto a partir do código-fonte, siga os passos abaixo.

### Pré-requisitos

  * **Python 3.10 ou superior** instalado.
  * **Git** instalado (para clonar o repositório).

### Instalação

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/joaquim-jf/ClipboardManager-Python
    cd SEU-REPOSITORIO
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    # Criar o ambiente virtual
    python -m venv .venv

    # Ativar no Windows (cmd)
    .venv\Scripts\activate

    # Ativar no macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

### Executando a Aplicação

1.  Com o ambiente virtual ativado, execute o script principal:

    ```bash
    python main.py
    ```

2.  **❗ IMPORTANTE: Permissões de Administrador**
    Para que os atalhos de teclado globais (`Shift` + `Ctrl` + `Número`) funcionem corretamente, pode ser necessário executar o script com privilégios de administrador.

      * **No Windows:** Execute seu terminal ou PyCharm como "Administrador" antes de rodar o comando `python main.py`.

-----

## 🔮 Próximos Passos

O projeto ainda está em evolução !

-----

## ✍️ Autor

**JF\_KING\_083**

  * GitHub: https://github.com/joaquim-jf
  * LinkedIn: https://www.linkedin.com/in/joaquim-felix-jf

-----

## Licença

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).

