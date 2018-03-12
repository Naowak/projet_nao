import re
from multi_key_dict import multi_key_dict

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
numbers_vocab = multi_key_dict({\
    ("1","un","une"): 1,\
    ("2","de","deux"): 2,\
    ("3","trois","troie"): 3,\
    ("4","quatre"): 4,\
    ("5","cinq"): 5,\
    ("6","six"): 6,\
    ("7","sept"): 7,\
    ("8","huit"): 8,\
    ("9","neuf"): 9,\
    ("10","dix"): 10})

colors_vocab =multi_key_dict({\
    ("rose","violet","mauve","magenta","fuchsia"): "Fuchsia",\
    ("vert","kaki"):"Green",\
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
    "valide": True})

#print(multi_key_dict({**numbers_vocab.items_dict, **colors_vocab.items_dict}))
union =lambda x, y: multi_key_dict({**x.items_dict, **y.items_dict})

rule_piece = [\
            [r".*?(\w+) pièces?.*?",ordinals_vocab],\
            [r".*?pièces? (\w+).*?", union(numbers_vocab,colors_vocab)],\
            [r".*?pièces? (\w+ \w+).*?", colors_vocab],\
            [r".*?ps([0-9]).*?",numbers_vocab]\
            ]
rule_colonne = [\
            [r".*?colonnes? (\w+)",numbers_vocab],\
            [r".*?(\w+) colonnes?.*?",union(numbers_vocab,ordinals_vocab)]\
            ]
rule_direction = [\
            [r".*?(:?vers la|à) (\w+).*?", directions_vocab]
            ]   
rule_rotate = [\
            [r".*?(?: tourn(?:é|ée|és|ez|er) .* (\w+) fois).*?",numbers_vocab]\
            ]
rule_valid = [\
            [r".*?(\w+)$", valid_vocab]
            ]

def apply_basic_rule(rule,sentence):
    for [regex,vocab] in rule:
        match = re.findall(regex, sentence)
        #print((regex,match))
        if match and match[0] in vocab:
            return vocab[match[0]]
    #print("No match")
    return
