import tkinter as tk
from tkinter import messagebox
import subprocess
import platform
import psutil
import socket
from PIL import ImageGrab
import matplotlib.pyplot as plt
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

# Windows lisans anahtarını almak için komut
def get_windows_key():
    try:
        command = 'wmic path SoftwareLicensingService get OA3xOriginalProductKey'
        product_key = subprocess.check_output(command, shell=True).decode().strip().split('\n')[1]
        return product_key
    except Exception as e:
        return "Lisans anahtarı alınamadı"

# Linux için lisans anahtarını almak
def get_linux_key():
    try:
        command = "sudo dmidecode -s system-uuid"
        product_key = subprocess.check_output(command, shell=True).decode().strip()
        return product_key
    except Exception as e:
        return "Lisans anahtarı alınamadı"

# Sistem bilgilerini almak
def get_system_info():
    system_info = {
        'İS': platform.system(),
        'Sürüm': platform.version(),
        'Mimari': platform.architecture()[0],
        'Makine': platform.machine(),
        'İşlemci': platform.processor(),
        'RAM': f"{psutil.virtual_memory().total // (1024 ** 3)} GB",
        'Disk': f"{psutil.disk_usage('/').total // (1024 ** 3)} GB",
        'IP Adres': socket.gethostbyname(socket.gethostname()),
        'CPU Kullanımı': f"{psutil.cpu_percent()}%",
        'Pil Durumu': get_battery_status()
    }

    # İşletim sistemine göre ekstra bilgiler ekleyelim
    if platform.system() == "Windows":
        system_info['Ürün Anahtarı'] = get_windows_key()
    elif platform.system() == "Linux":
        system_info['Ürün Anahtarı'] = get_linux_key()
    elif platform.system() == "Darwin":  # macOS
        system_info['Ürün Anahtarı'] = "macOS Anahtarı Bilgisi mevcut değil"

    return system_info

# Batarya durumunu almak
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"{battery.percent}% - {'Şarj etme' if battery.power_plugged else 'Şarj Olmuyor'}"
    return "Pil bilgisi mevcut değil"

# Sistem performansını sürekli izlemek
def monitor_system_performance(app):
    while True:
        time.sleep(1)
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        app.update_performance_graph(cpu_usage, ram_usage)

# GUI Uygulaması
class SystemInfoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="lightgray")
        
        # Sabit boyutlu form
        self.window.geometry("780x780")  # Form boyutlarını sabitleyin
        self.window.resizable(False, False)  # Boyutlandırmayı devre dışı bırakın
        
        # Sistem bilgilerini al
        system_info = get_system_info()

        # Başlık etiketi
        label = tk.Label(self.window, text="Sistem Bilgileri", font=("Arial", 16), bg="lightblue")
        label.pack(pady=10, fill='x')

        # Bilgileri ekrana yazdır
        self.info_frame = tk.Frame(self.window, bg="lightgray")
        self.info_frame.pack(padx=10, pady=10, fill='both', expand=True)

        for key, value in system_info.items():
            info_label = tk.Label(self.info_frame, text=f"{key}: {value}", font=("Arial", 12), bg="lightgray")
            info_label.pack(pady=5)

        # Kaydet butonu
        save_button = tk.Button(self.window, text="Bilgileri Kaydet", command=lambda: save_to_file(system_info), font=("Arial", 12), bg="lightgreen")
        save_button.pack(pady=10)

        # Ekran görüntüsü butonu
        capture_button = tk.Button(self.window, text="Ekran Görüntüsü Al", command=capture_screenshot, font=("Arial", 12), bg="lightcoral")
        capture_button.pack(pady=10)

        # Performans Grafiği
        self.figure = plt.Figure(figsize=(5, 2), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.window)
        self.canvas.get_tk_widget().pack(padx=10, pady=10)

        # Gerçek zamanlı performans takibi
        self.monitor_thread = threading.Thread(target=monitor_system_performance, args=(self,), daemon=True)
        self.monitor_thread.start()

        self.window.mainloop()

    # Performans grafiğini güncellemek
    def update_performance_graph(self, cpu_usage, ram_usage):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(['CPU Kullanımı', 'RAM Kullanımı'], [cpu_usage, ram_usage], color=['blue', 'green'])
        ax.set_ylim(0, 100)
        ax.set_title('Sistem Performansı')
        self.canvas.draw()

# Ekran görüntüsü almak
def capture_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    messagebox.showinfo("Ekran Görüntüsü", "Ekran görüntüsü 'screenshot.png' olarak kaydedildi.")

# Sistemi dosyaya kaydetme
def save_to_file(system_info):
    try:
        with open("sistem_bilgi.txt", "w") as file:
            for key, value in system_info.items():
                file.write(f"{key}: {value}\n")
        messagebox.showinfo("Başarılı", "Bilgiler başarıyla kaydedildi.")
    except Exception as e:
        messagebox.showerror("Hata", "Bilgiler kaydedilemedi.")

# Uygulamayı başlat
root = tk.Tk()
app = SystemInfoApp(root, "Çapraz Platform Sistem Bilgileri ve Performans Takibi")
