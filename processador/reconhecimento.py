# processador/reconhecimento.py
import os
import numpy as np
from PIL import Image
from processador.utils import registrar_log
import cv2

def treinar_reconhecedor(pasta_treinamento):
    """
    Treina um reconhecedor LBPH a partir de subpastas em `pasta_treinamento`.
    Retorna o objeto recognizer e o mapeamento de labels para nomes.
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels = [], []
    mapeamento = {}

    registrar_log(f"🧠 Iniciando treinamento com LBPH em: {pasta_treinamento}")

    valid_ext = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

    for idx, nome in enumerate(sorted(os.listdir(pasta_treinamento))):
        pasta_pessoa = os.path.join(pasta_treinamento, nome)
        if not os.path.isdir(pasta_pessoa):
            registrar_log(f"⏭️ Ignorando não-pasta de pessoa: {nome}")
            continue
        # Verifica existência de ao menos uma imagem válida na subpasta
        arquivos_sub = [f for f in os.listdir(pasta_pessoa)
                         if os.path.splitext(f)[1].lower() in valid_ext]
        if not arquivos_sub:
            registrar_log(f"⏭️ Ignorando pasta sem imagens: {nome}")
            continue
        mapeamento[idx] = nome

        for arquivo in sorted(arquivos_sub):
            caminho_img = os.path.join(pasta_pessoa, arquivo)
            try:
                pil_img = Image.open(caminho_img).convert('L')
                gray = np.array(pil_img)
            except Exception as e:
                registrar_log(f"⚠️ Falha ao abrir imagem: {caminho_img} ({e})")
                continue
            faces.append(gray)
            labels.append(idx)

    if not faces:
        registrar_log(f"❌ Nenhuma imagem válida para treinamento em: {pasta_treinamento}")
        raise RuntimeError(f"Nenhuma imagem para treinamento em {pasta_treinamento}")

    recognizer.train(faces, np.array(labels))
    registrar_log("✅ Treinamento concluído com sucesso")
    return recognizer, mapeamento
