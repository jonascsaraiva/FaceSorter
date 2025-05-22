# interface/interface.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QCheckBox, QFileDialog, QProgressBar, QTextEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from processador.reconhecimento import treinar_reconhecedor
from processador.detector import reconhecer_e_organizar
from processador.utils import registrar_log

class WorkerTreinamento(QThread):
    progresso = pyqtSignal(int)
    concluido = pyqtSignal(tuple)

    def __init__(self, pasta):
        super().__init__()
        self.pasta = pasta

    def run(self):
        try:
            reconhecedor, nomes = treinar_reconhecedor(self.pasta)
            self.concluido.emit((reconhecedor, nomes))
        except Exception as e:
            registrar_log(f"❌ Erro no treinamento: {e}")
            self.concluido.emit((None, {}))

class WorkerProcessamento(QThread):
    progresso = pyqtSignal(int)
    concluido = pyqtSignal()

    def __init__(self, entrada, saida, reconhecedor, nomes, recortar):
        super().__init__()
        self.entrada = entrada
        self.saida = saida
        self.reconhecedor = reconhecedor
        self.nomes = nomes
        self.recortar = recortar

    def run(self):
        reconhecer_e_organizar(
            self.entrada,
            self.saida,
            self.reconhecedor,
            self.nomes,
            self.recortar,
            self.progresso.emit
        )
        self.concluido.emit()

class InterfaceOrganizador(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizado de fotos por rosto")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("background-color: #6397c6; color: white;")
        self.init_ui()

        self.reconhecedor = None
        self.nomes = []
        self.pasta_entrada = ""
        self.pasta_saida = ""
        self.pasta_treinamento = ""

        self.btn_entrada.clicked.connect(self.selecionar_entrada)
        self.btn_saida.clicked.connect(self.selecionar_saida)
        self.btn_treinamento.clicked.connect(self.selecionar_treinamento)
        self.btn_treinar.clicked.connect(self.acao_treinar)
        self.btn_iniciar.clicked.connect(self.acao_iniciar)

    def estilo_botao(self):
        return (
            "QPushButton {"
            "background-color: rgba(29, 71, 119, 128);"
            " padding: 10px;"
            " border-radius: 15px;"
            "}"
            "QPushButton:hover {"
            " border: 2px solid #1b3c5a;"
            "}"
            "QPushButton:pressed {"
            " background-color: #1a2f45;"
            " border: 2px solid #0f1c2b;"
            "}"
        )

    def estilo_checkbox(self):
        return (
            "QCheckBox::indicator {"
            " width: 18px;"
            " height: 18px;"
            " border: 2px solid #1b3c5a;"
            " border-radius: 3px;"
            " background-color: #2c5d89;"
            "}"
            "QCheckBox::indicator:checked {"
            " image: none;"
            " background-color: #2c5d89;"
            " border: 2px solid #1b3c5a;"
            "}"
        )

    def estilo_progressbar(self):
        return (
            "QProgressBar {"
            " border: 2px solid #1b3c5a;"
            " border-radius: 10px;"
            " background-color: rgba(29, 71, 119, 128);"
            " text-align: center;"
            " height: 20px;"
            " color: white;"
            "}"
            "QProgressBar::chunk {"
            " background-color: #2ecc71;"
            " border-radius: 10px;"
            "}"
        )

    def init_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Organizado de fotos por rosto")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        layout.addSpacing(10)

        lbl_pastas = QLabel("Seleção de pastas:  📁")
        lbl_pastas.setFont(QFont("Arial", 12))
        lbl_pastas.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_pastas)

        self.btn_entrada = QPushButton("Selecionar pasta de Entrada")
        self.btn_saida = QPushButton("Selecionar Pasta de Saída")
        self.btn_treinamento = QPushButton("Selecionar Pasta de Treinamento")

        for btn in [self.btn_entrada, self.btn_saida, self.btn_treinamento]:
            btn.setStyleSheet(self.estilo_botao())
            layout.addWidget(btn)

        self.chk_recorte = QCheckBox("Recortar imagens invés de copiar")
        self.chk_recorte.setStyleSheet(self.estilo_checkbox())
        layout.addWidget(self.chk_recorte, alignment=Qt.AlignCenter)

        layout.addSpacing(15)
        lbl_treinamento = QLabel("Treinamento:  🧠")
        lbl_treinamento.setFont(QFont("Arial", 12))
        lbl_treinamento.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_treinamento)

        self.btn_treinar = QPushButton("Iniciar treinamento")
        self.btn_treinar.setStyleSheet(self.estilo_botao())
        layout.addWidget(self.btn_treinar)

        layout.addSpacing(15)
        lbl_processamento = QLabel("Processamento      🗂️")
        lbl_processamento.setFont(QFont("Arial", 12))
        lbl_processamento.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_processamento)

        hbox_processamento = QHBoxLayout()
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_pausar = QPushButton("Pausar")
        self.btn_reiniciar = QPushButton("Reiniciar")

        for btn in [self.btn_iniciar, self.btn_pausar, self.btn_reiniciar]:
            btn.setStyleSheet(self.estilo_botao())
            hbox_processamento.addWidget(btn)
        layout.addLayout(hbox_processamento)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self.estilo_progressbar())
        self.progress_bar.setValue(0)
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
        self.progress_bar.setValue(0)
        self.status_text.append("🧠 Thread de treinamento iniciada...")
        self.thread_treino = WorkerTreinamento(self.pasta_treinamento)
        self.thread_treino.progresso.connect(self.progress_bar.setValue)
        self.thread_treino.concluido.connect(self.finalizar_treinamento)
        self.thread_treino.start()

    def finalizar_treinamento(self, resultado):
        self.reconhecedor, self.nomes = resultado
        if self.reconhecedor:
            self.status_text.append("✔️ Treinamento concluído com sucesso")
        else:
            self.status_text.append("❌ Erro no treinamento")

    def acao_iniciar(self):
        if not self.pasta_entrada or not self.pasta_saida or self.reconhecedor is None:
            self.status_text.append("⚠️ Verifique as pastas e se o sistema foi treinado.")
            return
        self.progress_bar.setValue(0)
        self.status_text.append("🔍 Thread de processamento iniciada")
        self.thread_proc = WorkerProcessamento(
            self.pasta_entrada,
            self.pasta_saida,
            self.reconhecedor,
            self.nomes,
            self.chk_recorte.isChecked()
        )
        self.thread_proc.progresso.connect(self.progress_bar.setValue)
        self.thread_proc.concluido.connect(lambda: self.status_text.append("✅ Processamento finalizado"))
        self.thread_proc.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = InterfaceOrganizador()
    janela.show()
    sys.exit(app.exec_())