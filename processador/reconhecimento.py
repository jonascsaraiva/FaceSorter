import os
import cv2
import numpy as np
from PIL import Image
from processador.utils import registrar_log

parar_processamento = False


def definir_parar_processamento(valor):
    global parar_processamento
    parar_processamento = valor
    if valor:
        registrar_log("⏸️ Pausando processamento...")
    else:
        registrar_log("▶️ Retomando processamento...")


def treinar_reconhecedor(pasta_treinamento):
    if not os.path.exists(pasta_treinamento):
        raise Exception(f"Pasta de treinamento não encontrada: {pasta_treinamento}")

    faces = []
    labels = []
    nomes = {}
    id_atual = 0

    registrar_log(f"🧠 Iniciando treinamento com LBPH em: {pasta_treinamento}")

    for pessoa in os.listdir(pasta_treinamento):
        caminho_pessoa = os.path.join(pasta_treinamento, pessoa)
        if not os.path.isdir(caminho_pessoa):
            continue

        for arquivo in os.listdir(caminho_pessoa):
            if parar_processamento:
                registrar_log("⏹️ Treinamento interrompido")
                return None, {}

            caminho_arquivo = os.path.join(caminho_pessoa, arquivo)
            if not arquivo.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                registrar_log(f"⏭️ Ignorando não-imagem: {arquivo}")
                continue

            try:
                imagem = Image.open(caminho_arquivo).convert("L")
                imagem_np = np.array(imagem, "uint8")
                faces_detectadas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                rostos = faces_detectadas.detectMultiScale(imagem_np)

                for (x, y, w, h) in rostos:
                    faces.append(imagem_np[y:y + h, x:x + w])
                    labels.append(id_atual)

                nomes[id_atual] = pessoa
            except Exception as e:
                registrar_log(f"⚠️ Imagem inválida ignorada: {caminho_arquivo} ({e})")

        id_atual += 1

    if not faces:
        raise Exception(f"Nenhuma imagem para treinamento em {pasta_treinamento}")

    reconhecedor = cv2.face.LBPHFaceRecognizer_create()
    reconhecedor.train(faces, np.array(labels))

    registrar_log("✅ Treinamento finalizado")
    return reconhecedor, nomes


# Interface binding
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from interface.interface import InterfaceOrganizador
    import sys

    app = QApplication(sys.argv)
    janela = InterfaceOrganizador()
    janela.btn_pausar.clicked.connect(lambda: definir_parar_processamento(True))
    janela.btn_reiniciar.clicked.connect(lambda: definir_parar_processamento(False))
    janela.show()
    sys.exit(app.exec_())