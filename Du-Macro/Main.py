# ================== IMPORTS ==================

import sys
import pytesseract
import pyautogui
import time
import os
import threading
from collections import Counter

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QListWidget, QLineEdit, QMessageBox, QSpinBox, QCheckBox, QDialog
)
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QPainter, QColor, QPen
from PIL import ImageGrab, ImageOps, Image


# ================== CONFIGURAÇÕES ==================

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"


# ================== CLASSE PRINCIPAL ==================

class OverLordApp(QWidget):
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro OverLord - PyQt5")
        self.setGeometry(100, 100, 600, 500)

        # Variáveis principais
        self.tempo_entre_reproducoes = 1.5
        self.coordenadas_regiao = None
        self.condicoes_lista = []
        self.botao_reproduzir = None
        self.botao_manter_status = None
        self.botao_adicionar_status = None
        self.thread_macro = None
        self.stop_macro = False

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # ---- Seleção de Região OCR ----
        self.btn_selecionar = QPushButton("Selecionar região da tela (OCR)")
        self.btn_selecionar.clicked.connect(self.selecionar_regiao)
        main_layout.addWidget(self.btn_selecionar)

        # ---- Adicionar Condições ----
        cond_layout = QHBoxLayout()
        self.input_condicao = QLineEdit()
        self.input_condicao.setPlaceholderText("Digite uma condição (ex: Força +10)")

        self.spin_qtd = QSpinBox()
        self.spin_qtd.setMinimum(1)
        self.spin_qtd.setMaximum(10)
        self.spin_qtd.setValue(1)

        self.btn_add_condicao = QPushButton("Adicionar")
        self.btn_add_condicao.clicked.connect(self.adicionar_condicao)

        cond_layout.addWidget(self.input_condicao)
        cond_layout.addWidget(self.spin_qtd)
        cond_layout.addWidget(self.btn_add_condicao)
        main_layout.addLayout(cond_layout)

        # ---- Lista de Condições ----
        self.lista_condicoes = QListWidget()
        self.lista_condicoes.setFixedHeight(150)
        self.lista_condicoes.itemDoubleClicked.connect(self.remover_condicao)
        main_layout.addWidget(self.lista_condicoes)

        # ---- Seleção de Botões na Tela ----
        btn_layout = QHBoxLayout()

        self.btn_reproduzir = QPushButton("Selecionar botão REPRODUZIR")
        self.btn_reproduzir.clicked.connect(lambda: self.selecionar_botao("reproduzir"))

        self.btn_manter = QPushButton("Selecionar botão MANTER STATUS")
        self.btn_manter.clicked.connect(lambda: self.selecionar_botao("manter"))

        self.btn_adicionar = QPushButton("Selecionar botão ADICIONAR STATUS")
        self.btn_adicionar.clicked.connect(lambda: self.selecionar_botao("adicionar"))

        btn_layout.addWidget(self.btn_reproduzir)
        btn_layout.addWidget(self.btn_manter)
        btn_layout.addWidget(self.btn_adicionar)
        main_layout.addLayout(btn_layout)

        # ---- Preview Checkbox ----
        self.preview_checkbox = QCheckBox("Modo Preview (executa OCR e para)")
        main_layout.addWidget(self.preview_checkbox)

        # ---- Botões de Controle ----
        control_layout = QHBoxLayout()

        self.btn_start = QPushButton("▶️ Iniciar Macro")
        self.btn_start.clicked.connect(self.iniciar_macro)

        self.btn_stop = QPushButton("⛔ Parar Macro")
        self.btn_stop.clicked.connect(self.parar_macro)
        self.btn_stop.setEnabled(False)

        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)

        main_layout.addLayout(control_layout)

        # ---- Status ----
        self.status = QLabel("")
        main_layout.addWidget(self.status)

        self.setLayout(main_layout)

    # ================== Funções de Interface ==================

    def adicionar_condicao(self):
        texto = self.input_condicao.text().strip()
        quantidade = self.spin_qtd.value()
        if texto:
            condicao_formatada = f"{quantidade}x {texto}"
            self.condicoes_lista.append((quantidade, texto))
            self.lista_condicoes.addItem(condicao_formatada)
            self.input_condicao.clear()
        else:
            QMessageBox.warning(self, "Erro", "Digite uma condição válida.")

    def remover_condicao(self, item):
        index = self.lista_condicoes.row(item)
        self.lista_condicoes.takeItem(index)
        if index < len(self.condicoes_lista):
            self.condicoes_lista.pop(index)

    def selecionar_regiao(self):
        self.hide()
        time.sleep(0.5)
        selector = RegionSelector()
        selector.exec_()
        self.coordenadas_regiao = selector.get_coordinates()
        self.show()

        if self.coordenadas_regiao:
            self.status.setText(f"✅ Região OCR: {self.coordenadas_regiao}")
        else:
            self.status.setText("⚠️ Região não selecionada")

    def selecionar_botao(self, tipo):
        self.hide()
        time.sleep(0.5)
        selector = RegionSelector(selecao_ponto=True)
        selector.exec_()
        coords = selector.get_coordinates()

        if coords:
            x = (coords[0] + coords[2]) // 2
            y = (coords[1] + coords[3]) // 2

            if tipo == "reproduzir":
                self.botao_reproduzir = (x, y)
                self.status.setText(f"🟢 Botão REPRODUZIR: {self.botao_reproduzir}")
            elif tipo == "manter":
                self.botao_manter_status = (x, y)
                self.status.setText(f"🟢 Botão MANTER STATUS: {self.botao_manter_status}")
            elif tipo == "adicionar":
                self.botao_adicionar_status = (x, y)
                self.status.setText(f"🟢 Botão ADICIONAR STATUS: {self.botao_adicionar_status}")
        else:
            self.status.setText("⚠️ Botão não selecionado")

        self.show()

    # ================== Funções do Macro ==================

    def iniciar_macro(self):
        if not self.coordenadas_regiao:
            QMessageBox.warning(self, "Erro", "Selecione a região OCR antes de iniciar.")
            return

        if not self.condicoes_lista:
            QMessageBox.warning(self, "Erro", "Adicione pelo menos uma condição.")
            return

        if not self.botao_reproduzir:
            QMessageBox.warning(self, "Erro", "Selecione o botão REPRODUZIR.")
            return

        self.stop_macro = False
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status.setText("🟡 Macro rodando...")

        self.thread_macro = threading.Thread(target=self.executar_macro)
        self.thread_macro.start()

    def parar_macro(self):
        self.stop_macro = True
        self.status.setText("⛔ Macro parado.")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def executar_macro(self):
        contador = 0
        preview = self.preview_checkbox.isChecked()

        while not self.stop_macro:
            imagem = ImageGrab.grab(bbox=self.coordenadas_regiao)
            imagem = self.preprocessar_imagem(imagem)

            texto = pytesseract.image_to_string(imagem, lang='eng').strip()
            print(f"[{contador}] Texto OCR:\n{texto}\n")

            ocorrencias = Counter()

            for _, palavra in self.condicoes_lista:
                ocorrencias[palavra] = texto.count(palavra)

            encontrou = True
            for qtd, palavra in self.condicoes_lista:
                if ocorrencias[palavra] < qtd:
                    encontrou = False
                    break

            if encontrou:
                self.status.setText("✅ Condição encontrada! Macro parado.")
                print("✅ Condição encontrada! Parando macro.")
                break

            if preview:
                self.status.setText("🔍 Preview executado. Macro parado.")
                print("🔍 Preview ativado. Parando após OCR.")
                break

            pyautogui.moveTo(self.botao_reproduzir)
            pyautogui.click()
            time.sleep(self.tempo_entre_reproducoes)
            contador += 1

        self.parar_macro()

    def preprocessar_imagem(self, imagem):
        imagem = imagem.convert("L")  # Grayscale
        imagem = ImageOps.autocontrast(imagem)
        imagem = imagem.point(lambda x: 0 if x < 128 else 255, '1')  # Binarização
        return imagem


# ================== Classe para Seleção de Região ou Botões ==================

class RegionSelector(QDialog):
    def __init__(self, selecao_ponto=False):
        super().__init__()
        self.setWindowTitle("Selecionar Região")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.3)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(self.screen_geometry)

        self.start_pos = None
        self.end_pos = None
        self.selection_rect = QRect()
        self.selecao_ponto = selecao_ponto

        self.show()

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.selection_rect = QRect(self.start_pos, self.start_pos)
        self.update()

    def mouseMoveEvent(self, event):
        self.end_pos = event.pos()
        self.selection_rect = QRect(self.start_pos, self.end_pos).normalized()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        self.accept()

    def paintEvent(self, event):
        if not self.selection_rect.isNull():
            painter = QPainter(self)
            painter.setPen(QPen(QColor(0, 255, 0), 2, Qt.SolidLine))
            painter.drawRect(self.selection_rect)

    def get_coordinates(self):
        if self.selection_rect.isNull():
            return None
        x1 = self.selection_rect.left()
        y1 = self.selection_rect.top()
        x2 = self.selection_rect.right()
        y2 = self.selection_rect.bottom()
        return (x1, y1, x2, y2)


# ================== MAIN ==================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = OverLordApp()
    janela.show()
    sys.exit(app.exec_())
