# processador/reconhecimento.py
import os
import cv2
import numpy as np
from PIL import Image
from processador.utils import registrar_log


def treinar_reconhecedor(pasta_treinamento):
    """
    Treina um reconhecedor LBPH a partir de subpastas em `pasta_treinamento`.
    Retorna o objeto recognizer e o mapeamento de labels para nomes.
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels = [], []
    mapeamento = {}

    registrar_log("🧠 Iniciando treinamento com LBPH em: " + pasta_treinamento)

    # Extensões de imagem válidas
    valid_ext = {'.jpg', '.jpeg', '.png', '.bmp'}

    # Percorre cada subpasta (cada pessoa)
    for idx, nome in enumerate(sorted(os.listdir(pasta_treinamento))):
        caminho_pessoa = os.path.join(pasta_treinamento, nome)
        if not os.path.isdir(caminho_pessoa):
            continue
        mapeamento[idx] = nome

        # Carrega cada arquivo na pasta da pessoa
        for arquivo in sorted(os.listdir(caminho_pessoa)):
            ext = os.path.splitext(arquivo)[1].lower()
            if ext not in valid_ext:
                registrar_log(f"⏭️ Ignorando arquivo não imagem: {arquivo}")
                continue
            caminho_imagem = os.path.join(caminho_pessoa, arquivo)
            # Tenta ler com OpenCV
            gray = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                # Fallback usando PIL para suportar paths Unicode
                try:
                    pil_img = Image.open(caminho_imagem).convert('L')
                    gray = np.array(pil_img)
                except Exception as e:
                    registrar_log(f"⚠️ Imagem inválida ignorada: {caminho_imagem} ({e})")
                    continue
            faces.append(gray)
            labels.append(idx)

    # Valida existência de dados
    if not faces:
        registrar_log("❌ Nenhuma imagem válida para treinamento em: " + pasta_treinamento)
        raise RuntimeError("Nenhuma imagem para treinamento em " + pasta_treinamento)

    recognizer.train(faces, np.array(labels))
    registrar_log("✅ Treinamento concluído com sucesso")
    return recognizer, mapeamento
