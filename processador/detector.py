import os
import shutil
import cv2
import numpy as np
from PIL import Image
from processador.utils import registrar_log
from PyQt5.QtWidgets import QProgressBar

def reconhecer_e_organizar(pasta_entrada, pasta_saida, reconhecedor, mapeamento, recortar, atualizar_progresso=None, barra_progresso: QProgressBar = None):
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
    total = len(arquivos)

    registrar_log(f"\U0001f4e5 Iniciando processamento de {total} imagens da pasta: {pasta_entrada}")

    if barra_progresso:
        barra_progresso.setFormat("%p%")
        barra_progresso.setTextVisible(True)

    for i, nome_arquivo in enumerate(arquivos):
        caminho = os.path.join(pasta_entrada, nome_arquivo)
        try:
            # Primeira tentativa com OpenCV
            imagem = cv2.imdecode(np.fromfile(caminho, dtype=np.uint8), cv2.IMREAD_COLOR)
            if imagem is None:
                # Fallback com PIL
                imagem_pil = Image.open(caminho).convert("RGB")
                imagem = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)

            cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            rostos = cascade.detectMultiScale(cinza, scaleFactor=1.1, minNeighbors=5)

            nomes_detectados = []
            for (x, y, w, h) in rostos:
                face = cinza[y:y+h, x:x+w]
                try:
                    label, confianca = reconhecedor.predict(face)
                    if confianca < 100:
                        nomes_detectados.append(mapeamento.get(label, "desconhecido"))
                except Exception as e:
                    registrar_log(f"⚠️ Erro ao reconhecer rosto em {nome_arquivo}: {e}")

            if nomes_detectados:
                pasta_final = "_e_".join(sorted(set(nomes_detectados)))
            else:
                pasta_final = "nao_identificado"

            destino = os.path.join(pasta_saida, pasta_final)
            os.makedirs(destino, exist_ok=True)

            if recortar and rostos != ():
                for idx, (x, y, w, h) in enumerate(rostos):
                    recorte = imagem[y:y+h, x:x+w]
                    nome_saida = f"{os.path.splitext(nome_arquivo)[0]}_face{idx}.jpg"
                    caminho_saida = os.path.join(destino, nome_saida)
                    cv2.imwrite(caminho_saida, recorte)
            else:
                shutil.copy2(caminho, os.path.join(destino, nome_arquivo))

            registrar_log(f"\U0001f4e6 '{nome_arquivo}' salvo em: {pasta_final}")

            progresso = int((i + 1) / total * 100)
            if atualizar_progresso:
                atualizar_progresso(progresso)
            if barra_progresso:
                barra_progresso.setValue(progresso)

        except Exception as e:
            registrar_log(f"❌ Erro ao processar '{nome_arquivo}': {e}")
