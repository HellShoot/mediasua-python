import requests
from lxml import html
from urlparse import urlparse
from bs4 import BeautifulSoup
import json

if __name__ == '__main__':
    s = requests.Session()
    r = s.get(url="https://paco.ua.pt/secvirtual/c_historiconotas.asp")

    username = "EMAIL"
    password = "PASSWORD"

    tree = html.fromstring(r.content)
    o = urlparse(r.url)

    url_auth = o.scheme + "://" + o.netloc + tree.body.forms[0].attrib["action"]
    r = s.post(url_auth, data={'j_password': password, 'j_username': username, 'Submeter': 'OK'})

    tree = html.fromstring(r.content)

    inputs = tree.xpath("//input")

    payload = {'RelayState': inputs[0].value, 'SAMLResponse': inputs[1].value}

    r = s.post(tree.body.forms[0].attrib["action"], data=payload)
    r = s.get("https://paco.ua.pt/secvirtual/c_planocurr.asp")

    soup = BeautifulSoup(r.content)
    table = soup.find('table', attrs={'width':'95%', 'align':'center', 'cellspadding':'2'})

    cadeiras = []

    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 8 and cells[1].text.rstrip().replace("\r\n\t", "") != 'Codigo':
            if len(cells[7].text.rstrip().replace("\r\n\t", "")) != 0:
                cadeiras += [{'codigo': int(cells[1].text.rstrip().replace("\r\n\t", "")),
                             'nome': cells[2].text.rstrip().replace("\r\n\t", ""),
                             'ano': int(cells[3].text.rstrip().replace("\r\n\t", "")),
                             'semestre': int(cells[4].text.rstrip().replace("\r\n\t", "")),
                             'ects':float(cells[6].text.rstrip().replace("\r\n\t", "").replace(",", ".")),
                             'nota': float(cells[7].text.rstrip().replace("\r\n\t", "").replace(",", "."))}]
    nota = 0.0
    creditos = 0.0

    for cadeira in cadeiras:
        nota += (cadeira["nota"] * cadeira["ects"])
        creditos += cadeira["ects"]

    nota = nota / creditos

    semestres_ano = []

    for cadeira in cadeiras:
        if {"ano": cadeira["ano"], "semestre": cadeira["semestre"]} not in semestres_ano:
            semestres_ano += [{"ano": cadeira["ano"], "semestre": cadeira["semestre"]}]

    # notas por semestre e ano
    for semestre in semestres_ano:
        semestre["ects"] = 0
        semestre["nota"] = 0
        for cadeira in cadeiras:
            if cadeira["ano"] == semestre["ano"] and cadeira["semestre"] == semestre["semestre"]:
                semestre["ects"] += cadeira["ects"]
                semestre["nota"] += (cadeira["nota"] * cadeira["ects"])
        semestre["nota"] /= semestre["ects"]

    print "ECTS: " + str(creditos)
    print "Nota: " + str(nota)
    print "N. de Cadeiras: " + str(len(cadeiras))
    # print json.dumps({'cadeiras': cadeiras, 'media': nota, 'semestres': semestres_ano})