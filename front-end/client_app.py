import os
import subprocess
import ssl
import requests

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ModuleNotFoundError:
    print("Le module tkinter est manquant.")
    exit(1)

API_URL = "http://127.0.0.1:8000/auth"
REGISTER_URL = "http://127.0.0.1:8000/register"
CONFIG_DIR = "./client-configs"

# 🎨 Styles globaux
BG_COLOR = "#f0f4f7"
ENTRY_BG = "white"
BTN_COLOR = "#007acc"
BTN_TEXT = "white"
LABEL_COLOR = "#333"
FONT = ("Segoe UI", 10)

def login():
    username = username_entry.get()
    password = password_entry.get()
    data = {'username': username, 'password': password}
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            login_window.destroy()
            open_server_selection()
        else:
            messagebox.showerror("Erreur", "Identifiants invalides !")
    except Exception as e:
        messagebox.showerror("Erreur", f"API inaccessible : {e}")

def open_register_window():
    login_window.destroy()
    register_window = tk.Tk()
    register_window.title("Créer un compte")
    register_window.configure(bg=BG_COLOR)
    register_window.geometry("350x300")
    register_window.resizable(False, False)

    container = tk.Frame(register_window, bg=BG_COLOR)
    container.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(container, text="Nom d'utilisateur :", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT).pack(pady=(10, 0))
    new_username_entry = tk.Entry(container, bg=ENTRY_BG, font=FONT, width=30)
    new_username_entry.pack(pady=5)

    tk.Label(container, text="Mot de passe :", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT).pack(pady=(10, 0))
    new_password_entry = tk.Entry(container, show="*", bg=ENTRY_BG, font=FONT, width=30)
    new_password_entry.pack(pady=5)

    def register():
        username = new_username_entry.get()
        password = new_password_entry.get()
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        data = {'username': username, 'password': password}
        try:
            response = requests.post(REGISTER_URL, json=data)
            if response.status_code == 200:
                messagebox.showinfo("Succès", "Compte créé avec succès !")
                register_window.destroy()
                main_login_window()  # Redirige vers login
            else:
                messagebox.showerror("Erreur", response.json().get("detail", "Erreur inconnue"))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'inscription : {e}")

    tk.Button(container, text="S'inscrire", command=register,
              bg=BTN_COLOR, fg=BTN_TEXT, font=FONT, width=20).pack(pady=15)

    register_window.mainloop()

def open_server_selection():
    selection_window = tk.Tk()
    selection_window.title("Choix du serveur VPN")
    selection_window.configure(bg=BG_COLOR)
    selection_window.geometry("400x400")
    selection_window.resizable(False, False)

    container = tk.Frame(selection_window, bg=BG_COLOR)
    container.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(container, text="Sélectionnez un serveur VPN", bg=BG_COLOR, fg=LABEL_COLOR,
             font=("Segoe UI", 12, "bold")).pack(pady=(10, 15))

    ovpn_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".ovpn")]
    if not ovpn_files:
        messagebox.showerror("Erreur", "Aucun fichier .ovpn trouvé.")
        selection_window.destroy()
        return

    var = tk.StringVar(value=ovpn_files[0])

    radio_frame = tk.Frame(container, bg=BG_COLOR)
    radio_frame.pack(pady=5)

    for file in ovpn_files:
        tk.Radiobutton(radio_frame, text=file, variable=var, value=file,
                       bg=BG_COLOR, fg=LABEL_COLOR, font=FONT, anchor='w',
                       width=30, justify='left').pack(anchor='w', padx=10, pady=2)

    def proceed():
        selected_file = var.get()
        cert_path = filedialog.askopenfilename(title="Certificat .crt", filetypes=[("Certificat", "*.crt")])
        key_path = filedialog.askopenfilename(title="Clé privée .key", filetypes=[("Clé", "*.key")])

        if not cert_path or not key_path:
            messagebox.showerror("Erreur", "Certificat ou clé non sélectionné.")
            return

        run_openvpn(selected_file, cert_path, key_path)

    tk.Button(container, text="Se connecter", command=proceed,
              bg=BTN_COLOR, fg="white", font=FONT, width=25).pack(pady=20)

    selection_window.mainloop()

def run_openvpn(ovpn_file, cert_file, key_file):
    full_ovpn_path = os.path.join(CONFIG_DIR, ovpn_file)
    cmd = ["sudo", "openvpn", "--config", full_ovpn_path, "--cert", cert_file, "--key", key_file]
    terminal_cmd = ["x-terminal-emulator", "-e"] + cmd
    try:
        subprocess.Popen(terminal_cmd)
        messagebox.showinfo("Info", "Connexion VPN en cours...")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def main_login_window():
    global login_window, username_entry, password_entry
    login_window = tk.Tk()
    login_window.title("Connexion à la plateforme VPN")
    login_window.geometry("350x300")
    login_window.configure(bg=BG_COLOR)
    login_window.resizable(True, True)

    container = tk.Frame(login_window, bg=BG_COLOR)
    container.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(container, text="Nom d'utilisateur :", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT).pack(pady=(5, 0))
    username_entry = tk.Entry(container, bg=ENTRY_BG, font=FONT, width=30)
    username_entry.pack(pady=5)

    tk.Label(container, text="Mot de passe :", bg=BG_COLOR, fg=LABEL_COLOR, font=FONT).pack(pady=(10, 0))
    password_entry = tk.Entry(container, show="*", bg=ENTRY_BG, font=FONT, width=30)
    password_entry.pack(pady=5)

    tk.Button(container, text="Se connecter", command=login,
              bg=BTN_COLOR, fg=BTN_TEXT, font=FONT, width=20).pack(pady=(15, 5))

    tk.Button(container, text="Créer un compte", command=open_register_window,
              bg="#d3d3d3", fg="black", font=FONT, width=20).pack(pady=5)

    login_window.mainloop()

# Lance l'application
main_login_window()
