# Roteiro de Apresentação: Rastreamento de Objetos em Tempo Real

**Autores:** Tarcísio Prates e Francisco Abreu  
**Disciplina:** Visão Computacional  
**Instituição:** CEFET-MG  
**Tempo estimado:** 15 minutos

---

## 1. Introdução

*   **Contexto:** O rastreamento visual de objetos (Visual Object Tracking) é uma das tarefas fundamentais em Visão Computacional, atuando como base para sistemas de monitoramento automatizado, robótica e análise de trajetórias.
*   **Motivação:** Sistemas em tempo real operam sob restrições computacionais severas. Há uma necessidade intrínseca de equilibrar a eficiência de processamento (FPS) com a robustez do rastreamento frente a transformações físicas e ambientais.
*   **Problema a ser resolvido:** Manter a identificação e a localização espacial de um alvo predefinido ao longo de um fluxo de vídeo, contornando desafios como variações de iluminação, rotação do objeto e oclusões, utilizando hardware de propósito geral (CPU).
*   **Objetivos:** Implementar e avaliar comparativamente algoritmos de rastreamento baseados em filtros de correlação (CSRT e KCF) em um ambiente de tempo real, analisando seus compromissos entre custo computacional e estabilidade.

## 2. Breve Referencial Teórico

*   **Rastreamento de Objetos (Object Tracking):** Processo preditivo e corretivo de estimação do estado (posição e escala) de um alvo em quadros consecutivos, a partir de uma inicialização (Region of Interest - ROI).
*   **KCF (Kernelized Correlation Filters):** Algoritmo que projeta amostras de treinamento em um espaço de características utilizando matrizes circulantes. Isso permite que os cálculos sejam realizados no domínio da frequência (via Transformada Rápida de Fourier), reduzindo drasticamente a complexidade assintótica e permitindo altas taxas de processamento.
*   **CSRT (Discriminative Correlation Filter with Channel and Spatial Reliability):** Expande os filtros de correlação tradicionais introduzindo mapas de confiabilidade espacial. O algoritmo identifica quais regiões do objeto e do fundo são mais confiáveis, permitindo adaptação a deformações morfológicas e mitigando a interferência de fundos ruidosos.

## 3. Trabalhos Relacionados

*   Estudos clássicos de rastreamento avaliam filtros de correlação (como MOSSE e o próprio KCF) com foco estrito em sistemas embarcados, onde a capacidade de processamento é o principal gargalo limitante.
*   Trabalhos recentes baseados em *Deep Learning* (como arquiteturas YOLO acopladas a DeepSORT ou ByteTrack) oferecem alta precisão e capacidade de reidentificação. Contudo, demandam aceleradores de hardware (GPUs) para operação em tempo real, contrastando com as abordagens de processamento central (CPU) analisadas neste projeto.

## 4. Método Proposto para Solução

*   **Arquitetura do Software:** Desenvolvimento de uma aplicação desktop parametrizável desenvolvida em Python.
*   **Interface e Interação:** Construção de uma Interface Gráfica de Usuário (GUI) utilizando `CustomTkinter`, permitindo a inicialização manual da Bounding Box (ROI) via interações de mouse sobre o fluxo de vídeo provido pelo OpenCV.
*   **Pipeline de Processamento:** Captura assíncrona do *feed* de vídeo, aplicação do rastreador selecionado (CSRT ou KCF), registro de coordenadas centrais para o mapeamento contínuo de trajetória e cálculo em tempo real da taxa de quadros (FPS).

## 5. Experimentos

O ambiente de testes consistiu na submissão dos algoritmos a vídeos com variações dinâmicas de iluminação, movimentação abrupta e oclusão. Os resultados observados nos registros (pasta `.\experimento`) demonstram os seguintes cenários:

*   **Imagem 1 (CSRT):** Demonstra o rastreador capturando a trajetória do objeto de forma contínua. Observou-se a manutenção do rastreio sob alterações nas condições de luz, orientação e movimentos repentinos. A métrica de FPS, contudo, apresentou-se reduzida devido à complexidade computacional do cálculo de confiabilidade espacial.
*   **Imagem 2 (CSRT):** Ilustra uma limitação do método. Quando o objeto sai do campo de visão (FOV), o algoritmo perde a referência estrutural e falha em reidentificar o alvo em seu retorno à cena.
*   **Imagem 3 (KCF):** Exibe o rastreamento ativo com uma taxa de quadros aproximadamente quatro vezes superior à do algoritmo CSRT, evidenciando sua eficiência computacional.
*   **Imagem 4 (KCF):** Expõe a suscetibilidade do KCF a transformações morfológicas e ambientais. Variações bruscas de iluminação ou orientação resultaram na perda irreversível do alvo.

## 6. Análise de Resultados e Utilização

A experimentação evidencia um compromisso direto (trade-off) entre precisão e custo computacional:

*   **Desempenho do CSRT:** Apresentou alta invariância funcional a alterações de iluminação e rotação, provando-se mecanicamente robusto. A perda do objeto fora do FOV ressalta que trata-se de um rastreador puramente local, desprovido de mecanismos globais de re-detecção.
*   **Desempenho do KCF:** Demonstrou excelência em velocidade de processamento, tornando-se a alternativa viável para hardware restrito. A vulnerabilidade a rotações e variações luminosas ocorre pela ausência de mecanismos espaciais que discriminem características do objeto em relação ao fundo sob mutação.

**Potencial de Aplicação e Utilização:**

*   **Aplicações Industriais e Comerciais:** 
    *   O **KCF** demonstra aplicabilidade direta em ambientes controlados, como esteiras de produção em manufatura para controle de qualidade estruturado, onde a iluminação é constante e a orientação do alvo é previsível.
    *   O **CSRT** aplica-se ao monitoramento em varejo (rastreamento do comportamento e fluxo de clientes) e em veículos autônomos logísticos operando em armazéns com iluminação variada, desde que o hardware suporte a carga de processamento.
*   **Aplicações Militares e de Segurança:** 
    *   A robustez do **CSRT** frente a manobras bruscas confere utilidade em sistemas de mira eletrônica, veículos aéreos não tripulados (VANTs/Drones) para acompanhamento tático e sistemas de câmeras PTZ (Pan-Tilt-Zoom). A falha por saída de quadro exige que tais sistemas operem em conjunto com detectores holísticos ativados sob demanda (como YOLO ou detecção termal) para recuperar o alvo perdido.

## 7. Conclusão

*   A seleção do algoritmo de rastreamento deve ser estritamente pautada nas especificações de hardware e nas condições operacionais do domínio de aplicação.
*   O rastreador **CSRT** é a recomendação técnica quando a estabilidade e a resistência a distorções visuais precedem a necessidade de altas taxas de *framerate*.
*   O rastreador **KCF** atende sistemas de restrição computacional e ambientes de variáveis lumínicas e cinemáticas controladas.
*   **Trabalhos Futuros:** A mitigação da perda de alvos que deixam o campo de visão pode ser endereçada acoplando o atual sistema a um detector de objetos leve. O detector atuaria como mecanismo de salvaguarda (fallback), reinicializando as coordenadas do rastreador de forma autônoma sempre que o coeficiente de confiança decair abaixo de um limiar predefinido.
