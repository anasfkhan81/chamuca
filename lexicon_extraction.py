import pandas as pd
import re
from Ontolex import Lexicon

hind_lex ={'name':'chamuca_hi_lex', 'desc':'Lexical information derived in part from wiktionary, https://www.wiktionary.org', 'lang':['hi'], 'entries': {}}
port_lex = {'name':'chamuca_port_lex', 'desc':'Lexical information derived in part from wiktionary, https://www.wiktionary.org', 'lang':['pt'], 'entries': {}}
gend = lambda g: 'masculine' if g == 'm.' else 'feminine' if g == 'f.' else 'unknown'
pos = lambda ps: 'commonNoun' if ps == 'noun' else 'properNoun' if ps == 'proper noun' else 'nan'
lemma = lambda head, trans, ipa: {'rep':[(head, "hi-deva"), (trans, "hi-Latn")], 'lemma':True, 'id': head+'_lemma', 'number':'singular', 'case':'directCase', 'ipa':ipa}
lemma_mi = lambda head, trans : {'rep':[(head, "hi-deva"), (trans, "hi-Latn")], 'lemma':True, 'id': head+'_lemma', 'number':'singular', 'case':'directCase'}
obl_sing = lambda form,lemm: {'rep':[(form, "hi-deva")], "lemma":False, 'id': form +'_os_form_'+lemm, 'number':'singular', 'case':'obliqueCase'}
voc_sing = lambda form,lemm: {'rep':[(form, "hi-deva")], "lemma":False, 'id': form+'_vs_form_'+lemm,'number':'singular', 'case':'vocativeCase'}
dir_plu = lambda form,lemm: {'rep':[(form, "hi-deva")], "lemma":False, 'id': form+'_dp_form_'+lemm, 'number':'plural', 'case':'directCase'}
obl_plu = lambda form,lemm: {'rep':[(form, "hi-deva")], "lemma":False, 'id': form+'_op_form_'+lemm, 'number':'plural', 'case':'obliqueCase'}
voc_plu = lambda form,lemm: {'rep':[(form, "hi-deva")], "lemma":False, 'id': form+'_vp_form_'+lemm,'number':'plural', 'case':'vocativeCase'}

posp = lambda ps: 'commonNoun' if ps== 'Noun' else ps
genp = lambda g: 'masculine' if g == 'Masculine' else 'feminine' if g == 'Feminine' else 'unknown'

urdu = lambda ur: ur if isinstance(ur, str) else 'NA'


def extract_ipas(input_string):
    # Regular expression pattern to match substrings between '/'
    pattern = r'/(?P<substring>.*?)\/'
    
    # Find all matches using regular expression
    matches = re.findall(pattern, input_string)
    
    # Return the list of matched substrings
    return matches

def extract_hind_senses(input_string):
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
        lemma = row['Lemma']
        word_id = lemma +'_entry'
        gr = genp(row['Grammatical Gender'])
        pos = posp(row['Part of Speech'])
        formstrings = [substring.strip() for substring in row['Singular and Plural'].split(',')]
        forms_1 = {'rep':[(lemma, "pt")], 'lemma':True, 'id':lemma+'_lemma', 'number':'singular'}
        if len(formstrings)==2: 
            forms_2 = {'rep':[(formstrings[1], "pt")], 'lemma':False, 'id':lemma+'_plural', 'number':'plural'}
            forms = [forms_1, forms_2]
        else:
            print('strange '+lemma)
            forms = [forms_1]
    
        if senseIndex[0] == lemma:
            port_lex['entries'][word_id]['sense'] = port_lex['entries'][word_id]['sense']+[{'id': lemma+'_sense_'+str(senseIndex[1]), 'def':row['definition']}]
            senseIndex = (lemma, senseIndex[1]+1)
        else:
            senseContent = [{'id': lemma+'_sense_1', 'def':row['definition']}]
            port_lex['entries'][word_id] = {'gender':gr, 'entry_type':'Word', 'pos': pos, 'sense':senseContent, 'form':forms}
            senseIndex = (lemma, 2)
        
    return port_lex

    

def upload_hl():
    df = pd.read_csv("LessSimpleHindi.tsv", sep='\t')
    i = 0
    for index, row in df.iterrows():
        if i == 60:
            break
        word_id = row['Headword']+'_entry'
        gr = gend(row['Gender'])
        ipa_row = row['Pronunciation']
        ipas = []
        lemmaForm = row['Headword']
        if isinstance(ipa_row, str):
            ipas = extract_ipas(row['Pronunciation'])
            #print(str(ipas))
            ipa_lemma = ['']
            if ipas != []:
                ipa_lemma = ipas
            forms =  [lemma(row['Headword'], row['Transliteration'], ipa_lemma)]
        else:
            forms =  [lemma_mi(row['Headword'], row['Transliteration'])]
        senses = extract_hind_senses(row['Sense (Wiktionary)'])
        sense_content = []
        j = 1
        if len(senses) == 1:
            sense_content = [{'id': row['Headword']+'_sense', 'def':senses[0]}]
        else:
            for count in senses:
                print(row['Headword']+'_sense_'+str(j))
                sense_content = sense_content + [{'id': row['Headword']+'_sense_'+str(j), 'def':count}]
                j +=1
            
#        sense_content = [{'id': row['Headword']+'_sense', 'def':row['Sense (Wiktionary)']}]
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
            
 #           forms = forms + [obl_sing(row['oblique singular']), voc_sing(row['vocative singular']), dir_plu(row['direct plural']), obl_plu(row['oblique plural']), voc_plu(row['vocative plural']) ]
        else:
            print(row['Headword'])
        urdu_seeAlso = "http://lari-datasets.ilc.cnr.it/chamuca_ur_lex#"+urdu(row['Urdu ']).replace(' ', '')
        print(urdu_seeAlso)
        porEtymon = "http://lari-datasets.ilc.cnr.it/chamuca_pt_lex#"+row['Etymon pt-PT'] 
        hind_lex['entries'][word_id] = {'gender':gr, 'entry_type':'Word', 'pos':pos(row['Part of Speech']), 'form':forms, 'sense':sense_content, 'seeAlso':urdu_seeAlso, 'etymon':porEtymon}
        i+=1
    return hind_lex

def main():
    dic1 = upload_pt()
    l = Lexicon("http://lari-datasets.ilc.cnr.it/chamuca_pt_lex#", dic1)
    l.writeToFile('chamuca_pt_lex')
    dic2 = upload_hl()
    l2 = Lexicon("http://lari-datasets.ilc.cnr.it/chamuca_hi_lex#", dic2)
    l2.writeToFile('chamuca_hi_lex')

if __name__ == "__main__":
        main()
