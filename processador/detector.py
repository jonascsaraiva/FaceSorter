import os
import shutil
import cv2
from processador.utils import registrar_log

def reconhecer_e_organizar(pasta_entrada, pasta_saida, reconhecedor, mapeamento, recortar, atualizar_progresso=None):
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    total = len(arquivos)

    registrar_log(f"📥 Iniciando processamento de {total} imagens da pasta: {pasta_entrada}")

    for i, arq in enumerate(arquivos):
        caminho = os.path.join(pasta_entrada, arq)
        try:
            img_color = cv2.imread(caminho)
            if img_color is None:
                registrar_log(f"⚠️ Imagem inválida ignorada: {caminho}")
                continue

            gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            nomes_encontrados = []
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                label, confianca = reconhecedor.predict(face)
                if confianca < 100:
                    nomes_encontrados.append(mapeamento[label])

            if nomes_encontrados:
                pasta_dest = "_e_".join(sorted(set(nomes_encontrados)))
            else:
                pasta_dest = "nao_identificado"

            destino_full = os.path.join(pasta_saida, pasta_dest)
            os.makedirs(destino_full, exist_ok=True)
            shutil.copy2(caminho, os.path.join(destino_full, arq))

            registrar_log(f"📦 Imagem '{arq}' movida para: {pasta_dest}")

            if atualizar_progresso:
                atualizar_progresso(int((i+1)/total*100))

        except Exception as e:
            registrar_log(f"❌ Erro ao processar '{arq}': {e}")
