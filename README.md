# Rastreamento de Objetos em Tempo Real

**Visão Computacional**  
**CEFET-MG**

**Autores:** Tarcísio Prates e Francisco Abreu

---

## 📌 Sobre o Projeto

Este projeto consiste em uma aplicação de Visão Computacional focada no **rastreamento de objetos em tempo real** através de fluxos de vídeo. A ferramenta permite conectar-se a diferentes fontes de vídeo (como webcams convencionais ou câmeras IP via rede) e escolher, com o mouse, um objeto na tela para ser continuamente acompanhado.

O arquivo principal da aplicação é o `app.py`, que encapsula toda a lógica de rastreamento com o **OpenCV** e apresenta uma interface gráfica moderna e amigável desenvolvida em **CustomTkinter**.

## 🚀 Arquitetura e Tecnologias

- **Python 3**: Linguagem base do projeto.
- **OpenCV (`cv2`)**: Biblioteca central para processamento de imagens e visão computacional.
- **CustomTkinter**: Framework para criação de uma Interface Gráfica de Usuário (GUI) moderna e com suporte a *Dark Mode*.
- **Pillow (PIL)**: Utilizado para a conversão de frames do OpenCV (formato BGR) para um formato renderizável no CustomTkinter (RGB/ImageTk).

## 🧠 Algoritmos de Visão Computacional

A aplicação suporta dois algoritmos principais de *Object Tracking* fornecidos pelo módulo de contribuição do OpenCV. A alternância entre eles pode ser feita em tempo real pela interface:

### 1. CSRT (Discriminative Correlation Filter with Channel and Spatial Reliability)
* **Como funciona:** Ele aprimora os filtros de correlação discriminativa tradicionais utilizando "confiança espacial", ou seja, ele consegue entender as partes do objeto que são confiáveis para o rastreamento e ignora fundos complexos. Ele lida muito bem com mudanças de escala e rotação do objeto.
* **Vantagem:** Muito mais preciso, lida melhor com objetos rotacionando ou sofrendo oclusão parcial.
* **Desvantagem:** É mais pesado computacionalmente (menor FPS).

### 2. KCF (Kernelized Correlation Filters)
* **Como funciona:** Baseado na ideia de que várias amostras em torno de um objeto têm grandes sobreposições matemáticas. O algoritmo usa propriedades matemáticas de matrizes circulantes para processar essas sobreposições de forma extremamente rápida.
* **Vantagem:** Muito rápido, oferecendo um FPS (Frames Por Segundo) mais alto.
* **Desvantagem:** Menor precisão comparado ao CSRT. Pode perder o objeto mais facilmente se ele mudar de tamanho, girar muito ou for obstruído.

## 🖥️ A Interface de Usuário (UI)

O `app.py` constrói uma interface dividida em dois painéis principais:

- **Painel Esquerdo (Visor de Vídeo):** Exibe o feed de vídeo em tempo real. O usuário pode usar o mouse para desenhar uma Caixa Delimitadora (*Bounding Box* / ROI) ao redor de qualquer objeto na tela. Quando o objeto está sendo rastreado, uma mira (crosshair) e as linhas centrais são renderizadas sobre ele. O visor também exibe a taxa de quadros por segundo (FPS).
- **Painel Direito (Controles):** Permite inserir a Fonte de Vídeo (índice local `0`, `1` ou URL para câmeras IP), botões para "Iniciar/Parar Câmera", um seletor *dropdown* de Algoritmo de Rastreio (CSRT/KCF) e botões para "Selecionar Objeto" e "Limpar Rastreio". Um indicativo de *Status* na parte inferior informa a situação do rastreador (Aguardando, Rastrendo, Perdido).

## ⚙️ Como Executar

1. **Instale as dependências:**
Certifique-se de estar em seu ambiente virtual e execute o comando:
```bash
pip install -r requirements.txt
```

2. **Inicie a aplicação principal:**
```bash
python app.py
```

*(O projeto também inclui um arquivo `main.py` que executa uma versão do rastreador puramente baseada em janelas nativas do OpenCV, operada via linha de comando e atalhos de teclado).*
