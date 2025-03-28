import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
import socket

class SimpleSpeedTestApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Speed Test")
        self.window.geometry("400x500")
        self.window.configure(bg='#1B1E2B')
        
        # Ana frame
        main_frame = tk.Frame(self.window, bg='#1B1E2B')
        main_frame.pack(expand=True)
        
        # Test butonu
        self.test_button = tk.Button(
            main_frame,
            text="GO",
            font=('Helvetica', 14),
            bg='#00FF9F',
            fg='#1B1E2B',
            width=15,
            height=2,
            relief='flat',
            command=self.start_test
        )
        self.test_button.pack(pady=30)
        
        # Sonuç kartları için frame
        self.results_frame = tk.Frame(main_frame, bg='#1B1E2B')
        self.results_frame.pack(pady=20)
        
        # Download kartı
        self.create_result_card("DOWNLOAD", "0.00", "Mbps", 0)
        
        # Upload kartı
        self.create_result_card("UPLOAD", "0.00", "Mbps", 1)
        
        # Ping kartı
        self.create_result_card("PING", "0", "ms", 2)
        
        # Durum mesajı
        self.status_label = tk.Label(
            main_frame,
            text="Test başlatmak için butona tıklayın",
            font=('Helvetica', 10),
            bg='#1B1E2B',
            fg='#888888'
        )
        self.status_label.pack(pady=20)
        
        self.is_testing = False

    def create_result_card(self, title, initial_value, unit, row):
        card = tk.Frame(
            self.results_frame,
            bg='#252A3B',
            width=300,
            height=80
        )
        card.pack(pady=5)
        card.pack_propagate(False)
        
        # Başlık
        title_label = tk.Label(
            card,
            text=title,
            font=('Helvetica', 12),
            bg='#252A3B',
            fg='#888888'
        )
        title_label.pack(pady=(10, 0))
        
        # Değer ve birim aynı satırda
        value_frame = tk.Frame(card, bg='#252A3B')
        value_frame.pack(expand=True)
        
        value_label = tk.Label(
            value_frame,
            text=initial_value,
            font=('Helvetica', 24, 'bold'),
            bg='#252A3B',
            fg='white'
        )
        value_label.pack(side=tk.LEFT)
        
        unit_label = tk.Label(
            value_frame,
            text=unit,
            font=('Helvetica', 12),
            bg='#252A3B',
            fg='#888888'
        )
        unit_label.pack(side=tk.LEFT, padx=(5, 0), pady=(8, 0))
        
        setattr(self, f"{title.lower()}_value", value_label)
        setattr(self, f"{title.lower()}_card", card)

    def animate_completion(self, frame):
        def interpolate_color(start_rgb, end_rgb, steps, step):
            r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * (step / steps)
            g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * (step / steps)
            b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * (step / steps)
            return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

        start_color = (37, 42, 59)    # #252A3B
        end_color = (0, 255, 159)     # #00FF9F
        steps = 20
        duration = 50  # Her adım için ms

        def animate_step(step):
            if step <= steps:
                color = interpolate_color(start_color, end_color, steps, step)
                frame.configure(bg=color)
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Label) or isinstance(widget, tk.Frame):
                        widget.configure(bg=color)
                        if isinstance(widget, tk.Frame):
                            for subwidget in widget.winfo_children():
                                if isinstance(subwidget, tk.Label):
                                    subwidget.configure(bg=color)
                self.window.after(duration, lambda: animate_step(step + 1))

        animate_step(0)

    def measure_speed(self):
        try:
            self.status_label.config(text="Ping ölçülüyor...")
            
            # Ping ölçümü
            ping_values = []
            test_host = "8.8.8.8"
            
            for _ in range(4):
                try:
                    start_time = time.time()
                    socket.create_connection((test_host, 53), timeout=1)
                    ping_time = (time.time() - start_time) * 1000
                    if ping_time < 1000:
                        ping_values.append(ping_time)
                except:
                    continue
            
            if ping_values:
                average_ping = sum(ping_values) / len(ping_values)
                self.ping_value.config(text=f"{average_ping:.0f}")
                self.animate_completion(self.ping_card)
            
            # Download hızı ölçümü
            self.status_label.config(text="Download hızı ölçülüyor...")
            
            download_urls = [
                "http://speedtest.ftp.otenet.gr/files/test100Mb.db",
                "http://speedtest.tele2.net/100MB.zip",
                "http://proof.ovh.net/files/100Mb.dat"
            ]
            
            max_download_speed = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            for url in download_urls:
                try:
                    downloaded = 0
                    speeds = []
                    start_time = time.time()
                    
                    response = requests.get(url, stream=True, timeout=15)
                    total_size = int(response.headers.get('content-length', 0))
                    
                    if total_size == 0:
                        continue
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            downloaded += len(chunk)
                            elapsed = time.time() - start_time
                            
                            if elapsed > 0:
                                current_speed = (downloaded * 8) / (1000000 * elapsed)
                                speeds.append(current_speed)
                                
                                recent_speed = sum(speeds[-3:]) / len(speeds[-3:]) if len(speeds) >= 3 else current_speed
                                self.download_value.config(text=f"{recent_speed:.2f}")
                                
                                if downloaded >= 5 * 1024 * 1024:
                                    final_speed = sum(speeds[-3:]) / len(speeds[-3:])
                                    if final_speed > max_download_speed:
                                        max_download_speed = final_speed
                                    break
                    
                    if max_download_speed > 0:
                        self.download_value.config(text=f"{max_download_speed:.2f}")
                        self.animate_completion(self.download_card)
                        break
                        
                except Exception as e:
                    print(f"Download test error for {url}: {e}")
                    continue
            
            # Upload hızı ölçümü
            self.status_label.config(text="Upload hızı ölçülüyor...")
            
            try:
                # Daha büyük veri boyutu ve çoklu test
                upload_sizes = [2*1024*1024, 4*1024*1024, 8*1024*1024]  # 2MB, 4MB, 8MB
                max_upload_speed = 0
                upload_servers = [
                    "https://httpbin.org/post",
                    "https://postman-echo.com/post",
                    "https://api.imgur.com/3/upload"
                ]

                for size in upload_sizes:
                    data = b"0" * size
                    speeds = []

                    for server in upload_servers:
                        try:
                            start_time = time.time()
                            chunk_size = 512 * 1024  # 512KB chunks
                            sent = 0
                            
                            # Veriyi parçalar halinde gönder
                            for i in range(0, len(data), chunk_size):
                                chunk = data[i:i + chunk_size]
                                response = requests.post(
                                    server, 
                                    data=chunk,
                                    headers={'Content-Type': 'application/octet-stream'},
                                    timeout=10
                                )
                                
                                sent += len(chunk)
                                elapsed = time.time() - start_time
                                
                                if elapsed > 0:
                                    current_speed = (sent * 8) / (1000000 * elapsed)
                                    speeds.append(current_speed)
                                    
                                    # Son 3 ölçümün ortalamasını al
                                    recent_speed = sum(speeds[-3:]) / len(speeds[-3:]) if len(speeds) >= 3 else current_speed
                                    self.upload_value.config(text=f"{recent_speed:.2f}")
                                    
                            if speeds:
                                avg_speed = sum(speeds) / len(speeds)
                                max_upload_speed = max(max_upload_speed, avg_speed)
                                
                            # Başarılı bir test yaptıysak ve hız makul ise döngüyü kır
                            if max_upload_speed > 0:
                                break
                                
                        except Exception as e:
                            print(f"Upload test error for {server}: {e}")
                            continue
                    
                    if max_upload_speed > 0:
                        break

                if max_upload_speed > 0:
                    self.upload_value.config(text=f"{max_upload_speed:.2f}")
                    self.animate_completion(self.upload_card)
                else:
                    self.upload_value.config(text="--")

            except Exception as e:
                print(f"Upload test error: {e}")
                self.upload_value.config(text="--")
            
            self.status_label.config(text="Test tamamlandı!")
            
        except Exception as e:
            self.status_label.config(text="Bir hata oluştu!")
            print(f"Hata: {e}")

    def start_test(self):
        if not self.is_testing:
            self.is_testing = True
            self.test_button.config(state='disabled', text="TESTING...")
            self.download_value.config(text="0.00")
            self.upload_value.config(text="0.00")
            self.ping_value.config(text="0")
            
            # Test öncesi tüm kartları orijinal renge döndür
            for card in [self.download_card, self.upload_card, self.ping_card]:
                card.configure(bg='#252A3B')
                for widget in card.winfo_children():
                    if isinstance(widget, tk.Label) or isinstance(widget, tk.Frame):
                        widget.configure(bg='#252A3B')
                        if isinstance(widget, tk.Frame):
                            for subwidget in widget.winfo_children():
                                if isinstance(subwidget, tk.Label):
                                    subwidget.configure(bg='#252A3B')
            
            threading.Thread(target=self.run_test, daemon=True).start()

    def run_test(self):
        try:
            self.measure_speed()
        finally:
            self.is_testing = False
            self.test_button.config(state='normal', text="GO")

if __name__ == "__main__":
    app = SimpleSpeedTestApp()
    app.window.mainloop()
