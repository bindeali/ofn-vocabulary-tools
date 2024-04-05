import sys
import rdflib
from lxml import etree
from enum import Enum

# TODO: Vocabularies (low priority)
# TODO: RDF conversion
# TODO: Write to file


# inputLocation = sys.argv[1]
# outputLocation = sys.argv[2]
inputLocation = "Slovníky-Archi.xml"
outputName = "Slovník"

TermType = Enum("TermType", ['TERM', 'CLASS',
                'RELATIONSHIP', 'TROPE', 'SUBJECT', 'OBJECT'])

ARCHIMATE_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

propertyDefinitions = {}
terms = []


class Term:
    def __init__(self) -> None:
        self.id = ""
        self.type = TermType.TERM
        self.name = {}
        self.description = {}
        self.definition = {}
        self.source = ""
        self.domain = ""
        self.range = ""
        self.datatype = ""
        self.subClassOf = []
        self.tropes = []


class Vocabulary:
    def __init__(self) -> None:
        self.name = {}
        self.description = {}
        self.terms = []


vocabulary = Vocabulary()
vocabulary.name = outputName

# XML parsing

with open(inputLocation, "r", encoding="utf-8") as inputFile:
    tree = etree.parse(inputLocation)
    root = tree.getroot()
    properties = root.findall(
        ".//{http://www.opengroup.org/xsd/archimate/3.0/}propertyDefinition[@identifier]")
    elements = root.findall(
        ".//{http://www.opengroup.org/xsd/archimate/3.0/}element[@{http://www.w3.org/2001/XMLSchema-instance}type]")
    relationships = root.findall(
        ".//{http://www.opengroup.org/xsd/archimate/3.0/}relationship[@{http://www.w3.org/2001/XMLSchema-instance}type]")
    for property in properties:
        name = property.find(
            ".//{http://www.opengroup.org/xsd/archimate/3.0/}name")
        propertyDefinitions[property.attrib['identifier']
                            ] = getattr(name, "text", "name")
    for element in elements:
        if element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == "DataObject":
            term = Term()
            term.id = element.attrib['identifier']
            # Name
            names = element.findall(
                "{http://www.opengroup.org/xsd/archimate/3.0/}name")
            for name in names:
                lang = name.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                term.name[lang] = name.text
            # Properties
            termProperties = element.findall(
                "{http://www.opengroup.org/xsd/archimate/3.0/}property")
            for termProperty in termProperties:
                identifier = termProperty.attrib['propertyDefinitionRef']
                value = termProperty.find(property.find(
                    ".//{http://www.opengroup.org/xsd/archimate/3.0/}value"))
                valueLang = value.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                valueText = value.text
                propertyType = propertyDefinitions[identifier]
                match propertyType:
                    # Type
                    case "typ":
                        valueTextNormalized = valueText.strip().lower()
                        match valueTextNormalized:
                            case "typ subjektu":
                                term.type = TermType.SUBJECT
                            case "typ objektu":
                                term.type = TermType.OBJECT
                            case "typ vlastnosti":
                                term.type = TermType.TROPE
                    # Source
                    case "zdroj":
                        term.source = valueText
                    # Definition
                    case "definice":
                        term.definition[valueLang] = valueText
                    # Description
                    case "popis":
                        term.description[valueLang] = valueText
            for name in names:
                lang = name.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                term.name[lang] = name.text

    for relationship in relationships:
        identifier = relationship.attrib['identifier']
        source = relationship.attrib['source']
        target = relationship.attrib['target']
        sourceTerm = next((x for x in terms if x.id == source), None)
        targetTerm = next((x for x in terms if x.id == target), None)
        if sourceTerm is None or targetTerm is None:
            continue
        if element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == "Specialization":
            sourceTerm.subClassOf.append(targetTerm)
        elif element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == "Composition":
            sourceTerm.tropes.append(targetTerm)
        elif element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == "Association":
            term = Term()
            term.type = TermType.RELATIONSHIP
            term.id = element.attrib['identifier']
            term.source = source
            term.target = target
            # Name
            names = element.findall(
                "{http://www.opengroup.org/xsd/archimate/3.0/}name")
            for name in names:
                lang = name.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                term.name[lang] = name.text
            # Properties
            termProperties = element.findall(
                "{http://www.opengroup.org/xsd/archimate/3.0/}property")
            for termProperty in termProperties:
                identifier = termProperty.attrib['propertyDefinitionRef']
                value = termProperty.find(property.find(
                    ".//{http://www.opengroup.org/xsd/archimate/3.0/}value"))
                valueLang = value.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                valueText = value.text
                propertyType = propertyDefinitions[identifier]
                match propertyType:
                    # Not interested in type
                    # Source
                    case "zdroj":
                        term.source = valueText
                    # Definition
                    case "definice":
                        term.definition[valueLang] = valueText
                    # Description
                    case "popis":
                        term.description[valueLang] = valueText
            for name in names:
                lang = name.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                term.name[lang] = name.text

# RDF conversion
# graph = rdflib.Graph()

# Vocabulary


# File output

# with open("{}_OFN_Slovník.ttl".format(vocabulary.name), "w") as outputFile:
# pass
