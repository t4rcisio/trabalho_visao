import cv2
import time
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
from collections import deque

class RastreamentoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Visão Computacional - Rastreamento de Objetos")
        self.geometry("1000x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variáveis de Estado
        self.cap = None
        self.tracker = None
        self.tracker_type = "CSRT"
        self.initBB = None
        self.trajectory = deque(maxlen=64)
        
        self.is_running = False
        self.selecting_roi = False
        self.paused_frame = None
        self.roi_start = (0, 0)
        self.roi_end = (0, 0)

        # Construção da Interface
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Painel Esquerdo (Vídeo)
        self.video_frame = ctk.CTkFrame(self, corner_radius=10)
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both")
        
        # Eventos de Mouse no vídeo para seleção de ROI
        self.video_label.bind("<ButtonPress-1>", self.on_mouse_down)
        self.video_label.bind("<B1-Motion>", self.on_mouse_drag)
        self.video_label.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Painel Direito (Controles)
        self.control_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.control_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ns")
        self.control_frame.grid_propagate(False)

        # Elementos de Controle
        ctk.CTkLabel(self.control_frame, text="Configurações", font=("Arial", 20, "bold")).pack(pady=(20, 10))

        ctk.CTkLabel(self.control_frame, text="Fonte de Vídeo (IP ou Índice):").pack(anchor="w", padx=20, pady=(10, 0))
        self.cam_entry = ctk.CTkEntry(self.control_frame, placeholder_text="Ex: 0, 1 ou http://...")
        self.cam_entry.insert(0, "0")
        self.cam_entry.pack(fill="x", padx=20, pady=(5, 15))

        self.btn_start = ctk.CTkButton(self.control_frame, text="Iniciar Câmera", command=self.toggle_camera)
        self.btn_start.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.control_frame, text="Algoritmo de Rastreio:").pack(anchor="w", padx=20, pady=(20, 0))
        self.tracker_menu = ctk.CTkSegmentedButton(self.control_frame, values=["CSRT", "KCF"], command=self.change_tracker)
        self.tracker_menu.set("CSRT")
        self.tracker_menu.pack(fill="x", padx=20, pady=(5, 15))

        self.btn_select = ctk.CTkButton(self.control_frame, text="Selecionar Objeto", fg_color="#2b8a3e", hover_color="#237032", command=self.start_selection, state="disabled")
        self.btn_select.pack(fill="x", padx=20, pady=20)
        
        self.btn_clear = ctk.CTkButton(self.control_frame, text="Limpar Rastreio", fg_color="#c92a2a", hover_color="#a61e1e", command=self.clear_tracking)
        self.btn_clear.pack(fill="x", padx=20, pady=5)

        # Créditos (Rodapé)
        creditos = "Visão Computacional\nCEFET-MG\n\nTarcísio Prates e Francisco Abreu"
        self.credits_label = ctk.CTkLabel(self.control_frame, text=creditos, font=("Arial", 12), text_color="gray")
        self.credits_label.pack(side="bottom", pady=15)

        # Status
        self.status_label = ctk.CTkLabel(self.control_frame, text="Status: Aguardando...", text_color="gray")
        self.status_label.pack(side="bottom", pady=5)

    def create_tracker(self, t_type):
        if t_type == 'CSRT':
            return cv2.TrackerCSRT_create()
        elif t_type == 'KCF':
            return cv2.TrackerKCF_create()
        return cv2.TrackerCSRT_create()

    def change_tracker(self, choice):
        self.tracker_type = choice
        if self.initBB is not None and self.paused_frame is not None:
            self.tracker = self.create_tracker(self.tracker_type)
            self.tracker.init(self.paused_frame, self.initBB)

    def toggle_camera(self):
        if self.is_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        source = self.cam_entry.get().strip()
        if source.isdigit():
            source = int(source)
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(source)

        if self.cap.isOpened():
            self.is_running = True
            self.btn_start.configure(text="Parar Câmera", fg_color="#c92a2a", hover_color="#a61e1e")
            self.btn_select.configure(state="normal")
            self.status_label.configure(text="Câmera Conectada", text_color="#2b8a3e")
            self.update_video()
        else:
            self.status_label.configure(text="Erro ao abrir câmera!", text_color="#c92a2a")

    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.video_label.configure(image=None)
        self.btn_start.configure(text="Iniciar Câmera", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
        self.btn_select.configure(state="disabled")
        self.status_label.configure(text="Câmera Parada", text_color="gray")
        self.clear_tracking()

    def start_selection(self):
        if not self.is_running: return
        self.selecting_roi = True
        self.status_label.configure(text="Desenhe a caixa no vídeo!", text_color="#e67700")

    def clear_tracking(self):
        self.initBB = None
        self.tracker = None
        self.trajectory.clear()
        self.selecting_roi = False
        self.status_label.configure(text="Rastreio Limpo", text_color="gray")

    def on_mouse_down(self, event):
        if self.selecting_roi:
            self.roi_start = (event.x, event.y)
            self.roi_end = (event.x, event.y)

    def on_mouse_drag(self, event):
        if self.selecting_roi:
            self.roi_end = (event.x, event.y)
            self.draw_roi_preview()

    def on_mouse_up(self, event):
        if self.selecting_roi:
            self.roi_end = (event.x, event.y)
            self.selecting_roi = False
            
            x1, y1 = self.roi_start
            x2, y2 = self.roi_end
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            if w > 10 and h > 10 and self.paused_frame is not None:
                self.initBB = (x, y, w, h)
                self.tracker = self.create_tracker(self.tracker_type)
                self.tracker.init(self.paused_frame, self.initBB)
                self.trajectory.clear()
                self.status_label.configure(text=f"Rastreando ({self.tracker_type})", text_color="#2b8a3e")
            else:
                self.status_label.configure(text="Caixa muito pequena!", text_color="#c92a2a")

    def draw_roi_preview(self):
        if self.paused_frame is not None:
            frame_copy = self.paused_frame.copy()
            cv2.rectangle(frame_copy, self.roi_start, self.roi_end, (255, 0, 0), 2)
            self.display_frame(frame_copy)

    def display_frame(self, frame):
        # Converte BGR para RGB para o Tkinter
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Converte para PIL Image
        pil_image = Image.fromarray(rgb_image)
        
        # Cria a imagem compatível com CustomTkinter mantendo o tamanho redimensionado
        ctk_image = ctk.CTkImage(light_image=pil_image, size=(800, 600))
        
        self.video_label.configure(image=ctk_image)

    def update_video(self):
        if not self.is_running:
            return

        if self.selecting_roi:
            # Pausa o vídeo durante a seleção, mas mantém a tela chamando o after
            self.after(30, self.update_video)
            return

        start_time = time.time()
        ret, frame = self.cap.read()

        if ret:
            # Redimensiona para caber na label (opcional, aqui mantemos tamanho fixo ou escalável)
            frame = cv2.resize(frame, (800, 600))
            self.paused_frame = frame.copy() # Guarda o frame limpo para o rastreador
            
            if self.initBB is not None and self.tracker is not None:
                success, box = self.tracker.update(frame)
                
                if success:
                    x, y, w, h = [int(v) for v in box]
                    
                    center_x = x + w // 2
                    center_y = y + h // 2
                    self.trajectory.appendleft((center_x, center_y))
                    
                    # Desenhar Mira (Crosshair)
                    mira_size = 20
                    cv2.circle(frame, (center_x, center_y), mira_size, (0, 255, 0), 2)
                    cv2.circle(frame, (center_x, center_y), 3, (0, 0, 255), -1) # Ponto vermelho no centro
                    cv2.line(frame, (center_x - mira_size - 10, center_y), (center_x + mira_size + 10, center_y), (0, 255, 0), 2)
                    cv2.line(frame, (center_x, center_y - mira_size - 10), (center_x, center_y + mira_size + 10), (0, 255, 0), 2)
                    
                    self.status_label.configure(text=f"Rastreando ({self.tracker_type})", text_color="#2b8a3e")
                else:
                    self.trajectory.clear()
                    cv2.putText(frame, "PERDIDO", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.status_label.configure(text="Objeto Perdido!", text_color="#c92a2a")

            # Desenha a trajetória na tela
            for i in range(1, len(self.trajectory)):
                if self.trajectory[i - 1] is None or self.trajectory[i] is None:
                    continue
                # A espessura da linha diminui ao longo do tempo para dar efeito de "rastro"
                thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
                cv2.line(frame, self.trajectory[i - 1], self.trajectory[i], (0, 0, 255), thickness)

            # Calcula e exibe FPS
            fps = int(1 / (time.time() - start_time + 0.0001))
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            self.display_frame(frame)

        # Agenda a próxima atualização
        self.after(15, self.update_video)

    def on_closing(self):
        self.stop_camera()
        self.destroy()

if __name__ == "__main__":
    app = RastreamentoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
