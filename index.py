# ouverture du fichier stopwords_fr
stopwordsfile = "cacm/common_words"
# Récupération de la liste des mots vides
stopwords_list = open(stopwordsfile, "r", encoding="utf-8").read().splitlines()

ponctuation_list = ['?', '.', '!', '<', '>', '}', '{', ':', '(', ')', '[', ']', '\"', ',', '-', "»", "«", '\'', '’',
                    '#', '+', '_', '-', '*', '/', '=']


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
def read_documents(path):
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
            

def main():
    doc_freq_list = read_documents("cacm/cacm.all")
    inverse_file_by_freq = create_inverse_file_by_freq(doc_freq_list)
    print("c bon")

    
if __name__ == "__main__":
    main()