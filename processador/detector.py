# processador/reconhecimento.py
import os
import cv2
import numpy as np
from processador.utils import registrar_log


def treinar_reconhecedor(pasta_treinamento):
    """
    Treina um reconhecedor LBPH a partir de subpastas em `pasta_treinamento`.
    Retorna o objeto recognizer e o mapeamento de labels para nomes.
    """
    # Cria o reconhecedor LBPH (requer opencv-contrib-python)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels = [], []
    mapeamento = {}

    registrar_log("🧠 Iniciando treinamento com LBPH")

    # Percorre cada subpasta (cada pessoa)
    for idx, nome in enumerate(sorted(os.listdir(pasta_treinamento))):
        caminho_pessoa = os.path.join(pasta_treinamento, nome)
        if not os.path.isdir(caminho_pessoa):
            continue
        mapeamento[idx] = nome

        # Carrega cada imagem em tons de cinza
        for arquivo in os.listdir(caminho_pessoa):
            caminho_imagem = os.path.join(caminho_pessoa, arquivo)
            gray = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                registrar_log(f"⚠️ Imagem inválida ignorada: {caminho_imagem}")
                continue
            faces.append(gray)
            labels.append(idx)

    # Valida existência de dados
    if not faces:
        registrar_log("❌ Nenhuma imagem válida para treinamento em " + pasta_treinamento)
        raise RuntimeError("Nenhuma imagem para treinamento em " + pasta_treinamento)

    # Treina o reconhecedor
    recognizer.train(faces, np.array(labels))
    registrar_log("✅ Treinamento concluído com sucesso")
    return recognizer, mapeamento