import pickle
import math

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
        term_weights = []
        #count documents in which term appears
        nb_doc_term = len(inverse_file_by_freq[term])
        #docuemnts number
        nb_doc = len(inverse_file)
        #calculate weight
        for doc in inverse_file_by_freq[term]:
            docno = doc[0]
            weight = (doc[1]/doc[1]) * math.log10((nb_doc/nb_doc_term)+1)
            term_weights.append((docno, weight))

        inverse_file_by_weight[term] = term_weights
    return inverse_file_by_weight    

#1.3 Fonction d'acces
# 1.3.1 cette fonction retourne la liste des termes et leurs fréquences dans un document donné
def get_doc_freq(inverse_file_path, docno):
    return openPkl(inverse_file_path)[docno-1][1]

#1.3.2 cette fonction retourne la frequence d'un terme donné dans chaque document
def get_term_freq(inverse_file_by_freq_path, term):
    return openPkl(inverse_file_by_freq_path)[term]

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
    """
    inverse_file_by_weight = create_inverse_file_by_weight("out/inversefilebyfreq.pkl","out/inversefile.pkl")
    with open("out/inversefilebyweight", "w", encoding="utf-8") as file:
        file.write(str(inverse_file_by_weight))
        savePkl(inverse_file_by_weight, "inversefilebyweight.pkl", "out/")

    print(get_doc_freq("out/inversefile.pkl", 146))
    print(len(get_term_freq("out/inversefilebyfreq.pkl","report")))
    print("------------------------------")
    print(inverse_file_by_weight["report"])
    print("c bon")


if __name__ == "__main__":
    main()