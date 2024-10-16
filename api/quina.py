import requests
from lxml import html
from flask import Flask, jsonify
import re  # Biblioteca para expressões regulares

app = Flask(__name__)

# URL da página
url = "https://www.loterias.com.br/quina/"

def obter_dados_quina():
    # Faz a requisição HTTP para obter o conteúdo da página
    response = requests.get(url)

    # Analisa o HTML utilizando lxml
    tree = html.fromstring(response.content)

    # Extrai o último resultado usando XPath
    ultimo_resultado_xpath = '/html/body/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[1]/div'
    ultimo_resultado = tree.xpath(ultimo_resultado_xpath)

    # Extrai as informações do próximo sorteio usando XPath
    proximo_sorteio_xpath = '/html/body/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[2]'
    proximo_sorteio = tree.xpath(proximo_sorteio_xpath)

    # Extrai a estimativa dentro do span com a classe 'hide-for-small-only'
    estimativa_xpath = '//span[@class="hide-for-small-only"]'
    estimativa_element = tree.xpath(estimativa_xpath)

    # Variáveis para armazenar as informações extraídas
    data_sorteio = ""
    valor_sorteado = ""
    vencedores = False
    numeros_sorteados = []
    data_prox_sorteio = ""
    estimativa = ""

    # Verifica se os dados do último sorteio foram encontrados e processa
    if ultimo_resultado:
        resultado_texto = ultimo_resultado[0].text_content().strip()
        
        # Extração da data do sorteio
        data_match = re.search(r'Terça-feira, \d{1,2} \w+ \d{4}', resultado_texto)
        if data_match:
            data_sorteio = data_match.group(0)
        
        # Extração do valor acumulado e remoção do "R$"
        valor_match = re.search(r'Acumulado: (\S+)R\$', resultado_texto)
        if valor_match:
            valor_sorteado = valor_match.group(1)  # Captura apenas o valor, sem "R$"
        
        # Extração dos vencedores (booleano)
        if "Sem vencedores" in resultado_texto:
            vencedores = False
        else:
            vencedores = True
        
        # Extração dos números sorteados (como array de inteiros)
        numeros_match = re.search(r'(\d{1,2} \d{1,2} \d{1,2} \d{1,2} \d{1,2})', resultado_texto)
        if numeros_match:
            numeros_sorteados = [int(n) for n in numeros_match.group(0).split()]

    # Verifica se os dados do próximo sorteio foram encontrados e processa
    if proximo_sorteio:
        proximo_sorteio_texto = proximo_sorteio[0].text_content().strip()
        
        # Extração da data do próximo sorteio
        data_prox_match = re.search(r'Quarta-feira, \d{1,2} \w+ \d{4}', proximo_sorteio_texto)
        if data_prox_match:
            data_prox_sorteio = data_prox_match.group(0)

    # Verifica se a estimativa foi encontrada
    if estimativa_element:
        estimativa = estimativa_element[0].text_content().strip()

    # Formata o resultado em JSON
    resultado_json = {
        "data_sorteio": data_sorteio if data_sorteio else "Não encontrado",
        "valor_sorteado": valor_sorteado if valor_sorteado else "Não encontrado",
        "vencedores": vencedores,
        "numeros_sorteados": numeros_sorteados,
        "data_prox_sorteio": data_prox_sorteio if data_prox_sorteio else "Não encontrado",
        "estimativa": estimativa if estimativa else "Não encontrado"
    }

    return resultado_json

@app.route('/api/quina', methods=['GET'])  # Modifiquei o endpoint para incluir 'api/'
def get_quina():
    # Obtém os dados da Quina e os retorna como JSON
    dados = obter_dados_quina()
    return jsonify(dados)

# Para executar localmente, você pode deixar este trecho
if __name__ == '__main__':
    app.run(debug=True)
