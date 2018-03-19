import re
from multi_key_dict import multi_key_dict
# from nltk.parse import generate
# from nltk import load_parser
import arpeggio as peg
from arpeggio.cleanpeg import ParserPEG
from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF
from sys import argv

["Place la pièce 2 dans la deuxième colonne",\
"Tourne la pièce rouge deux fois vers la droite",\
"Mets le carré rose en bas",\
"Décale-la de deux colonnes",\
"Décale-la dans la colonne trois",\
"Décale la pièce deux colonnes à droite",\
"Termine mon tour",\
"Décale la vers la droite de deux colonnes"]

def direction(): return Optional(["vers la ","à "]),["droite","gauche"]

def valider(): return peg.RegExMatch(r"(?:valid(?:ez|é|er|e)|en bas)")
def num_piece(): return ["un","deux","trois","1","2","3","une","de","troie"]
def num_colonne(): return peg.RegExMatch(r"(?:\d|10|dix|\
    un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|troie|de)")

def ordinaux(): return peg.RegExMatch(
    r"(?:\de|10e|1ère|\
    première|deuxième|troisième|quatrième|cinquième|sixième|septième|huitième|neuvième|dixième)")

def verbe(): return peg.RegExMatch(
    r"(?:(?:(?:décal|pos|termin|plac)(?:er|ez|é|e))|(?:chosi(?:s|r|e|ssez))|(?:met(?:s|ttez|tre)))(?:(?: |-)(?:la|le)| une| un)")

def reg_o() : return ["carré","bloc","o","haut","eau"]
def reg_i() : return["barre","bâton","i"]
def reg_t() : return["thé","t"]
def reg_l() : return["elle","lambda","l"]
def reg_j() : return["j","gamma"]
def reg_z() : return["z","biais"]
def reg_s() : return["z inversé","biais inversé"]

def forme(): return Optional(["en forme de "]),[reg_o,reg_i,reg_j,reg_l,reg_s,reg_t,reg_z]

def fuschia() : return ["rose","violet","mauve","magenta","fuschia","lila","violette"]
def green(): return ["verte" ,"kaki","vert"]
def yellow(): return "jaune"
def blue(): return ["bleu foncé","bleu"]
def aqua(): return ["ciel","bleu clair","bleu cyan","cyan","turquoise","bleu turquoise"]
def red(): return ["rouge"]
def orange(): return ["orange"]

def color(): return Optional(["de couleur "]),[yellow, fuschia, green, aqua, blue, red, orange]

def select_piece(): return [("pièce", peg.Not([color,num_piece])),
                            ("pièce", [num_piece, (forme, color), (color, forme), color, forme]),
                            (forme, Optional([color]))]

def select_column(): return [("dans la", [(ordinaux, "colonne"), ("colonne", num_colonne)]),
                            (Optional(["de "]), num_colonne, ["colonnes", "colonne"], direction),
                            (direction, Optional(["de"]), num_colonne, ["colonnes", "colonne"])
                            ]

def action(): return verbe, [(select_piece,select_column),
                            (select_column,select_piece),
                            select_column,
                            select_piece],Optional(valider)

def mainrule(): return action, peg.EOF

parser= peg.ParserPython(mainrule,debug=True)
try:
    parse_tree = parser.parse(argv[1])
except peg.NoMatch as e:
    print(e)

class Visit(peg.PTNodeVisitor):
    def visit_ordinaux(self, node, children):
        return node.value 

    def visit_direction(self, node, children):
        return node.value
    
    def visit_action(self, node, children):
        return node.value

result = peg.visit_parse_tree(parse_tree,Visit(debug=True))
print("result",result)
# nom_fichier = "gr_play.fcfg"
# #grammaire = load(nom_fichier)
# parser = load_parser(nom_fichier)

# arbre = parser.parse("Place la pièce 2".lower().split())

# for arbre in arbre:
# 	print(arbre)

# interpretation = arbre.label()

# for element in interpretation:
# 	print(element)
# 	print(interpretation[element])


def union(x, y): return multi_key_dict({**x.items_dict, **y.items_dict})
ordinals_vocab = multi_key_dict({\
    ("première","1er"): 1,\
    ("deuxième","2e"): 2,\
    ("troisième","3e"): 3,\
    ("quatrième","4e"): 4,\
    ("cinquième","5e"): 5,\
    ("sixième","6e"): 6,\
    ("septième","7e"): 7,\
    ("huitième","8e"): 8,\
    ("neuvième","9e"): 9,\
    ("dixième","10e"): 10})

shape_vocab = multi_key_dict({
    ("carré","bloc","o","haut","eau"): "O",\
    ("barre", "bâton", "i"): "I",
    ("thé","t"): "T",\
    ("l", "elle","lambda"): "L",\
    ("j", "l inversé","gamma"): "J",\
    ("z","biais"): "Z",\
    ("s", "z inversé", "biais inversé"): "S"})

index_piece_vocab = multi_key_dict({
    ("1", "un", "une"): 1,\
    ("2", "de", "deux"): 2,\
    ("3", "trois", "troie"): 3})

index_column_vocab = union(index_piece_vocab,multi_key_dict({
    ("4","quatre"): 4,\
    ("5","cinq"): 5,\
    ("6","six"): 6,\
    ("7","sept"): 7,\
    ("8","huit"): 8,\
    ("9","neuf"): 9,\
    ("10","dix"): 10}))

colors_vocab =multi_key_dict({
    ("rose","violet","mauve","magenta","fuchsia","lila","violette"): "Fuchsia",\
    ("verte","kaki","verte"):"Green",\
    "jaune": "Yellow",\
    ("bleu foncé","bleu"):"Blue",\
    ("bleu ciel","bleu clair","bleu cyan","cyan","turquoise","bleu turquoise"):"Aqua",\
    "rouge": "Red",\
    "orange": "Orange"})

directions_vocab = multi_key_dict({
    "gauche":1,\
    "droite":-1})

valid_vocab = multi_key_dict({
    "valider": True,\
    "validé": True,
    "en bas": True})

#print(multi_key_dict({**numbers_vocab.items_dict, **colors_vocab.items_dict}))


rule_piece = [\
            [r".*?(\w+) pièces?.*?",ordinals_vocab],\
            [r".*?pièces? (\w+).*?", union(index_piece_vocab,colors_vocab)],\
            [r".*?pièces? (\w+ \w+).*?", colors_vocab],\
            [r".*?ps([0-9]).*?",index_piece_vocab]\
            ]
rule_colonne = [\
            [r".*?colonnes? (\w+)",index_column_vocab],\
            [r".*?(\w+) colonnes?.*?",union(index_column_vocab,ordinals_vocab)]\
            ]
rule_direction = [\
            [r".*?(?: vers la|à) (\w+).*?", directions_vocab]
            ]   
rule_rotate = [\
            [r".*?(?: tourn(?:é|ée|és|ez|er) .* (\w+) fois).*?", index_column_vocab]
            ]
rule_valid = [\
            [r".*?(\w+)$", valid_vocab],\
            [r".*?(\w+ \w+)$", valid_vocab]
            ]

def apply_basic_rule(rule,sentence):
    for [regex,vocab] in rule:
        match = re.findall(regex, sentence)
        #print((regex,match))
        if match and match[0] in vocab:
            return vocab[match[0]]
    #print("No match")
    return
