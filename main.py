import cv2
import time
from collections import deque

def create_tracker(tracker_type):
    """Cria a instância do tracker baseado no tipo escolhido."""
    if tracker_type == 'CSRT':
        return cv2.TrackerCSRT_create()
    elif tracker_type == 'KCF':
        return cv2.TrackerKCF_create()
    elif tracker_type == 'MOSSE':
        try:
            return cv2.legacy.TrackerMOSSE_create()
        except AttributeError:
            print("MOSSE não disponível nesta versão do OpenCV, usando KCF como fallback.")
            return cv2.TrackerKCF_create()
    else:
        return cv2.TrackerCSRT_create()

def main():
    # Configurações iniciais
    print("\nQual câmera você deseja usar?")
    print("[0] Webcam padrão do notebook")
    print("[1, 2...] Outra câmera (ex: DroidCam / Iriun via USB)")
    print("[URL] Link de Câmera IP (ex: http://192.168.0.5:8080/video)")
    escolha = input("Digite a opção (pressione Enter para a padrão '0'): ").strip()
    
    if escolha == "":
        video_source = 0
    elif escolha.isdigit():
        video_source = int(escolha)
    else:
        video_source = escolha  # Para URL ou arquivos de vídeo
        
    tracker_type = 'CSRT'
    
    # Inicializa a captura de vídeo
    if isinstance(video_source, int):
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            # No Windows, câmeras USB externas/virtuais às vezes precisam do DirectShow
            cap = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(video_source)
        
    if not cap.isOpened():
        print("Erro ao abrir a câmera ou vídeo.")
        return

    # Lê o primeiro frame
    ret, frame = cap.read()
    if not ret:
        print("Erro ao ler o frame da câmera.")
        return
        
    # Configuração do gravador de vídeo (VideoWriter)
    height, width = frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec para .mp4
    out_video = cv2.VideoWriter('output_rastreamento.mp4', fourcc, 20.0, (width, height))

    # Variáveis de controle
    tracker = None
    initBB = None # Bounding Box inicial
    trajectory = deque(maxlen=64) # Fila para armazenar os últimos pontos da trajetória (rastro)
    
    print("="*50)
    print("SISTEMA DE RASTREAMENTO DE OBJETOS EM TEMPO REAL")
    print("="*50)
    print("Comandos:")
    print(" 's' - Selecionar um novo objeto (ROI) para rastrear")
    print(" 'c' - Mudar para rastreador CSRT (Mais preciso, mais lento)")
    print(" 'k' - Mudar para rastreador KCF (Menos preciso, mais rápido)")
    print(" 'q' - Sair do programa")
    print("="*50)

    # Loop principal
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Variáveis para cálculo de FPS
        start_time = time.time()

        # Se temos uma Bounding Box (objeto foi selecionado)
        if initBB is not None:
            # Atualiza o rastreador
            (success, box) = tracker.update(frame)

            if success:
                # Rastreador encontrou o objeto
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Calcula o centro do objeto para a trajetória
                center_x = x + w // 2
                center_y = y + h // 2
                trajectory.appendleft((center_x, center_y))
            else:
                # Rastreador falhou (ex: objeto ocluído ou saiu da tela)
                cv2.putText(frame, "FALHA NO RASTREAMENTO", (10, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                trajectory.clear() # Limpa a trajetória se perder o objeto
                
        # Desenha a trajetória na tela
        for i in range(1, len(trajectory)):
            if trajectory[i - 1] is None or trajectory[i] is None:
                continue
            # A espessura da linha diminui ao longo do tempo para dar efeito de "rastro"
            thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
            cv2.line(frame, trajectory[i - 1], trajectory[i], (0, 0, 255), thickness)

        # Calcula o FPS
        end_time = time.time()
        fps = 1 / (end_time - start_time + 0.0001)

        # Exibe as informações na tela
        cv2.putText(frame, f"Tracker: {tracker_type}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        info_text = "Aperte 's' para selecionar o objeto" if initBB is None else "Aperte 'q' para sair"
        cv2.putText(frame, info_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Exibe o frame atual
        cv2.imshow("Sistema de Rastreamento (Pressione 's' para selecionar)", frame)
        
        # Salva o frame no arquivo de vídeo de saída
        out_video.write(frame)

        # Captura as teclas pressionadas
        key = cv2.waitKey(1) & 0xFF

        # Se a tecla 's' for pressionada, seleciona a Bounding Box
        if key == ord("s"):
            # cv2.selectROI pausa o vídeo para você desenhar o retângulo
            initBB = cv2.selectROI("Sistema de Rastreamento (Pressione 's' para selecionar)", frame, fromCenter=False, showCrosshair=True)
            
            # Inicializa/reinicializa o rastreador
            tracker = create_tracker(tracker_type)
            tracker.init(frame, initBB)
            trajectory.clear() # Limpa a trajetória antiga
            
        # Troca para CSRT
        elif key == ord("c"):
            tracker_type = 'CSRT'
            if initBB is not None:
                tracker = create_tracker(tracker_type)
                tracker.init(frame, initBB)
                
        # Troca para KCF
        elif key == ord("k"):
            tracker_type = 'KCF'
            if initBB is not None:
                tracker = create_tracker(tracker_type)
                tracker.init(frame, initBB)

        # Se a tecla 'q' for pressionada, sai do loop
        elif key == ord("q"):
            break

    # Libera os recursos
    cap.release()
    out_video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    import numpy as np # Importado aqui pois é usado no desenho da trajetória
    main()
