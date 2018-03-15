import re
from multi_key_dict import multi_key_dict

["Place la pièce 2 dans la deuxième collone",\
"Tourne la pièce rouge deux fois vers la droite",\
"Mets le carré rose en bas",\
"Décale-la de deux colonnes",\
"Décale-la dans la colonne trois",\
"Décale la pièce deux colonnes à droite",\
"Termine mon tour",\
"Décale la vers la droite de deux colonnes"]

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
    ("carré","bloc","o","haut","eau"): 'O',\
    ("barre", "bâton", "i"): 'I',
    ("thé","t"): 'T',\
    ("l", "elle","lambda"): 'L',\
    ("j", "l inversé","gamma"): 'J',\
    ("z","biais"): 'Z',\
    ("s", "z inversé", "biais inversé"): 'S'})

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
