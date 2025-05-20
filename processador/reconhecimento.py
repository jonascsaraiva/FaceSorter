import os
import cv2
import numpy as np
from processador.utils import registrar_log

def treinar_reconhecedor(pasta_treinamento):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels = [], []
    nomes, mapeamento = [], {}

    registrar_log("Iniciando treinamento com LBPH")

    for idx, nome in enumerate(sorted(os.listdir(pasta_treinamento))):
        caminho_pessoa = os.path.join(pasta_treinamento, nome)
        if not os.path.isdir(caminho_pessoa):
            continue
        mapeamento[idx] = nome
        nomes.append(nome)

        for img_file in os.listdir(caminho_pessoa):
            img_path = os.path.join(caminho_pessoa, img_file)
            gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                registrar_log(f"Imagem inválida ignorada: {img_path}")
                continue
            faces.append(gray)
            labels.append(idx)

    if not faces:
        registrar_log("❌ Nenhuma imagem válida para treinamento.")
        raise RuntimeError("Nenhuma imagem para treinamento em " + pasta_treinamento)

    recognizer.train(faces, np.array(labels))
    registrar_log("✔️ Treinamento concluído com sucesso")
    return recognizer, mapeamento
