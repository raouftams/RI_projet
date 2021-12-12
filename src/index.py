import pickle
import math
from tqdm import tqdm

# ouverture du fichier stopwords_fr
stopwordsfile = "cacm/common_words"
# Récupération de la liste des mots vides
stopwords_list = open(stopwordsfile, "r", encoding="utf-8").read().splitlines()

ponctuation_list = ['?', '.', '!', '<', '>', '}', '{', ':', '(', ')', '[', ']', '\"', ',', '-', "»", "«", '\'', '’',
                    '#', '+', '_', '-', '*', '/', '=']

#Utilities functions
def openPkl(file_path):
    with  open(file_path,"rb") as file:
        return pickle.load(file)

def savePkl(objname,filename,pathsave):
    with  open(pathsave+filename,"wb") as file:
        pickle.dump(objname,file,pickle.HIGHEST_PROTOCOL)

# Eliminer les mots vides et la ponctuation
def Stopword_elimination(text):
    word_list = []
    # Eliminer la punctuation
    for character in ponctuation_list:
        text = text.replace(character, ' ')

    # str -> list
    words = text.split()
    for word in words:
        if word.lower() not in stopwords_list:
            word_list.append(word.lower())
    return word_list

# Dictionnaire des fréquences
def dict_freq(word_list):
    frequence_dict = {}
    for word in word_list:
        if word not in frequence_dict:
            frequence_dict[word] = word_list.count(word)
    return frequence_dict

#read all documents
def create_inverse_file(path):
    title = ""
    text = ""
    doc_freq_list = []
    with open(path, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith(".I"):
                docno = line.split()[1]
            if line.startswith('.T'):
                title = lines[i+1]
            if line.startswith(".W"):
                text = ""
                j = i + 1
                while not line.startswith('.B'):
                    if(j < len(lines)):
                        text += lines[j] + " "
                        line = lines[j]
                        j += 1
                i = j
            if line.startswith(".B"):
                doc_text = title + text
                word_list = Stopword_elimination(doc_text)
                frequence_dict = dict_freq(word_list)
                doc_freq_list.append((docno, frequence_dict))
            
            i += 1
    file.close()
    return doc_freq_list

#création d'un fichier inversé par féquence
def create_inverse_file_by_freq(doc_freq_list):
    inverse_file_by_freq = {}
    for doc in doc_freq_list:
        docno = doc[0]
        frequence_dict = doc[1]
        for word in frequence_dict.keys():
            if word not in inverse_file_by_freq.keys():
                inverse_file_by_freq[word] = []
            inverse_file_by_freq[word].append((docno, frequence_dict[word]))

    return inverse_file_by_freq 

#création d'un fichier inversé par pondération
def create_inverse_file_by_weight(inverse_file_by_freq_path, inverse_file_path):
    inverse_file_by_freq = openPkl(inverse_file_by_freq_path)
    inverse_file = openPkl(inverse_file_path)
    inverse_file_by_weight = {}
    for term in inverse_file_by_freq.keys():
        term_weights = {}
        #count documents in which term appears
        nb_doc_term = len(inverse_file_by_freq[term])
        #docuemnts number
        nb_doc = len(inverse_file)
        #calculate weight
        for doc in inverse_file_by_freq[term]:
            docno = doc[0]
            weight = (doc[1]/doc[1]) * math.log10((nb_doc/nb_doc_term)+1)
            term_weights[docno] = weight

        inverse_file_by_weight[term] = term_weights
    return inverse_file_by_weight    

#1.3 Fonction d'acces
# 1.3.1 cette fonction retourne la liste des termes et leurs fréquences dans un document donné
def get_doc_freq(inverse_file_path, docno):
    inverse_file = openPkl(inverse_file_path)
    if docno-1 < len(inverse_file):
        return inverse_file[docno-1][1]
    
    return None

#1.3.2 cette fonction retourne la frequence d'un terme donné dans chaque document
def get_term_freq(inverse_file_by_freq_path, term):
    inverse_file_by_freq = openPkl(inverse_file_by_freq_path)
    if term in inverse_file_by_freq.keys():
        return inverse_file_by_freq[term]
    
    return None


"""Modèle booléen"""
def eliminate_logical_operators(request):
    return request.replace("and", " ").replace("or", " ").replace("not", " ").replace("(", " ").replace(")", " ")

def replace_logical_by_mathematical_operators(request):
    request = request.replace("and", "*").replace("or", "+")
    partitioned_request = list(request.partition("not"))
    for i in range(0, len(partitioned_request)-1):
        if partitioned_request[i] == "not":
            partitioned_request[i] = "int(not"
            partitioned_request[i+1] = partitioned_request[i+1] + ")"
    
    temp_request = ""
    for i in range(0, len(partitioned_request)):
        temp_request += partitioned_request[i]
    return temp_request

def create_boolean_model(inverse_file_path, request:str):
    request = request.lower()
    transformed_request = eliminate_logical_operators(request)
    request_list = transformed_request.split(" ")
    inverse_file = openPkl(inverse_file_path)
    termes_in_doc = {}
    pertinent_docs = []
    for doc in inverse_file:
        for term in request_list:
            if term not in doc[1].keys():
                termes_in_doc[term] = 0
            else:
                termes_in_doc[term] = 1


        temp_request = request
        for term in termes_in_doc.keys():
            if term != "":
                temp_request = temp_request.replace(term, str(termes_in_doc[term]))
        
        if eval(replace_logical_by_mathematical_operators(temp_request)):
            pertinent_docs.append([doc[0], len(doc[1].keys())])

    return pertinent_docs

"""Modèle vectoriel"""

#calcul avec méthode de produit interne
def intern_product(inverse_file,inverse_file_by_weight, request_vector):
    pertinent_docs = {}
    for doc in inverse_file:
        request_weight_in_doc = 0
        doc_number = doc[0]
        for term in request_vector:
            if term in doc[1].keys():
                request_weight_in_doc += inverse_file_by_weight[term][doc_number] * request_vector[term]
        
        if request_weight_in_doc > 0:
            pertinent_docs[doc_number] = request_weight_in_doc
    
    pertinent_docs = dict(sorted(pertinent_docs.items(), key=lambda item: item[1], reverse=True))
    return pertinent_docs

#calcul avec coefficient de dice
def dice_coefficient(inverse_file,inverse_file_by_weight, request_vector):
    pertinent_docs = {}
    for doc in inverse_file:
        request_weight_in_doc = 0
        wij_square = 0
        wiq_square = 0
        doc_number = doc[0]
        for term in request_vector:
            if term in doc[1].keys():
                request_weight_in_doc += inverse_file_by_weight[term][doc_number] * request_vector[term]
                wij_square += inverse_file_by_weight[term][doc[0]] ** 2
                wiq_square += request_vector[term] ** 2

        if request_weight_in_doc > 0:
            pertinent_docs[doc_number] = (2*request_weight_in_doc)/(wij_square + wiq_square)
    
    pertinent_docs = dict(sorted(pertinent_docs.items(), key=lambda item: item[1], reverse=True))
    return pertinent_docs

#calcul avec mesure de cosinus
def mesure_cosinus(inverse_file,inverse_file_by_weight, request_vector):
    pertinent_docs = {}
    for doc in inverse_file:
        request_weight_in_doc = 0
        wij_square = 0
        wiq_square = 0
        doc_number = doc[0]
        for term in request_vector:
            if term in doc[1].keys():
                request_weight_in_doc += inverse_file_by_weight[term][doc_number] * request_vector[term]
                wij_square += inverse_file_by_weight[term][doc[0]] ** 2
                wiq_square += request_vector[term] ** 2

        if request_weight_in_doc > 0:
            pertinent_docs[doc_number] = request_weight_in_doc/math.sqrt(wij_square * wiq_square)
    
    pertinent_docs = dict(sorted(pertinent_docs.items(), key=lambda item: item[1], reverse=True))
    return pertinent_docs

#calcul avec mesure jaccard
def mesure_jaccard(inverse_file,inverse_file_by_weight, request_vector):
    pertinent_docs = {}
    for doc in inverse_file:
        request_weight_in_doc = 0
        wij_square = 0
        wiq_square = 0
        doc_number = doc[0]
        for term in request_vector:
            if term in doc[1].keys():
                request_weight_in_doc += inverse_file_by_weight[term][doc_number] * request_vector[term]
                wij_square += inverse_file_by_weight[term][doc[0]] ** 2
                wiq_square += request_vector[term] ** 2

        if request_weight_in_doc > 0:
            pertinent_docs[doc_number] = request_weight_in_doc/(wij_square + wiq_square - request_weight_in_doc)
    
    pertinent_docs = dict(sorted(pertinent_docs.items(), key=lambda item: item[1], reverse=True))
    return pertinent_docs


def create_vectorial_model(inverse_file_by_weight_path, inverse_file_path, request:str, method = 1):
    """
        method: la méthode utilisée pour calculer les poids
            1- produit intern
            2- coef de dice
            3- mesure du cosinus
            4- mesure Jaccard
    """
    request = request.lower()
    request_list = Stopword_elimination(request) 
    inverse_file_by_weight = openPkl(inverse_file_by_weight_path)
    inverse_file = openPkl(inverse_file_path)
    request_vector = {}
    for term in inverse_file_by_weight.keys():
        if term in request_list:
            request_vector[term] = 1
    
    if method == 2:
        return dice_coefficient(inverse_file, inverse_file_by_weight, request_vector)
    
    if method == 3:
        return mesure_cosinus(inverse_file, inverse_file_by_weight, request_vector)
    
    if method == 4:
        return mesure_jaccard(inverse_file, inverse_file_by_weight, request_vector)

    return intern_product(inverse_file, inverse_file_by_weight, request_vector)
                
"""---------------------Evaluation-----------------------"""
def list_to_string(list):
    string = ""
    for item in list:
        string += str(item) + " "
    return string

def read_query(query_file_path):
    queries = {}
    with open(query_file_path, 'r', encoding="utf_8") as file:
        lines = file.read().splitlines()
        i = 0
        query = ""
        while i < len(lines):
            line = lines[i]
            if line.startswith(".I"):
                query_nb = line.split()[1]
            if line.startswith(".W"):
                query = ""
                j = i + 1
                while not line.startswith('.N'):
                    if(j < len(lines)):
                        query += lines[j] + " "
                        line = lines[j]
                        j += 1
                i = j
            if line.startswith(".N"):
                queries[query_nb] = list_to_string(Stopword_elimination(query))
            i += 1
    return queries

def read_qrels(qrels_file_path):
    queries = {}
    with open(qrels_file_path, "r", encoding="utf_8") as file:
        lines = file.read().splitlines()
        for line in lines:
            line_list = line.split(" ")
            query_nb = line_list[0]
            if query_nb not in queries.keys():
                queries[query_nb] = []
            queries[query_nb].append(line_list[1])
    
    return queries
        


def main():
    """
    inverse_file = create_inverse_file("cacm/cacm.all")
    # save inverse file
    with open ("out/inversefile","w",encoding="utf-8") as file:
        file.write(str(inverse_file))
        savePkl(inverse_file,"inversefile.pkl","out/")

    inverse_file_by_freq = create_inverse_file_by_freq(inverse_file)
    # save inverse file by freq
    with open ("out/inversefilebyfreq","w",encoding="utf-8") as file:
        file.write(str(inverse_file))
        savePkl(inverse_file_by_freq,"inversefilebyfreq.pkl","out/")
    
    inverse_file_by_weight = create_inverse_file_by_weight("out/inversefilebyfreq.pkl","out/inversefile.pkl")
    with open("out/inversefilebyweight", "w", encoding="utf-8") as file:
        file.write(str(inverse_file_by_weight))
        savePkl(inverse_file_by_weight, "inversefilebyweight.pkl", "out/")
    
    #print(create_inverse_file("../cacm/cacm.all"))
    print(len(get_term_freq("out/inversefilebyfreq.pkl", "computer")))
    print(len(create_boolean_model("out/inversefile.pkl", "(computer or key)")))
    print(len(create_boolean_model("out/inversefile.pkl", "key")))
    print("-------------------------------------------------------------")
    print(openPkl("out/inversefilebyweight.pkl")["computer"]["3204"])
    print(openPkl("out/inversefilebyweight.pkl")["monica"]["3204"])
    print("-------------------------------------------------------------")
    print(create_vectorial_model("out/inversefilebyweight.pkl", "out/inversefile.pkl", "computer key monica", 4))
    #print(create_inverse_file_by_weight("../out/inversefilebyfreq.pkl", "../out/inversefile.pkl")["computer"]["4"])
    """

    
    requests = read_query("cacm/query.text")
    pertinent_docs = read_qrels("cacm/qrels.text")

    for i in range(1, 5):
        rappel = 0
        precision = 0
        nb_selected_pertinent_docs = 0
        nb_selcted_docs = 0

        vectorial_pertinent_docs = create_vectorial_model("out/inversefilebyweight.pkl", "out/inversefile.pkl", requests["10"], i)
        temp_list = vectorial_pertinent_docs.values()
        max_value = max(temp_list)

        for item in vectorial_pertinent_docs.items():
            if item[1] == max_value:
                nb_selcted_docs += 1
                if item[0] in pertinent_docs["10"]:
                    nb_selected_pertinent_docs += 1

        rappel = nb_selected_pertinent_docs / len(pertinent_docs["10"])
        precision = nb_selected_pertinent_docs / nb_selcted_docs
    
        print(str(i) + ": " + str(rappel) + "/" + str(precision))
        


if __name__ == "__main__":
    main()

