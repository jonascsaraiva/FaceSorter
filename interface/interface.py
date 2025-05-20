# interface/interface.py
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QCheckBox, QFileDialog, QProgressBar, QTextEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Thread para treinamento
class TreinamentoThread(QThread):
    concluido = pyqtSignal(object, dict)
    erro = pyqtSignal(str)

    def __init__(self, pasta_treinamento):
        super().__init__()
        self.pasta_treinamento = pasta_treinamento

    def run(self):
        try:
            from processador.reconhecimento import treinar_reconhecedor
            from processador.utils import registrar_log
            registrar_log(f"🧠 Thread de treinamento iniciada: {self.pasta_treinamento}")
            recognizer, mapeamento = treinar_reconhecedor(self.pasta_treinamento)
            self.concluido.emit(recognizer, mapeamento)
        except Exception as e:
            self.erro.emit(str(e))

# Thread para processamento
class ProcessamentoThread(QThread):
    progresso = pyqtSignal(int)
    concluido = pyqtSignal()
    erro = pyqtSignal(str)

    def __init__(self, pasta_entrada, pasta_saida, reconhecedor, mapeamento, recortar):
        super().__init__()
        self.pasta_entrada = pasta_entrada
        self.pasta_saida = pasta_saida
        self.reconhecedor = reconhecedor
        self.mapeamento = mapeamento
        self.recortar = recortar

    def run(self):
        try:
            from processador.detector import reconhecer_e_organizar
            from processador.utils import registrar_log
            registrar_log("🔍 Thread de processamento iniciada")
            reconhecer_e_organizar(
                self.pasta_entrada,
                self.pasta_saida,
                self.reconhecedor,
                self.mapeamento,
                self.recortar,
                lambda val: self.progresso.emit(val)
            )
            self.concluido.emit()
        except Exception as e:
            self.erro.emit(str(e))

class InterfaceOrganizador(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de fotos por rosto")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("background-color: #6397c6; color: white;")
        self.reconhecedor = None
        self.nomes = {}
        self.pasta_entrada = ""
        self.pasta_saida = ""
        self.pasta_treinamento = ""
        self.init_ui()

    def estilo_botao(self):
        return (
            "QPushButton { background-color: rgba(29,71,119,128); padding:10px; border-radius:15px;}"
            "QPushButton:hover { border:2px solid #1b3c5a;}"
            "QPushButton:pressed { background-color:#1a2f45; border:2px solid #0f1c2b;}"
        )

    def estilo_checkbox(self):
        return (
            "QCheckBox::indicator { width:18px; height:18px; border:2px solid #1b3c5a; border-radius:3px; background-color:#2c5d89;}"
            "QCheckBox::indicator:checked { image:none; background-color:#2c5d89; border:2px solid #1b3c5a;}"
        )

    def estilo_progressbar(self):
        return (
            "QProgressBar { border:2px solid #1b3c5a; border-radius:10px; background-color:rgba(29,71,119,128); text-align:center; height:20px; color:white;}"
            "QProgressBar::chunk { background-color:#2ecc71; border-radius:10px;}"
        )

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Organizador de fotos por rosto")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Seleção de pastas
        layout.addSpacing(10)
        lbl_pastas = QLabel("Seleção de pastas: 📁")
        lbl_pastas.setFont(QFont("Arial", 12))
        lbl_pastas.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_pastas)

        self.btn_entrada = QPushButton("Selecionar pasta de Entrada")
        self.btn_saida = QPushButton("Selecionar pasta de Saída")
        self.btn_treinamento = QPushButton("Selecionar pasta de Treinamento")
        for btn in [self.btn_entrada, self.btn_saida, self.btn_treinamento]:
            btn.setStyleSheet(self.estilo_botao())
            layout.addWidget(btn)
        self.btn_entrada.clicked.connect(self.selecionar_entrada)
        self.btn_saida.clicked.connect(self.selecionar_saida)
        self.btn_treinamento.clicked.connect(self.selecionar_treinamento)

        # Checkbox recorte
        self.chk_recorte = QCheckBox("Recortar imagens invés de copiar")
        self.chk_recorte.setStyleSheet(self.estilo_checkbox())
        layout.addWidget(self.chk_recorte, alignment=Qt.AlignCenter)

        # Treinamento
        layout.addSpacing(15)
        lbl_trein = QLabel("Treinamento: 🧠")
        lbl_trein.setFont(QFont("Arial", 12))
        lbl_trein.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_trein)

        self.btn_treinar = QPushButton("Iniciar treinamento")
        self.btn_treinar.setStyleSheet(self.estilo_botao())
        self.btn_treinar.clicked.connect(self.acao_treinar)
        layout.addWidget(self.btn_treinar)

        # Processamento
        layout.addSpacing(15)
        lbl_proc = QLabel("Processamento: 🗂️")
        lbl_proc.setFont(QFont("Arial", 12))
        lbl_proc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_proc)

        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_pausar = QPushButton("Pausar")
        self.btn_reiniciar = QPushButton("Reiniciar")
        for btn in [self.btn_iniciar, self.btn_pausar, self.btn_reiniciar]:
            btn.setStyleSheet(self.estilo_botao())
            layout.addWidget(btn)
        self.btn_iniciar.clicked.connect(self.acao_iniciar)

        # Progress bar e log
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self.estilo_progressbar())
        layout.addWidget(self.progress_bar)

        lbl_log = QLabel("Log:")
        lbl_log.setFont(QFont("Arial", 12))
        lbl_log.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_log)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFixedHeight(150)
        layout.addWidget(self.status_text)

        self.setLayout(layout)

    def selecionar_entrada(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de Entrada")
        if pasta:
            self.pasta_entrada = pasta
            self.status_text.append(f"📥 Entrada: {pasta}")

    def selecionar_saida(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de Saída")
        if pasta:
            self.pasta_saida = pasta
            self.status_text.append(f"📤 Saída: {pasta}")

    def selecionar_treinamento(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de Treinamento")
        if pasta:
            self.pasta_treinamento = pasta
            self.status_text.append(f"📚 Treinamento: {pasta}")

    def acao_treinar(self):
        if not self.pasta_treinamento:
            self.status_text.append("⚠️ Selecione a pasta de treinamento primeiro.")
            return
        self.btn_treinar.setEnabled(False)
        self.status_text.append("🧠 Thread de treinamento iniciada...")
        self.thread_treino = TreinamentoThread(self.pasta_treinamento)
        self.thread_treino.concluido.connect(self._on_treino_concluido)
        self.thread_treino.erro.connect(self._on_treino_erro)
        self.thread_treino.start()

    def _on_treino_concluido(self, recognizer, mapeamento):
        self.reconhecedor = recognizer
        self.nomes = mapeamento
        self.status_text.append("✔️ Treinamento concluído com sucesso")
        self.btn_treinar.setEnabled(True)

    def _on_treino_erro(self, mensagem):
        self.status_text.append(f"❌ Erro no treinamento: {mensagem}")
        self.btn_treinar.setEnabled(True)

    def acao_iniciar(self):
        if not self.pasta_entrada or not self.pasta_saida or self.reconhecedor is None:
            self.status_text.append("⚠️ Verifique pastas e treinamento.")
            return
        self.btn_iniciar.setEnabled(False)
        recortar = self.chk_recorte.isChecked()
        self.status_text.append("🔍 Thread de processamento iniciada...")
        self.thread_proc = ProcessamentoThread(
            self.pasta_entrada,
            self.pasta_saida,
            self.reconhecedor,
            self.nomes,
            recortar
        )
        self.thread_proc.progresso.connect(self.progress_bar.setValue)
        self.thread_proc.concluido.connect(self._on_proc_concluido)
        self.thread_proc.erro.connect(self._on_proc_erro)
        self.thread_proc.start()

    def _on_proc_concluido(self):
        self.status_text.append("✅ Processamento concluído.")
        self.btn_iniciar.setEnabled(True)

    def _on_proc_erro(self, mensagem):
        self.status_text.append(f"❌ Erro no processamento: {mensagem}")
        self.btn_iniciar.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InterfaceOrganizador()
    window.show()
    sys.exit(app.exec_())
