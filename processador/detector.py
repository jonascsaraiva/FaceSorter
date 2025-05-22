"""
Módulo responsável por detectar rostos nas imagens da pasta de entrada
usando o reconhecedor facial previamente treinado. Ele move ou copia as imagens
com base nos rostos reconhecidos para pastas organizadas na pasta de saída.
Inclui suporte a pausa e retomada do processo.
"""

import os
import shutil
import cv2
import numpy as np
from processador.utils import registrar_log

class EstadoProcessamento:
    """
    Classe para encapsular o estado de pausa/retomada do processamento,
    evitando o uso de variáveis globais soltas.
    """
    parar = False

def definir_parar_processamento(valor):
    EstadoProcessamento.parar = valor
    if valor:
        registrar_log("⏸️ Pausando processamento...")
    else:
        registrar_log("▶️ Retomando processamento...")

def carregar_classificador():
    return cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def reconhecer_e_organizar(pasta_entrada, pasta_saida, reconhecedor, mapeamento, recortar, atualizar_progresso=None):
    cascade = carregar_classificador()
    arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
    total = len(arquivos)

    registrar_log(f"📥 Iniciando processamento de {total} imagens da pasta: {pasta_entrada}")

    for i, nome_arquivo in enumerate(arquivos):
        if EstadoProcessamento.parar:
            registrar_log("⏹️ Processamento interrompido")
            break

        caminho = os.path.join(pasta_entrada, nome_arquivo)
        try:
            imagem = cv2.imread(caminho)
            if imagem is None:
                registrar_log(f"⚠️ Imagem inválida ignorada: {caminho}")
                continue

            cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            rostos = cascade.detectMultiScale(cinza, scaleFactor=1.1, minNeighbors=5)

            nomes_detectados = []
            for (x, y, w, h) in rostos:
                face = cinza[y:y+h, x:x+w]
                try:
                    label, confianca = reconhecedor.predict(face)
                    if confianca < 100:
                        nomes_detectados.append(mapeamento.get(label, "nao_identificado"))
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

            registrar_log(f"📦 '{nome_arquivo}' salvo em: {pasta_final}")

            if atualizar_progresso:
                try:
                    atualizar_progresso(int((i + 1) / total * 100))
                except Exception as e:
                    registrar_log(f"⚠️ Erro ao atualizar progresso: {e}")

        except Exception as e:
            registrar_log(f"❌ Erro ao processar '{nome_arquivo}': {e}")
