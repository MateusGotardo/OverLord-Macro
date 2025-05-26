import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image
import pytesseract
import pyautogui
import keyboard
import threading
import time
import win32gui
import win32con
import ctypes


# Caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Variáveis Globais
ocr_area = None
button_area = None
running = False


### =========================
### Função para selecionar área na tela
### =========================
def selecionar_area():
    root.withdraw()  # Oculta janela principal temporariamente

    selecao = tk.Tk()
    selecao.attributes("-fullscreen", True)
    selecao.attributes('-alpha', 0.3)
    selecao.configure(bg='black')
    selecao.attributes('-topmost', True)
    selecao.overrideredirect(True)  # Sem borda

    canvas = tk.Canvas(selecao, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = curX = curY = 0

    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x = canvas.canvasx(event.x)
        start_y = canvas.canvasy(event.y)

    def on_mouse_drag(event):
        nonlocal curX, curY
        curX, curY = canvas.canvasx(event.x), canvas.canvasy(event.y)
        canvas.delete("selecion")
        canvas.create_rectangle(start_x, start_y, curX, curY, outline='red', width=2, tags="selecion")
def selecionar_area_dupla():
    root.withdraw()

    def selecionar(label):
        selecao = tk.Tk()
        selecao.attributes("-fullscreen", True)
        selecao.attributes('-alpha', 0.3)
        selecao.configure(bg='black')
        selecao.attributes('-topmost', True)
        selecao.overrideredirect(True)

        canvas = tk.Canvas(selecao, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)

        start_x = start_y = curX = curY = 0

        def on_mouse_down(event):
            nonlocal start_x, start_y
            start_x = canvas.canvasx(event.x)
            start_y = canvas.canvasy(event.y)

        def on_mouse_drag(event):
            nonlocal curX, curY
            curX, curY = canvas.canvasx(event.x), canvas.canvasy(event.y)
            canvas.delete("selecion")
            canvas.create_rectangle(start_x, start_y, curX, curY, outline='red', width=2, tags="selecion")

        def on_mouse_up(event):
            selecao.destroy()
            x1, y1 = min(start_x, curX), min(start_y, curY)
            x2, y2 = max(start_x, curX), max(start_y, curY)
            area = (int(x1), int(y1), int(x2), int(y2))
            print(f"Área {label} selecionada: {area}")
            areas[label] = area

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        selecao.mainloop()

    areas = {}

    messagebox.showinfo("Seleção", "Selecione a área do OCR (onde aparece o texto).")
    selecionar("ocr")

    messagebox.showinfo("Seleção", "Agora selecione a área do botão (onde deve clicar).")
    selecionar("botao")

    global ocr_area, botao_area
    ocr_area = areas.get("ocr")
    botao_area = areas.get("botao")

    root.deiconify()



### =========================
### Função para captura OCR
### =========================
def ocr_monitor():
    global running
    while running:
        if ocr_area is not None:
            img = ImageGrab.grab(ocr_area)
            texto = pytesseract.image_to_string(img, lang='eng')
            texto = texto.strip()
            print(f"OCR detectado: {texto}")

            if any(palavra in texto.lower() for palavra in ["pronto", "ready", "aceitar", "accept"]):
                clicar_na_area()

        time.sleep(0.5)  # Delay para não sobrecarregar


### =========================
### Função para clicar na área
### =========================
def clicar_na_area():
    if ocr_area is not None:
        x = (ocr_area[0] + ocr_area[2]) // 2
        y = (ocr_area[1] + ocr_area[3]) // 2
        pyautogui.click(x, y)
        print(f"🖱️ Clique em: {x}, {y}")


### =========================
### Iniciar / Parar monitoramento
### =========================
def iniciar():
    global running
    if ocr_area is None:
        messagebox.showwarning("Aviso", "Selecione a área antes de iniciar.")
        return

    running = True
    threading.Thread(target=ocr_monitor, daemon=True).start()
    status_label.config(text="Status: Rodando")


def parar():
    global running
    running = False
    status_label.config(text="Status: Parado")


### =========================
### Janela principal
### =========================
root = tk.Tk()
root.title("Auto OCR Clicker")
root.geometry("300x200")
root.attributes('-topmost', True)

# Remove a barra da janela
hwnd = ctypes.windll.user32.GetForegroundWindow()
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TOOLWINDOW)

# Interface
tk.Button(root, text="Selecionar Área OCR e Botão", command=selecionar_area).pack(pady=10)
tk.Button(root, text="Iniciar", command=iniciar, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Parar", command=parar, bg="red", fg="white").pack(pady=5)
status_label = tk.Label(root, text="Status: Parado", fg="blue")
status_label.pack(pady=10)

root.mainloop()
