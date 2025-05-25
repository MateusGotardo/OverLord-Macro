import pytesseract
from PIL import ImageGrab
import pyautogui
import time
import os

# 1. Caminho do executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 2. Diretório onde estão os arquivos .traineddata
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Regiões da tela (ajuste conforme sua resolução e posição da janela do jogo)
regiao_atributos = (634, 313, 1206, 573)  # esquerda, topo, direita, inferior
botao_reproduzir = (916, 549)  # coordenadas do botão "Reproduzir"

# Condições para parar a macro
condicoes = [
    "Força +10",
    "Crítico +1%",
    "Redução de dano dos cinco",
]

# Tempo de espera entre cliques (em segundos)
tempo_entre_reproducoes = 1.5


def extrair_texto(regiao):
    """Captura a tela na região e retorna o texto reconhecido por OCR."""
    imagem = ImageGrab.grab(bbox=regiao)
    texto = pytesseract.image_to_string(imagem, lang='eng')  # Use 'por' se instalar o idioma
    return texto


def verificar_condicoes(texto, condicoes, combinar_todos=False):
    """Verifica se as condições estão presentes no texto."""
    if combinar_todos:
        return all(cond in texto for cond in condicoes)
    else:
        return any(cond in texto for cond in condicoes)


def clicar_reproduzir():
    """Clica no botão 'Reproduzir'."""
    pyautogui.moveTo(botao_reproduzir)
    pyautogui.click()


print("Iniciando macro OverLord...")
time.sleep(2)

contador = 0

while True:
    texto = extrair_texto(regiao_atributos)
    print(f"[{contador}] Texto extraído:\n{texto}\n")

    if verificar_condicoes(texto, condicoes):
        print("✅ Condição encontrada! Macro pausada.")
        break

    print("🔄 Condição não encontrada. Reproduzindo novamente...")
    clicar_reproduzir()
    time.sleep(tempo_entre_reproducoes)
    contador += 1

print("Macro finalizada.")
