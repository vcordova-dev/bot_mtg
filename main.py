import customtkinter as ctk
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

# Configuração da aparência
ctk.set_appearance_mode("dark")  # Modos: "system" (default), "dark", "light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (default), "green", "dark-blue"

# Configuração da janela principal
app = ctk.CTk()
app.geometry("500x500")
app.title("SAÍDA MONTAGEM")

# Definindo o diretório para salvar arquivos
directory = r"Z:\bot_mtg"
if not os.path.exists(directory):
    os.makedirs(directory)

directory_xml = r"Z:\bot_mtg\xml"
if not os.path.exists(directory_xml):
    os.makedirs(directory)

# Função para lidar com o submit ao pressionar Enter
def on_enter(event):
    handle_submit()

# Lista para armazenar os últimos 5 envios
history = []

# Função para carregar contadores do arquivo de persistência
def load_counters():
    global count_option1, count_option2, last_update_date, total
    counters_file_path = os.path.join(directory, "counters.txt")
    if os.path.exists(counters_file_path):
        with open(counters_file_path, "r") as file:
            lines = file.readlines()
            if len(lines) == 4:
                last_update_date = lines[0].split(": ")[1].strip()
                count_option1 = int(lines[1].split(": ")[1].strip())
                count_option2 = int(lines[2].split(": ")[1].strip())
                total = int(lines[3].split(": ")[1].strip())
            else:
                reset_counters()
    else:
        reset_counters()

# Função para salvar contadores no arquivo de persistência
def save_counters():
    counters_file_path = os.path.join(directory, "counters.txt")
    with open(counters_file_path, "w") as file:
        file.write(f"Data: {last_update_date}\n")
        file.write(f"Maicon: {count_option1}\n")
        file.write(f"Guilherme: {count_option2}\n")
        file.write(f"Total: {total}\n")

# Função para reiniciar os contadores
def reset_counters():
    global count_option1, count_option2, last_update_date, total
    count_option1 = 0
    count_option2 = 0
    total = 0
    last_update_date = datetime.now().strftime("%Y-%m-%d")
    save_counters()

# Verifica se é necessário reiniciar os contadores
def check_reset_counters():
    global last_update_date
    current_date = datetime.now().strftime("%Y-%m-%d")
    if (current_date != last_update_date):
        reset_counters()

# Função para atualizar o widget de histórico
def update_history_textbox():
    history_textbox.configure(state="normal")
    history_textbox.delete("1.0", "end")
    for entry in history:
        history_textbox.insert("end", entry + "\n")
    history_textbox.insert("end", f"Total Maicon: {count_option1}\n")
    history_textbox.insert("end", f"Total Guilherme: {count_option2}\n")
    history_textbox.insert("end", f"Total: {total}\n")
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
    tree.write(os.path.join(directory_xml, filename), encoding="utf-8", xml_declaration=True)

# Função para salvar dados no arquivo de log diário
def save_to_log(selected_option, input_text):
    log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    log_file_path = os.path.join(directory, log_filename)
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%H:%M:%S')} - MONTADOR: {selected_option}, PEDIDO: {input_text}\n")

# Função para lidar com o submit
def handle_submit():
    global count_option1, count_option2, total
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
    
    total = count_option1 + count_option2

    history.append(f"MONTADOR: {selected_option}, PEDIDO: {input_text}")
    
    # Mantém apenas os últimos 5 envios
    if len(history) > 5:
        history.pop(0)
    
    # Atualiza o conteúdo do widget de texto
    update_history_textbox()
    
    input_var.set("")  # Limpa o campo de entrada após o submit

    # Salva os dados em um arquivo XML
    save_to_xml(selected_option, input_text)

    # Salva os dados no arquivo de log diário
    save_to_log(selected_option, input_text)

    # Salva os contadores no arquivo de persistência
    save_counters()

# Função para criar o arquivo de resumo diário
def create_summary_file():
    log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    log_file_path = os.path.join(directory, log_filename)
    summary_filename = f"resumo_{datetime.now().strftime('%Y-%m-%d')}.txt"
    summary_file_path = os.path.join(directory, summary_filename)

    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            log_content = log_file.read()

        with open(summary_file_path, "w") as summary_file:
            summary_file.write(f"Resumo Diário - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            summary_file.write(f"\nTotal Maicon: {count_option1}\n")
            summary_file.write(f"Total Guilherme: {count_option2}\n")
            summary_file.write(f"Total: {total}\n\n")
            # summary_file.write(log_content)
    
    return summary_file_path

# Função para enviar e-mails
def send_email(summary_file_path):
    email_user = 'vcordova@embrapolsul.com.br'
    email_password = '996576298'
    email_send = 'jalmeida@embrapolsul.com.br'
    
    subject = f"Resumo Diário - {datetime.now().strftime('%Y-%m-%d')}"

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    with open(summary_file_path, 'r') as f:
        summary_content = f.read()

    msg.attach(MIMEText(summary_content, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, email_send, text)
            print("E-mail enviado com sucesso")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

# Função para o trabalho agendado
def job():
    summary_file_path = create_summary_file()
    if os.path.exists(summary_file_path):
        send_email(summary_file_path)

# Agendamento diário às 21:00
schedule.every().day.at("22:00").do(job)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

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

# Função principal da aplicação
def main():
    # Carrega os contadores ao iniciar a aplicação
    load_counters()
    check_reset_counters()
    update_history_textbox()

    # Inicia a thread para o agendamento
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()

    # Loop principal da aplicação
    app.mainloop()

if __name__ == "__main__":
    main()
