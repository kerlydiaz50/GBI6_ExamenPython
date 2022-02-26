# Importar módulos a utilizar 
import csv
import itertools
import re
import pandas as pd
from Bio import Entrez

# Función download_pubmed
def download_pubmed(keyword):
    """La función download_pubmed, se realizará para descargar la data de PubMed utilizando el ENTREZ de Biopython, esta recibe un argumento que es un keyword, el parámetro de entrada corresponde a este keyword y retorna."""
    
    Entrez.email = "kerly.diaz@est.ikiam.edu.ec"
    handle = Entrez.esearch(db="pubmed", 
                            term="Ecuador genomics[Title/Abstract]",
                            usehistory="y")
    record = Entrez.read(handle)
    # Generar una lista
    id_list = record["IdList"]
    #print(record["Count"])
    webenv = record["WebEnv"]
    query_key = record["QueryKey"]
    handle = Entrez.efetch(db="pubmed",
                           rettype="medline", 
                           retmode="text", 
                           retstart=0,
                           retmax=1000,
                           webenv=webenv,
                           query_key=query_key)
    keyword1 = handle.read()
    keyword2 = re.sub(r'\n\s{6}', ' ', keyword1)
    return (keyword2)

# Función mining_pubs
def mining_pubs(tipo,keyword2):
    """La función mining_pubmed, recibe un argumento/parámetro que es un tipo, este cambiará de acuerdo al objetivo, por lo que si el  tipo es "DP" este recupera el año de publicación del artículo, si el tipo es "AU" recupera el número de autores por PMID y si es "AD" recupera el conteo de autores por país."""
    
    # Tipo = "PMDI" recupera el número de referencia de PubMed, el cual es un número de los artículos indexados en PubMed
    PMID = re.findall("PMID- (\d*)", keyword2) 
    # Tipo = "DP" recupera el año de publicación del artículo
    Año = re.findall("DP\s{2}-\s(\d{4})", keyword2) 
    publicyear = pd.DataFrame() 
    publicyear["PMID"] = PMID
    publicyear["Años"] = Año
    # Tipo = "AU" recupera el número de autores por PMID 
    authornumber = keyword2.split("PMID- ") 
    authornumber.pop(0) 
    Autnumero = []
    for i in range(len(authornumber)):
        num = re.findall("AU -", authornumber[i])
        n = (len(num))
        Autnumero.append(n)
    Autnumero1 = pd.DataFrame()
    Autnumero1["PMID"] = PMID 
    Autnumero1["Número de autores"] = Autnumero
    
    # Tipo = "AD" recupera el conteo de autores por país
    ADcountries = []
    for line in keyword2.splitlines():
        if line.startswith("AD  -"):
            ADcountries.append(line[:])
    
    ADpaises1 = []
    ADpaises2 = []
    ADpaises3 = []
    ADpaises4 = []
    ADpaises5 = []
    ADpaises6 = []
    ADpaises7 = []
    ADpaisesTotal = []
    for line in keyword2.splitlines():
        if line.startswith("AD  -"):
            
            ADcountries = line[:]
            
            ADct1 = re.findall(r'\,\s(\w+)\.', ADcountries)
            ADct2 = re.findall(r'\,\s(\w+[^0-9\,]\s\w+[^0-9])\.', ADcountries)
            ADct3 = re.findall(r'\,\s(\w+)\.\s[a-z0-9_\.-]+@[\da-z\.-]+\.[a-z\.]{2,6}', ADcountries)
            ADct4 = re.findall(r'\,\s(\w+[^0-9\,]\s\w+[^0-9])\.\s[a-z0-9_\.-]+@[\da-z\.-]+\.[a-z\.]{2,6}', ADcountries)
            ADct5 = re.findall(r'\,\s(\w+)\. Electronic address:\s[a-z0-9_\.-]+@[\da-z\.-]+\.[a-z\.]{2,6}', ADcountries)
            ADct6 = re.findall(r'\,\s(\w+[^0-9\,]\s\w+[^0-9])\. Electronic address:\s[a-z0-9_\.-]+@[\da-z\.-]+\.[a-z\.]{2,6}', ADcountries)
            ADct7 = re.findall(r'\,\s\w+[0-9\-]\,\s(\w+)\.\n', ADcountries)
            
            ADpaises1.append(ADct1)
            ADpaises2.append(ADct2)
            ADpaises3.append(ADct3)
            ADpaises4.append(ADct4)
            ADpaises5.append(ADct5)
            ADpaises6.append(ADct6)
            ADpaises7.append(ADct7)   
    ADpaisesTotal = ADpaises1 + ADpaises2 + ADpaises3 + ADpaises4 + ADpaises5 + ADpaises6 + ADpaises7
    ADpaisesTotal = list(itertools.chain.from_iterable(ADpaisesTotal))
    len(ADpaisesTotal)
    unique_ADpaisesTotal = list(set(ADpaisesTotal))
    unique_ADpaisesTotal.sort()
    len(unique_ADpaisesTotal)
    worldcoord = {}
    with open('countries.txt') as f:
        csvr = csv.DictReader(f)
        for row in csvr:
            worldcoord[row['Name']] = [row['Latitude'], row['Longitude']]
    sortcountries = []
    longitudect = []
    latitudect = []
    quantct = []
    for i in unique_ADpaisesTotal:
        if i in worldcoord.keys():
            sortcountries.append(i)
            latitudect.append(float(worldcoord[i][0]))
            longitudect.append(float(worldcoord[i][1]))
            quantct.append(ADpaisesTotal.count(i))
    
    Numauthcountry = pd.DataFrame()
    Numauthcountry["country"] = sortcountries 
    Numauthcountry["num_auth"] = quantct
    
    # Finalmente, se coloca el dato de dataframes de cada tipo y que retorna
    if tipo == 'AD':
        return Numauthcountry
    if tipo == 'AU':
        return Autnumero1
    if tipo == 'DP':
        return publicyear