import pandas as pd
import re
import math
from rdflib import Literal, XSD
from Ontolex import Lexicon


hind_lex ={'name':'chamuca_hi_lex', 'desc':'Lexical information derived in part from wiktionary, https://www.wiktionary.org', 'lang':['hi'], 'entries': {}}
port_lex = {'name':'chamuca_port_lex', 'desc':'Lexical information derived in part from wiktionary, https://www.wiktionary.org', 'lang':['pt'], 'entries': {}}
urdu_lex  = {'name':'chamuca_ur_lex', 'desc':'Lexical information derived in part from wiktionary, https://www.wiktionary.org', 'lang':['ur'], 'entries': {}}
gend = lambda g: 'masculine' if g == 'm.' else 'feminine' if g == 'f.' else 'unknown'
pos = lambda ps: 'commonNoun' if ps == 'noun' else 'properNoun' if ps == 'proper noun' else 'interjection' if ps == 'Interjection' else 'nan'
#lemma = lambda head, trans, ipa: {'rep':[(head, "hi-deva"), (trans, "hi-Latn")], 'lemma':True, 'id': head+'_lemma', 'number':'singular', 'case':'directCase', 'ipa':ipa}
lemma = lambda scr1, scr2, head, trans, ipa: {'rep':[(head, scr1), (trans, scr2)], 'lemma':True, 'id': str(head)+'_lemma', 'number':'singular', 'case':'directCase', 'ipa':ipa}
#lemma_mi = lambda head, trans : {'rep':[(head, "hi-Deva"), (trans, "hi-Latn")], 'lemma':True, 'id': head+'_lemma', 'number':'singular', 'case':'directCase'}
lemma_s = lambda scr1, scr2, head, trans : {'rep':[(head, scr1), (trans, scr2)], 'lemma':True, 'id': str(head)+'_lemma', 'number':'singular', 'case':'directCase'}
obl_sing = lambda form,lemm: {'rep':[(form, "hi-Deva")], "lemma":False, 'id': form +'_os_form_'+lemm, 'number':'singular', 'case':'obliqueCase'}
voc_sing = lambda form,lemm: {'rep':[(form, "hi-Deva")], "lemma":False, 'id': form+'_vs_form_'+lemm,'number':'singular', 'case':'vocativeCase'}
dir_plu = lambda form,lemm: {'rep':[(form, "hi-Deva")], "lemma":False, 'id': form+'_dp_form_'+lemm, 'number':'plural', 'case':'directCase'}
obl_plu = lambda form,lemm: {'rep':[(form, "hi-Deva")], "lemma":False, 'id': form+'_op_form_'+lemm, 'number':'plural', 'case':'obliqueCase'}
voc_plu = lambda form,lemm: {'rep':[(form, "hi-Deva")], "lemma":False, 'id': form+'_vp_form_'+lemm,'number':'plural', 'case':'vocativeCase'}

posp = lambda ps: 'commonNoun' if ps== 'Noun' else ps
genp = lambda g: 'masculine' if g == 'Masculine' else 'feminine' if g == 'Feminine' else 'unknown'

urdu = lambda ur: ur if isinstance(ur, str) else 'NA'

def is_valid_integer_literal(value):
    try:
        # Attempt to create a Literal with explicit integer datatype
        lit_int = Literal(value, datatype=XSD.integer)

        # Check if the parsed value is an integer
        if lit_int.value is not None and isinstance(lit_int.value, int):
            return True, lit_int.value  # Valid integer
        return False, None  # Not a valid integer
    except Exception as e:
        # If an exception occurs, it's not a valid integer
        return False, None


def extract_ipas(input_string):
    # Regular expression pattern to match substrings between '/'
    pattern = r'/(?P<substring>.*?)\/'
    
    # Find all matches using regular expression
    matches = re.findall(pattern, input_string)
    
    # Return the list of matched substrings
    return matches

def extract_senses(input_string):
    if isinstance(input_string, str):
    # Split the input string based on '&'
        substrings = input_string.split('&')
    
    # Remove leading spaces from each substring
        substrings = [substring.strip() for substring in substrings]

        return substrings
    else:
        return ['']

def upload_pt():
    df2 = pd.read_csv("PtLex.tsv", sep='\t')
    senseIndex = ('', 1)
    for index, row in df2.iterrows():
        lemma = str(row['Lemma']).replace(' ','')
        word_id = lemma +'_entry'
        gr = genp(row['Gender'])
        pos = posp(row['Part_of_Speech'])
        formstrings = [substring.strip() for substring in str(row['Singular and Plural']).split(',')]
        forms_1 = {'rep':[(lemma, "pt")], 'lemma':True, 'id':lemma+'_lemma', 'number':'singular'}
        if len(formstrings)==2: 
            forms_2 = {'rep':[(formstrings[1], "pt")], 'lemma':False, 'id':lemma+'_plural', 'number':'plural'}
            forms = [forms_1, forms_2]
        else:
            print('strange '+lemma)
            forms = [forms_1]
    
        if senseIndex[0] == lemma:
            port_lex['entries'][word_id]['sense'] = port_lex['entries'][word_id]['sense']+[{'id': lemma+'_sense_'+str(senseIndex[1]), 'def':row['Definition']}]
            senseIndex = (lemma, senseIndex[1]+1)
        else:
            senseContent = [{'id': lemma+'_sense_1', 'def':row['Definition']}]
            port_lex['entries'][word_id] = {'gender':gr, 'entry_type':'Word', 'pos': str(pos), 'sense':senseContent, 'form':forms}
            senseIndex = (lemma, 2)
      
    return port_lex

    
def upload_ur(file_name):
    # upload file into dataframe df1
    # df1 = pd.read_csv("SimpleUrdu.tsv", sep='\t')
    df1 = pd.read_csv(file_name, sep='\t')
    i = 0

    #iterate through each row of the dataframe
    for index, row in df1.iterrows():
        # check if headword exists, if not, skip row
        if not pd.isnull(row['Headword']):
            # create id for word by combining headword with '_entry' tag

            
            headword = str(row['Headword']).replace(' ','')
            print(headword)
            word_id = headword+'_entry'

            # extract gender, ipa, and lemma info from the row
            gr = gend(row['Gender'])
            ipa_row = row['Pronunciation']
            ipas = []
            lemmaForm = headword

            if isinstance(ipa_row, str):
                ipas = extract_ipas(row['Pronunciation'])
                #print(str(ipas))
                ipa_lemma = ['']
                if ipas != []:
                    ipa_lemma = ipas
                forms =  [lemma("ur-Arab", "ur-Latn", headword, row['Transliteration'], ipa_lemma)]
            else:
                forms =  [lemma_s("ur-Arab", "ur-Latn",headword, row['Transliteration'])]

            hindi_seeAlso = "http://lari-datasets.ilc.cnr.it/chamuca_hi_lex#"+urdu(row['Headword Hindi']).replace(' ', '')
            # extract sense information from the 'Sense (Wiktionary)' column
            senses = extract_senses(row['Sense (Wiktionary)'])
            sense_content = []
            # we will count the number of senses with j
            j = 1

            # check if the list of senses consists of one item,
            # otherwise go through the list and create a new sense_id for each sense
            # augmenting j each time
            
            if len(senses) == 1:
                sense_content = [{'id': str(headword) +'_sense', 'def':senses[0]}]
            else:
                for count in senses:
                    print(headword+'_sense_'+str(j))
                    sense_content = sense_content + [{'id': str(headword)+'_sense_'+str(j), 'def':count}]
                    j +=1
                
            print(hindi_seeAlso)
        else:
            print(row['Etymon pt-PT'])
        corpus = 0
        corpus_str = str(row['urTenTen18']).replace(",", "")
        if corpus_str == 'N':
            corpus = 'N'
        elif is_valid_integer_literal(corpus_str)[0]:
            corpus = is_valid_integer_literal(corpus_str)[1]
            print("urdu corpus: "+ str(corpus))
        porEtymon = "http://lari-datasets.ilc.cnr.it/chamuca_pt_lex#"+str(row['Etymon pt-PT'])
        etymology = row['Etymology Free']
        hindi_head = (row['Headword Hindi']).replace(' ', '')
        if hindi_head != 'NA':
            hindi_seeAlso = "http://lari-datasets.ilc.cnr.it/chamuca_ur_lex#"+hindi_head+"_entry"
        else:
            hindi_seeAlso = 'NA'
        
        urdu_lex['entries'][word_id] = {'gender':gr, 'entry_type':'Word', 'pos':pos(row['Part of Speech']), 'sense':sense_content, 'seeAlso':hindi_seeAlso, 'form':forms, 'etymon':porEtymon, 'etymology': etymology, 'urTenTen18':corpus}
        

    return urdu_lex


def upload_hl(file_name):
    # upload file into dataframe df
    # df = pd.read_csv("LessSimpleHindi.tsv", sep='\t')
    df = pd.read_csv(file_name, sep='\t')
    i = 0
    # iterate through each row of the dataframe df
    for index, row in df.iterrows():
        # make sure you only iterate through the first 60 rows only
        # this should be updated
        #if i == 60:
        #    break
        # create id for word by combining headword with '_entry' tag
        word_id = str(row['Headword'])+'_entry'
        # extract gender, ipa and lemma info from the row
        gr = gend(row['Gender'])
        ipa_row = row['Pronunciation']
        ipas = []
        lemmaForm = row['Headword']
        # check if the ipa_row info is a string, in which case
        # add it to the set of forms in the list form
        if isinstance(ipa_row, str):
            ipas = extract_ipas(row['Pronunciation'])
            #print(str(ipas))
            ipa_lemma = ['']
            if ipas != []:
                ipa_lemma = ipas
            forms =  [lemma("hi-Deva", "hi-Latn", row['Headword'], row['Transliteration'], ipa_lemma)]
        else:
            forms =  [lemma_s("hi-Deva", "hi-Latn", row['Headword'], row['Transliteration'])]

        # extract sense information from the 'Sense (Wiktionary)' column
        senses = extract_senses(row['Definition'])
        sense_content = []
        # we will count the number of senses with j
        j = 1

        # check if the list of senses consists of one item,
        # otherwise go through the list and create a new sense_id for each sense
        # augmenting j each time
        
        if len(senses) == 1:
            sense_content = [{'id': str(row['Headword'])+'_sense', 'def':senses[0]}]
        else:
            for count in senses:
                print(row['Headword']+'_sense_'+str(j))
                sense_content = sense_content + [{'id': str(row['Headword'])+'_sense_'+str(j), 'def':count}]
                j +=1

        # corpus information
        corpus = 0
        corpus_str = str(row['hiTenTen21 Absolute (1)']).replace(",", "")
        if corpus_str == 'N':
            corpus = 'N'
        elif is_valid_integer_literal(corpus_str)[0]:
            corpus = is_valid_integer_literal(corpus_str)[1]

            
        # grammatical information (different forms of the noun)
        if not pd.isnull(row['oblique singular']):
            # split obl_sing
            obls = row['oblique singular']
            substrings = [substring.strip() for substring in obls.split(',')]
            forms = forms + [obl_sing(r, lemmaForm) for r in substrings]

            vocs = row['vocative singular']
            substrings = [substring.strip() for substring in vocs.split(',')]
            forms = forms + [voc_sing(r, lemmaForm) for r in substrings]

            dirp = row['direct plural'] 
            substrings = [substring.strip() for substring in vocs.split(',')]
            forms = forms + [dir_plu(r, lemmaForm) for r in substrings]

            oblp = row['oblique plural']
            substrings = [substring.strip() for substring in oblp.split(',')]
            forms = forms + [obl_plu(r, lemmaForm) for r in substrings]

            vocp = row['vocative plural']
            substrings = [substring.strip() for substring in vocp.split(',')]
            forms = forms + [voc_plu(r, lemmaForm) for r in substrings]
            
        else:
            print(row['Headword'])
        urdu_head = urdu(row['Urdu ']).replace(' ', '')
        if urdu_head != 'NA':
            urdu_seeAlso = "http://lari-datasets.ilc.cnr.it/chamuca_ur_lex#"+urdu_head+"_entry"
        else:
            urdu_seeAlso = 'NA'
            print(urdu_seeAlso)
        porEtymon = "http://lari-datasets.ilc.cnr.it/chamuca_pt_lex#"+str(row['Etymon pt-PT'])
        etymology = row['Etymology Free']

        print(corpus)
        hind_lex['entries'][word_id] = {'gender':gr, 'entry_type':'Word', 'pos':pos(row['Part of Speech']),'form':forms, 'sense':sense_content, 'seeAlso':urdu_seeAlso, 'etymon':porEtymon, 'etymology': etymology, 'hiTenTen21':corpus}
        i+=1

    return hind_lex

def main():
    dic1 = upload_pt()
    l = Lexicon("http://lari-datasets.ilc.cnr.it/chamuca_pt_lex#", dic1)
    l.writeToFile('chamuca_pt_lex')
    dic2 = upload_hl("SimplifiedHindi.tsv")
    l2 = Lexicon("http://lari-datasets.ilc.cnr.it/chamuca_hi_lex#", dic2)
    l2.writeToFile('chamuca_hi_lex')
    dic3 = upload_ur("SimpleUrdu.tsv")
    l3 = Lexicon("http://lari-datasets.ilc.cnr.it/chamuca_ur_lex#", dic3)
    l3.writeToFile('chamuca_ur_lex')

if __name__ == "__main__":
        main()
