# Programa que le um arquivo e retorna outro arquivo com os indices de cada aquivo lido

# bibliotecas 
import os
import ssl 
import sys
import nltk
from nltk.corpus import mac_morpho
from pickle import load
from pickle import dump

# Variaveis do ssl, não sei ainda porque colocar
_create_unverified_https_context = ssl._create_unverified_context
ssl._create_default_https_context = _create_unverified_https_context


# variaveis mestre
stopwords = nltk.corpus.stopwords.words("portuguese")
stemmer = nltk.stem.RSLPStemmer()
lista_simbolos = ['.', ',', '!', '?', '...', '-', '\n', '\t', ' ']
lista_etiquetas = ['PREP', 'ART', 'KC', 'KS']

# funções

# Função que recebe o nome do arquivo e retorna uma lista com os dados tratados, ja sem símbolos e stopwords
def ler_arquivos(nome_arqv):
	lista_dados = []
	cop_lista = []
	

	arquivo_lido = open(nome_arqv, 'r', encoding='utf-8')
	lista_dados = arquivo_lido.read()
	lista_dados = lista_dados.lower()

	for simbolo in lista_simbolos:
		lista_dados = lista_dados.replace(simbolo,' ')

	arquivo_lido.close()

	lista_dados = lista_dados.split()
	cop_lista = lista_dados.copy()
	cop_lista = ' '.join([data for data in lista_dados if data not in stopwords])
	cop_lista = cop_lista.split()

	return cop_lista


# função que cria um arquivo binario para salvar tagger do etiquetador, para leitura mais rapida
# PS: executar o programa excluindo o .bin leva a uma execuçao bem mais demorada
def criar_tagger_bin():
	sentencas_etiquetadas = mac_morpho.tagged_sents()
	etiquetador_unigram = nltk.tag.UnigramTagger( sentencas_etiquetadas )
	output = open('etiqueta_tagger.bin', 'wb')
	dump(etiquetador_unigram, output, -1)
	output.close()


# funçao que le um arquivo binario de tag do unigram e retorna as tags para ser utilizada no etiquetador
def ler_tagger_bin():
	inpu = open('etiqueta_tagger.bin', 'rb')
	tagger = load(inpu)
	inpu.close()
	return tagger

# Função que trata os caracteres da lista
def trata_nome_arqv(lista):
	separador = ""
	lista = separador.join(lista)
	lista = lista.split()
	return lista


# pega o nome do arquivo com a lista de arquivos passado pela linha de comando e ja abre ele para leitura	
arquivo_base = open(sys.argv[1],'r')

# cria uma lista para receber os nomes dos arquivos que serão usados no indice
lista_arquivos = []
for linha in arquivo_base:
	lista_arquivos += linha

arquivo_base.close()

# lista que recebe o nome dos aquivos tratado para a utilização na abertura dos mesmos
lista_arquivos = trata_nome_arqv(lista_arquivos)

# dicionario que tem como relaçao o indice do arquivo e uma lista com os dados do arquivo respectivamente {indice_arquivo:[dados arquivo]}
dados_arqvs = {}
txt_arqvs = []

# contador para o indice do dicionario
num_arqv = 0

# for que para cada nome de arquivo ele executa a func ler_arquivos(nome do aquivo), e tem como saída o dicionario com os indices e dados de todos os arquivos da base 
for nome in lista_arquivos:
	txt_arqvs += ler_arquivos(nome)
	dados_arqvs[num_arqv] = ler_arquivos(nome)
	num_arqv+=1 

#if que faz a verificaçao se o arquivo binario ja existe, se sim ele le o arquivo, se nao ele cria o arquivo e le ele
if os.path.isfile('etiqueta_tagger.bin') == True:
	tagger = ler_tagger_bin()
else:
	criar_tagger_bin()
	tagger = ler_tagger_bin()




for n in range(len(dados_arqvs)):
	dados_etiquetados = tagger.tag(dados_arqvs[n])	
	dados_arqvs[n] = [stemmer.stem(dados_etiquetados[i][0]) for i in range(len(dados_etiquetados)) if dados_etiquetados[i][1] not in lista_etiquetas]


indice_invertido = {}
cont = 1
for data in dados_arqvs.values():
	for item in data:
		if item in indice_invertido:
			indice_invertido[item][cont] = data.count(item)
		else:
			indice_invertido[item] = {cont:data.count(item)}
	cont+=1

liste_simbolos_indice = ['{', '}']
arquivo_indice = open('indice.txt', 'w')

for item in indice_invertido:
	arquivo_indice.write(item+str(indice_invertido[item]).replace(' ', '').replace('}', '').replace(',', ' ').replace(':', ',').replace('{', ': '))
	arquivo_indice.write('\n')


arquivo_indice.close()