import customtkinter as ctk
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# Configuração da aparência
ctk.set_appearance_mode("dark")  # Modos: "system" (default), "dark", "light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (default), "green", "dark-blue"

# Configuração da janela principal
app = ctk.CTk()
app.geometry("500x500")
app.title("SAÍDA MONTAGEM")

# Função para lidar com o submit ao pressionar Enter
def on_enter(event):
    handle_submit()

# Lista para armazenar os últimos 5 envios
history = []

# Função para carregar contadores do arquivo de persistência
def load_counters():
    global count_option1, count_option2, last_update_date
    if os.path.exists("counters.txt"):
        with open("counters.txt", "r") as file:
            lines = file.readlines()
            if len(lines) == 3:
                last_update_date = lines[0].strip()
                count_option1 = int(lines[1].strip())
                count_option2 = int(lines[2].strip())
            else:
                reset_counters()
    else:
        reset_counters()

# Função para salvar contadores no arquivo de persistência
def save_counters():
    with open("counters.txt", "w") as file:
        file.write(f"{last_update_date}\n")
        file.write(f"{count_option1}\n")
        file.write(f"{count_option2}\n")

# Função para reiniciar os contadores
def reset_counters():
    global count_option1, count_option2, last_update_date
    count_option1 = 0
    count_option2 = 0
    last_update_date = datetime.now().strftime("%Y-%m-%d")
    save_counters()

# Verifica se é necessário reiniciar os contadores
def check_reset_counters():
    global last_update_date
    current_date = datetime.now().strftime("%Y-%m-%d")
    if current_date != last_update_date:
        reset_counters()

# Função para atualizar o widget de histórico
def update_history_textbox():
    history_textbox.configure(state="normal")
    history_textbox.delete("1.0", "end")
    for entry in history:
        history_textbox.insert("end", entry + "\n")
    history_textbox.insert("end", f"Total Maicon: {count_option1}\n")
    history_textbox.insert("end", f"Total Guilherme: {count_option2}\n")
    history_textbox.configure(state="disabled")

# Função para salvar dados em um arquivo XML
def save_to_xml(selected_option, input_text):
    entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Criação do elemento raiz
    root = ET.Element("PEDIDO")
    
    # Adicionando elementos
    option_elem = ET.SubElement(root, "MONTADOR")
    option_elem.text = selected_option
    
    input_elem = ET.SubElement(root, "OP")
    input_elem.text = input_text
    
    time_elem = ET.SubElement(root, "DATA_HORA")
    time_elem.text = entry_time
    
    # Criação da árvore XML
    tree = ET.ElementTree(root)
    
    # Salvando o XML em um arquivo
    filename = f"{input_text}{datetime.now().strftime('_%H%M%S')}.xml"
    tree.write(filename, encoding="utf-8", xml_declaration=True)

# Função para lidar com o submit
def handle_submit():
    global count_option1, count_option2
    selected_option = option_var.get()
    input_text = input_var.get()

    # Validação para garantir que o input seja um número inteiro
    if not input_text.isdigit():
        error_label.configure(text="Erro: O campo de entrada deve conter apenas números inteiros")
        return
    else:
        error_label.configure(text="")  # Limpa a mensagem de erro se a entrada for válida
    
    # Validação para garantir que uma opção válida seja selecionada
    if selected_option not in ["Maicon", "Guilherme"]:
        error_label.configure(text="Erro: Selecione um montador válido")
        return
    
    # Incrementar o contador de acordo com a opção selecionada
    if selected_option == "Maicon":
        count_option1 += 1
    elif selected_option == "Guilherme":
        count_option2 += 1

    history.append(f"MONTADOR: {selected_option}, PEDIDO: {input_text}")
    
    # Mantém apenas os últimos 5 envios
    if len(history) > 5:
        history.pop(0)
    
    # Atualiza o conteúdo do widget de texto
    update_history_textbox()
    
    input_var.set("")  # Limpa o campo de entrada após o submit

    # Salva os dados em um arquivo XML
    save_to_xml(selected_option, input_text)

    # Salva os contadores no arquivo de persistência
    save_counters()

# Variável para armazenar a opção selecionada
option_var = ctk.StringVar(value="Selecione um montador")

# Caixa de seleção com duas opções
option_menu = ctk.CTkOptionMenu(app, variable=option_var, values=["Selecione um montador", "Maicon", "Guilherme"])
option_menu.pack(pady=10)

# Variável para armazenar o texto de entrada
input_var = ctk.StringVar()

# Caixa de entrada de dados
input_entry = ctk.CTkEntry(app, textvariable=input_var, width=300, height=30, corner_radius=10)
input_entry.pack(pady=10)
input_entry.bind("<Return>", on_enter)  # Bind da tecla Enter para submeter

# Rótulo para exibir mensagens de erro
error_label = ctk.CTkLabel(app, text="", text_color="red")
error_label.pack(pady=5)

# Botão de submit para quem preferir clicar ao invés de pressionar Enter
submit_button = ctk.CTkButton(app, text="ENVIAR", command=handle_submit, width=100, height=40, corner_radius=10)
submit_button.pack(pady=10)

# Widget de texto para mostrar o histórico
history_textbox = ctk.CTkTextbox(app, width=450, height=200, corner_radius=10)
history_textbox.pack(pady=10)
history_textbox.configure(state="disabled")

# Carrega os contadores ao iniciar a aplicação
load_counters()
check_reset_counters()
update_history_textbox()

# Loop principal da aplicação
app.mainloop()
