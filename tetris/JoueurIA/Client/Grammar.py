import re
from multi_key_dict import multi_key_dict
# from nltk.parse import generate
# from nltk import load_parser
import arpeggio as peg
from arpeggio.cleanpeg import ParserPEG
from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF
from sys import argv
from math import *

["Place la pièce 2 dans la deuxième colonne",\
"Tourne la pièce rouge deux fois vers la droite",\
"Mets le carré rose en bas",\
"Décale-la de deux colonnes",\
"Décale-la dans la colonne trois",\
"Décale la pièce deux colonnes à droite",\
"Termine mon tour",\
"Décale la vers la droite de deux colonnes"]


def union(x, y): return multi_key_dict({**x.items_dict, **y.items_dict})
ordinals_vocab = multi_key_dict({
    ("première", "1er"): 1,
    ("deuxième", "2e"): 2,
    ("troisième", "3e"): 3,
    ("quatrième", "4e"): 4,
    ("cinquième", "5e"): 5,
    ("sixième", "6e"): 6,
    ("septième", "7e"): 7,
    ("huitième", "8e"): 8,
    ("neuvième", "9e"): 9,
    ("dixième", "10e"): 10})
index_piece_vocab = multi_key_dict({
    ("1", "un", "une"): 1,
    ("2", "de", "deux"): 2,
    ("3", "trois", "troie"): 3})
index_column_vocab = union(index_piece_vocab, multi_key_dict({
    ("4", "quatre"): 4,
    ("5", "cinq"): 5,
    ("6", "six"): 6,
    ("7", "sept"): 7,
    ("8", "huit"): 8,
    ("9", "neuf"): 9,
    ("10", "dix"): 10}))

def direction(): return Optional(["vers la ","à "]),["droite","gauche"]

def valid(): return peg.RegExMatch(r"(?:valid(?:ez|é|er|e)|en bas)")
def num_piece(): return ["un","deux","trois","1","2","3","une","de","troie"]
def num_column(): return peg.RegExMatch(r"(?:\d|10|dix|\
    un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|troie|de)")

def ordinaux(): return peg.RegExMatch(
    r"(?:\de|10e|1ère|\
    première|deuxième|troisième|quatrième|cinquième|sixième|septième|huitième|neuvième|dixième)")

def verb(): return peg.RegExMatch(
    r"(?:(?:(?:décal|pos|termin|plac|sélectionn)(?:er|ez|é|e))|(?:choisi(?:s|r|e|ssez))|(?:met(?:s|ttez|tre)))(?:(?: |-)(?:la|le)| une| un)")

def turn(): return peg.RegExMatch(
	r"(?:(?:(tourn)(?:er|ez|é|e))(?:(?: |-)(?:la|le))?)")

def reg_o() : return ["carré","bloc","o","haut","eau"]
def reg_i() : return["barre","bâton","i"]
def reg_t() : return["thé","t"]
def reg_l() : return["elle","lambda","l"]
def reg_j() : return["j","gamma"]
def reg_z() : return["z","biais"]
def reg_s() : return["z inversé","biais inversé"]

def shape(): return Optional(["en forme de "]),[reg_o,reg_i,reg_j,reg_l,reg_s,reg_t,reg_z]

def fuchsia() : return ["rose","violet","mauve","magenta","fuchsia","lila","violette"]
def green(): return ["verte" ,"kaki","vert"]
def yellow(): return "jaune"
def blue(): return ["bleue foncé","bleu foncé","bleue","bleu"]


def aqua(): return ["ciel", "bleue claire", "bleue clair", "bleue cyan", "cyan", "turquoise",
                    "bleue turquoise","bleu claire", "bleu clair", "bleu cyan", "bleu turquoise","bleue ciel","bleu ciel"]
def red(): return ["rouge"]
def orange(): return ["orange"]

def color(): return Optional(["de couleur "]),[yellow, fuchsia, green, aqua, blue, red, orange]

def select_piece(): return [("pièce", peg.Not([color, num_column, shape])),
                            ("pièce", peg.And( num_column, ["colonnes", "colonne"] )),
                            ("pièce", [num_piece, (shape, color), (color, shape), color, shape]),
                            (shape, Optional([color]))]

def select_column(): return [("dans la", [(ordinaux, "colonne"), ("colonne", num_column)]),
                            (Optional(["de "]), num_column, ["colonnes", "colonne"], direction),
                            (direction, Optional(["de"]), num_column, ["colonnes", "colonne"])
                            ]

def select_turn(): return turn, ((Optional(select_piece), Optional(num_column, "fois"), Optional(direction)))

def action(): return [(Optional((verb, [(select_piece,select_column),
                            (select_column,select_piece),
                            select_column,
                            select_piece]))),
                        (select_turn)],Optional(valid)

def mainrule(): return action, peg.EOF

def filter_dict(l): 
    return dict(elem.popitem() for elem in l if type(elem) is dict)


class ShapeAndColorNotMatchException(Exception):
    pass

class HorMoveException(Exception):
    pass

class UnvalaibleChooseException(Exception):
    pass

class Visit(peg.PTNodeVisitor):
    def __init__(self, debug, colors=None, state=None):
        super().__init__(debug)
        if state is not None and colors is not None:
            self.colors = colors
            self.pieces = state["pieces"]
            self.current_abscisse = state["actual_abscisse"]
            self.current_piece = state["actual_pieces"]
        self.mess = {"valid":False}

    def visit_reg_o(self, node, children): return "O"
    def visit_reg_i(self, node, children): return "I"
    def visit_reg_t(self, node, children): return "T"
    def visit_reg_l(self, node, children): return "L"
    def visit_reg_j(self, node, children): return "J"
    def visit_reg_z(self, node, children): return "L"
    def visit_reg_s(self, node, children): return "S"
    
    def visit_fuchsia(self, node, children) : return self.colors["Fuchsia"]
    def visit_green(self, node, children)   : return self.colors["Green"]
    def visit_yellow(self, node, children)  : return self.colors["Yellow"]
    def visit_blue(self, node, children)    : return self.colors["Blue"]
    def visit_aqua(self, node, children)    : return self.colors["Aqua"]
    def visit_red(self, node, children)     : return self.colors["Red"]
    def visit_orange(self, node, children)  : return self.colors["Orange"]

    def visit_shape(self, node, children): return {shape:children[-1]}
    def visit_color(self, node, children): return {color:children[-1]}

    def visit_valid(self, node, children):
        # convert to valid
        self.mess["valid"] = True
        return {valid:True}

    def visit_direction(self, node, children):
        print("directions:",node, children)
        print(type(node),type(children))
        if "gauche" == children[-1]:
            return {direction:-1}
        if "droite" == children[-1]:
            return {direction:1}

    def visit_select_piece(self, node, children):
        # convert to choose
        info = filter_dict(children)
        #print("select_piece:", info)
        if info:
            choose = info.popitem()[1]
            for key in info:
                if not choose == info[key]:
                    raise ShapeAndColorNotMatchException
            if choose not in self.pieces :
                raise UnvalaibleChooseException
            self.mess["choose"] = choose
        return info

    def visit_select_column(self, node, children):
        # convert to hor_move
        info = filter_dict(children)
        #print("num_column:", info)
        if ordinaux in info:
            self.mess["hor_move"] = info[ordinaux] - self.current_abscisse
        elif direction in info and num_column in info:
            self.mess["hor_move"] = info[num_column] * info[direction]
        elif num_column in info:
            self.mess["hor_move"] = info[num_column] - self.current_abscisse
        else :
            raise HorMoveException
        return info

    def visit_select_turn(self, node, children):
    	info = filter_dict(children)
    	if num_column in info:
    		self.mess["rotate"] = num_column 
    	else:
    		self.mess["rotate"] = 1
    	if direction in info and info[direction]==-1:
    		self.mess["rotate"] = 4 - (self.mess["rotate"] % 4)


    def visit_num_column(self, node, children):
        return {num_column: index_column_vocab[node.value] }

    def visit_num_piece(self, node, children):
        return {num_piece: self.pieces[index_piece_vocab[node.value]]}

    def visit_ordinaux(self, node, children):
        return {ordinaux: ordinals_vocab[node.value]}

    def visit_mainrule(self, node, children):
        return children

parser = peg.ParserPython(mainrule, debug=False)
if __name__ == "__main__":
    try:
        parse_tree = parser.parse(argv[1])
        print("parse tree: ", parse_tree)
    except peg.NoMatch as e:
        print(e)
    result = peg.visit_parse_tree(parse_tree, Visit(debug=False))
    print("result: ", result)
