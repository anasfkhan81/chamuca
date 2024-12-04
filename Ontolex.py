#!/usr/bin/env python
# -*- coding: utf-8 -*-
#this part (line above) is not important for handling encoding in input output; just to use utf in your code


# import unidecode
# import codecs
import rdflib
from rdflib import URIRef, BNode, Literal, Graph, Namespace
from rdflib.namespace import RDF, RDFS, FOAF, Namespace, NamespaceManager, OWL, XSD, SKOS, DC, DCTERMS, DCAT

ontolex_uri= "http://www.w3.org/ns/lemon/ontolex#"
lexinfo_uri = "http://www.lexinfo.net/ontology/2.0/lexinfo#"
lime_uri = "http://www.w3.org/ns/lemon/lime#"
gold_uri = "http://linguistics-ontology.org/gold/2010/"
decomp_uri = "http://www.w3.org/ns/lemon/decomp#"
frac_uri = "http://www.w3.org/ns/lemon/frac#"
cito_uri = "http://purl.org/spar/cito"
fabio_uri = "http://purl.org/spar/fabio/"
ontolex_ns = Namespace(ontolex_uri)
lexinfo_ns = Namespace(lexinfo_uri)
lime_ns = Namespace(lime_uri)
gold_ns = Namespace(gold_uri)
decomp_ns =  Namespace(decomp_uri)
cito_ns =  Namespace(cito_uri)
fabio_ns =Namespace(fabio_uri)
frac_ns = Namespace(frac_uri)


lex = {'name':'hindi_lex','lang':['hi'],'entries':	{'अगस्त_entry': {'entry_type':'Word','pos':'commonNoun', 'gender':'masculine', 'form': [{'id':'अगस्त_lemma','rep': [('अगस्त', 'hi-deva')], 'lemma':True}],  'sense': [{'id': 'अगस्त_1', 'def': 'August'}]}, 'काजू_entry': {'entry_type':'Word','pos':'commonNoun', 'form': [{'id':'काजू_lemma','rep': [('काजू', 'hi-deva')], 'lemma':True}], 'sense': [{'id': 'sense_काजू_1', 'def': 'cashew nut'}]}}}



class Lexicon():
    # Defines a class lexicon that given a python dictionary of the appropriate form creates an ontolex-lemon lexicon

    def __init__(self, namespace, indic, extraname={}):
        # name is the string name of the lexicon
        # namespace is a string with the namespace of the lexicon
        # indic is a dictionary containing the content of the lexicon
        # extraname is a dictionary with extra namespaces

        self.indic = indic
        self.name = indic['name']
        self.namespace = namespace

        # Here we handle the namespace information for the lexicon

        this = URIRef(namespace)
        BASE = Namespace(namespace)

        namespace_manager = NamespaceManager(Graph())
        namespace_manager.bind('ontolex', ontolex_ns, override=False)
        namespace_manager.bind('lime', lime_ns, override=False)
        namespace_manager.bind('lexinfo', lexinfo_ns, override=False)
        namespace_manager.bind('gold', gold_ns, override=False)
        namespace_manager.bind('owl', OWL, override=False)
        namespace_manager.bind('skos', SKOS, override=False)
        namespace_manager.bind('decomp', decomp_ns, override=False)
        namespace_manager.bind('cito', cito_ns, override=False)
        namespace_manager.bind('fabio', fabio_ns, override=False)
        namespace_manager.bind('frac', frac_ns, override=False)
        namespace_manager.bind('', BASE, override=False)
        namespace_manager.bind('dct', DCTERMS, override=False)
        namespace_manager.bind('dc', DC, override=False)

        # Create lexicon graph
        self.lex = Graph()
        self.lex.namespace_manager = namespace_manager

        # Define lexicon and add metadata
        self.lex.add((this, RDF.type, lime_ns.Lexicon))
        # add the description of the dataset given in indic['desc']
        if 'desc' in indic.keys():
            self.lex.add((this, DC.description, Literal(indic['desc'])))

        # The languages of the lexicon are added
        for l in indic['lang']:
            lang = Literal(l)
            self.lex.add((this, lime_ns.language, lang))

        # Create lexical entries for each entry in the dictionary

        for e in indic['entries']:
            self.addLexicalEntry(e)

    def addPartOfSpeech(self, keys, entity, subj):
        if 'pos' in keys:
            pos = entity['pos']
            if pos != '':
                self.lex.add((subj, lexinfo_ns.partOfSpeech, URIRef(lexinfo_uri + pos)))

    def addGender(self, keys, entity, subj):
        if 'gender' in keys:
            gen = entity['gender']
            if gen != '':
                self.lex.add((subj, lexinfo_ns.gender, URIRef(lexinfo_uri + gen)))

    def addCase(self, keys, entity, subj):
        if 'case' in keys:
            case = entity['case']
            if case != '':
                self.lex.add((subj, lexinfo_ns.case, URIRef(lexinfo_uri + case)))

    def addNumber(self, keys, entity, subj):
        
        if 'number' in keys:
            num = entity['number']
            if num != '':
                self.lex.add((subj, lexinfo_ns.number, URIRef(lexinfo_uri + num)))

    def addEtyRoot(self, keys, entity, subj):
        if 'etymon' in keys:
            etym = entity['etymon']
            new_url = etym.replace(' ', '_')
            if etym != '':
                self.lex.add((subj, lexinfo_ns.etymologicalRoot, URIRef(new_url)))


    def addEty(self, keys, entity, subj):
        if 'etymology' in keys:
            etymy = entity['etymology']
            if etymy != '':
                self.lex.add((subj, lexinfo_ns.etymology, Literal(etymy)))

                
    def addSeeAlso(self, keys, entity, subj):
        if 'seeAlso' in keys:
            see_url = entity['seeAlso']
            if see_url[-2:]!='NA':
                print(see_url[-2:])
                self.lex.add((subj, RDFS.seeAlso, URIRef(see_url)))

            
    def addForms(self, entry, ent):

        for f in entry['form']:

            form = URIRef(self.namespace + f['id'])

            form_keys = list(f.keys())

            # Add the form as an individual of type ontolex Form
            self.lex.add((form, RDF.type, ontolex_ns.Form))

            # Relate the form together using the appropriate property writtenRep
            i = 0
            for forms in f['rep']:
                print(str((forms[1])))
                self.lex.add((form, ontolex_ns.writtenRep, Literal(forms[0], lang=forms[1])))
                
            # Check if it is a lemma or not
            if f['lemma']:
                self.lex.add((ent, ontolex_ns.canonicalForm, form))
                if 'ipa' in f.keys():
                    for ipa in f['ipa']:
                        self.lex.add((form, ontolex_ns.phoneticRep, Literal(ipa, lang=f"hi-fonipa")))
            else:
                self.lex.add((ent, ontolex_ns.lexicalForm, form))

            # Check gender

            self.addGender(form_keys, f, form)

            # Check Case
            self.addCase(form_keys, f, form)

            # Check Number
            self.addNumber(form_keys, f, form)

            # Check Mood


    def addSenses(self, entry, ent):

        for s in entry['sense']:
            # Create the sense URI based on the sense id which has been passed through the dictionary
            sense = URIRef(self.namespace + s['id'])

            # Add the sense as an individual of type ontolex sense
            self.lex.add((sense, RDF.type, ontolex_ns.LexicalSense))

            # Relate the sense together using the appropriate property  sense
            self.lex.add((ent, ontolex_ns.sense, sense))
            self.lex.add((sense, ontolex_ns.isSenseOf, ent))

            # Add a definition
            self.lex.add((sense, SKOS.definition, Literal(s['def'])))



    def addLexicalEntry(self, lemma_id):
        # adds a lexical entry to the lexicon, with the id lemma_id and information from entry
        ent = URIRef(self.namespace + lemma_id)
        self.lex.add((ent, RDF.type, ontolex_ns.LexicalEntry))

        # check which entry type it is word, multiword entry, etc
        entry_type = self.indic['entries'][lemma_id]['entry_type']
        self.lex.add((ent, RDF.type, URIRef(ontolex_uri + entry_type)))

        entry_keys = list(self.indic['entries'][lemma_id].keys())

        # add part of speech
        self.addPartOfSpeech(entry_keys, self.indic['entries'][lemma_id], ent)

        # add gender
        self.addGender(entry_keys, self.indic['entries'][lemma_id], ent)

        # add forms
        self.addForms(self.indic['entries'][lemma_id], ent)

        # add senses
        self.addSenses(self.indic['entries'][lemma_id], ent)

        #add etymological root
        #need to make this roots, just root for now
        self.addEtyRoot(entry_keys, self.indic['entries'][lemma_id], ent)

        self.addEty(entry_keys, self.indic['entries'][lemma_id], ent)

        # add related entries
        self.addSeeAlso(entry_keys, self.indic['entries'][lemma_id], ent)      

        # add other stuff

    def writeToFile(self, filename, s_format='turtle'):
        new_filename = filename + '.rdf'
        self.lex.serialize(destination=new_filename, format=s_format)

        # g = open(filename+'.rdf','w')
        # g.write(self.lex.serialize(format='turtle'))
        # g.close()

    def addMorphInfo(self, keys, entry, name, ent):
        # stem
        if 'stem' in keys:
            stem = URIRef(self.namespace + name + "_stem")
            self.lex.add((stem, RDF.type, gold_ns.Stem))
            self.lex.add((stem, gold_ns.writtenRealization, Literal(entry['stem'], lang="xfa")))


    def addLexicalEntry(self, lemma_id):
        # adds a lexical entry to the lexicon, with the id lemma_id and information from entry
        ent = URIRef(self.namespace + lemma_id)
        self.lex.add((ent, RDF.type, ontolex_ns.LexicalEntry))

        # check which entry type it is word, multiword entry, etc
        entry_type = self.indic['entries'][lemma_id]['entry_type']
        self.lex.add((ent, RDF.type, URIRef(ontolex_uri + entry_type)))

        entry_keys = list(self.indic['entries'][lemma_id].keys())

        # add part of speech
        self.addPartOfSpeech(entry_keys, self.indic['entries'][lemma_id], ent)

        # add gender
        self.addGender(entry_keys, self.indic['entries'][lemma_id], ent)

        # add forms
        self.addForms(self.indic['entries'][lemma_id], ent)

        # add senses
        self.addSenses(self.indic['entries'][lemma_id], ent)

	# add etyRoot
        self.addEtyRoot(entry_keys, self.indic['entries'][lemma_id], ent)

        self.addEty(entry_keys, self.indic['entries'][lemma_id], ent)

        # add related entries
        self.addSeeAlso(entry_keys, self.indic['entries'][lemma_id], ent)

        self.addMorphInfo(entry_keys, self.indic['entries'][lemma_id], lemma_id, ent)

        # add other stuff

