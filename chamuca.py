import rdflib
from rdflib import URIRef, BNode, Literal, Graph, Namespace
from rdflib.namespace import RDF, RDFS, FOAF, Namespace, NamespaceManager, OWL, XSD, SKOS, DC, DCTERMS, DCAT



base_uri = "http://lari-datasets.ilc.cnr.it/chamuca_lexical_resource#"
hindi = "http://lari-datasets.ilc.cnr.it/chamuca_hindi_lex#"
urdu = "http://lari-datasets.ilc.cnr.it/chamuca_urdu_lex#"
pt = "http://lari-datasets.ilc.cnr.it/chamuca_pt_lex#"
hindi_ns = Namespace(hindi)
urdu_ns = Namespace(urdu)
pt_ns = Namespace(pt)

def main():



    this = URIRef(base_uri)
    BASE = Namespace(this)

    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind('', BASE, override=False)
    namespace_manager.bind('hindi_lex', hindi_ns, override=False)
    namespace_manager.bind('urdu_lex', urdu_ns, override=False)
    namespace_manager.bind('pt_lex', pt_ns, override=False)
    namespace_manager.bind('dct', DCTERMS, override=False)
    namespace_manager.bind('dc', DC, override=False)
    namespace_manager.bind('dcat', DCAT, override=False)

    chamuca_resource = Graph()
    chamuca_resource.namespace_manager = namespace_manager

    chamuca_resource.add((this, RDF.type, DCAT.dataset))
    chamuca_resource.add((this, DCTERMS.title, Literal("chamuça", lang= "eng")))
    chamuca_resource.add((this, DCTERMS.language, Literal("hi")))
    chamuca_resource.add((this, DCTERMS.language, Literal("pt")))
    chamuca_resource.add((this, DCTERMS.language, Literal("ur")))
    chamuca_resource.add((this, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    chamuca_resource.add((this, DCTERMS.hasPart, URIRef(hindi)))
    chamuca_resource.add((this, DCTERMS.hasPart, URIRef(urdu)))
    chamuca_resource.add((this, DCTERMS.hasPart, URIRef(pt)))

    chamuca_resource.serialize(destination="chamuca_lexical_resource.rdf", format='xml')


if __name__ == "__main__":
        main()
