"""
Módulo de reconhecimento facial.

Este módulo realiza o treinamento de um reconhecedor facial (LBPH) com base nas imagens
presentes em subpastas da pasta de treinamento, onde cada subpasta representa uma pessoa.
Ele também define as opções de pausa/retomada durante o processo e registra logs para cada etapa.
"""

import os
import cv2
import numpy as np
from PIL import Image
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

def treinar_reconhecedor(pasta_treinamento, atualizar_progresso=None):
    if not os.path.exists(pasta_treinamento):
        raise Exception(f"Pasta de treinamento não encontrada: {pasta_treinamento}")

    faces = []
    labels = []
    nomes = {}
    id_atual = 0
    classificador = carregar_classificador()

    registrar_log(f"🧠 Iniciando treinamento com LBPH em: {pasta_treinamento}")

    pastas = [p for p in os.listdir(pasta_treinamento) if os.path.isdir(os.path.join(pasta_treinamento, p))]
    total_pastas = len(pastas)

    for i, pessoa in enumerate(pastas):
        caminho_pessoa = os.path.join(pasta_treinamento, pessoa)

        for arquivo in os.listdir(caminho_pessoa):
            if EstadoProcessamento.parar:
                registrar_log("⏹️ Treinamento interrompido")
                return None, {}

            caminho_arquivo = os.path.join(caminho_pessoa, arquivo)
            if not arquivo.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                registrar_log(f"⏭️ Ignorando não-imagem: {arquivo}")
                continue

            try:
                imagem = Image.open(caminho_arquivo).convert("L")
                imagem_np = np.array(imagem, "uint8")
                rostos = classificador.detectMultiScale(imagem_np)

                for (x, y, w, h) in rostos:
                    faces.append(imagem_np[y:y + h, x:x + w])
                    labels.append(id_atual)

                nomes[id_atual] = pessoa
            except Exception as e:
                registrar_log(f"⚠️ Imagem inválida ignorada: {caminho_arquivo} ({e})")

        id_atual += 1
        if atualizar_progresso:
            try:
                atualizar_progresso(int((i + 1) / total_pastas * 100))
            except Exception as e:
                registrar_log(f"⚠️ Erro ao atualizar progresso: {e}")

    if not faces:
        raise Exception(f"Nenhuma imagem para treinamento em {pasta_treinamento}")

    reconhecedor = cv2.face.LBPHFaceRecognizer_create()
    reconhecedor.train(faces, np.array(labels))

    registrar_log("✅ Treinamento finalizado")

    return reconhecedor, nomes
