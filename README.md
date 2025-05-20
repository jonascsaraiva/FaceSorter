# FaceSorter

Aplicativo em Python com interface gráfica para separar imagens por reconhecimento facial.

## Funcionalidades
- Detecta rostos automaticamente
- Reconhece pessoas com base em um conjunto de treinamento
- Organiza imagens em pastas nomeadas
- Interface amigável com PyQt5
- Opção de recortar ou copiar imagem completa

## Como usar
1. Instale as dependências:
   pip install -r requirements.txt

2. Execute:
   python -m main

## Estrutura de pastas
- Entrada/: onde você coloca as imagens desorganizadas
- treinamento/: onde coloca as imagens por pessoa para treinamento
- saida/: onde o programa salva as imagens separadas
- interface/: interface gráfica em PyQt5
- processador/: lógica de detecção, reconhecimento e logs
- logs/: registros automáticos de ações e erros
