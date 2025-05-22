from interface.interface import InterfaceOrganizador
from PyQt5.QtWidgets import QApplication
import sys

# Integra controle de pausa
from processador.reconhecimento import definir_parar_processamento

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = InterfaceOrganizador()

    janela.btn_pausar.clicked.connect(lambda: definir_parar_processamento(True))
    janela.btn_reiniciar.clicked.connect(lambda: definir_parar_processamento(False))

    janela.show()
    sys.exit(app.exec_())
