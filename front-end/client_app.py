import os
import subprocess
import ssl
import requests

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ModuleNotFoundError:
    print("Le module tkinter est manquant. Cette fonctionnalité nécessite tkinter pour l'interface graphique.")
    exit(1)

API_URL = "http://127.0.0.1:8000/auth"
CONFIG_DIR = "./client-configs"

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
        messagebox.showerror("Erreur", f"Impossible de contacter l'API : {e}")

def open_server_selection():
    selection_window = tk.Tk()
    selection_window.title("Choix du serveur VPN")

    ovpn_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".ovpn")]
    if not ovpn_files:
        messagebox.showerror("Erreur", "Aucun fichier .ovpn trouvé.")
        selection_window.destroy()
        return

    tk.Label(selection_window, text="Sélectionnez un serveur :").pack()

    var = tk.StringVar(value=ovpn_files[0])

    for file in ovpn_files:
        tk.Radiobutton(selection_window, text=file, variable=var, value=file).pack(anchor='w')

    def proceed():
        selected_file = var.get()
        cert_path = filedialog.askopenfilename(title="Sélectionnez le certificat .crt", filetypes=[("Certificat", "*.crt")])
        key_path = filedialog.askopenfilename(title="Sélectionnez la clé privée .key", filetypes=[("Clé privée", "*.key")])

        if not cert_path or not key_path:
            messagebox.showerror("Erreur", "Certificat ou clé non sélectionné.")
            return

        run_openvpn(selected_file, cert_path, key_path)

    tk.Button(selection_window, text="Se connecter", command=proceed).pack(pady=10)
    selection_window.mainloop()

def run_openvpn(ovpn_file, cert_file, key_file):
    full_ovpn_path = os.path.join(CONFIG_DIR, ovpn_file)

    cmd = [
        "sudo", "openvpn",
        "--config", full_ovpn_path,
        "--cert", cert_file,
        "--key", key_file
    ]

    terminal_cmd = ["x-terminal-emulator", "-e"] + cmd

    try:
        subprocess.Popen(terminal_cmd)
        messagebox.showinfo("Info", "Connexion VPN en cours dans un nouveau terminal.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

login_window = tk.Tk()
login_window.title("Connexion à la plateforme VPN")

tk.Label(login_window, text="Nom d'utilisateur :").pack()
username_entry = tk.Entry(login_window)
username_entry.pack()

tk.Label(login_window, text="Mot de passe :").pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

tk.Button(login_window, text="Se connecter", command=login).pack(pady=10)

login_window.mainloop()
