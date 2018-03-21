# coding: utf-8
import sys
import os
sys.path.append("../")
sys.path.append("../../")
import copy
import random
import numpy as np
import asyncio

from JoueurIA.Client import Heuristic as H
from JoueurIA.Client import ClientInterface
from JoueurIA import Level

class Entropy(Level.Level):
    """Cette classe permet de charger une IA créer par Train_Entropy à partir d'un des fichiers de sauvegarde et
    de l'intégrer au serveur. Elle permet aux clients de pouvoir y accèder et jouer contre elle"""

    def __init__(self, name, load_file):
        """Paramètres :
            - name : String : Nom de l'IA
            - load_file : String : nom de fichier où est enregistrer l'IA que l'on souhaite charger"""
        self.file = load_file
        self.weights = list()
        self.heuristic = {}
	#on charge une IA
        self.load()

    def define_heuristic(self, heuristic_list) :
        """ Paramètres :
             - heuristic_list : list de String : Nom des heuristics sélectionnées pour créer une nouvelle heuristique

            Retour : 
                None

            Ajoute les heuristics de heuristic_list dans self.heuristic.
            Les considères pour cette IA."""

        for h in heuristic_list : 
            if h == "line_transition" :
                self.heuristic[h] = H.line_transition
            elif h == "column_transition" :
                self.heuristic[h] = H.column_transition
            elif h == "holes" : 
                self.heuristic[h] = H.holes
            elif h == "wells" :
                self.heuristic[h] = H.wells
            elif h == "score" :
                self.heuristic[h] = H.score
            elif h == "height" :
                self.heuristic[h] = H.height
            elif h == "hidden_empty_cells" :
                self.heuristic[h] = H.hidden_empty_cells
            elif h == "erosion" :
                self.heuristic[h] = H.erosion
            elif h == "agregate_height" :
                self.heuristic[h] = H.agregate_height
            else :
                raise NameError("L'heuristic ", h, " is not defined")

    async def play(self, state):
        """ Paramètres :
            - state : State.State : Etat du tetris

            Retourne le meilleur play pour l'ia self.current_eval"""
        return H.best_move(list(self.heuristic.values()),self.weights,state)
   
    def load(self):
        """Charge une IA à partir de self.file"""
        #on vérifie que le fichier existe :
        if os.path.isfile(self.file) :
            f = open(self.file, "r")
            cpt = 0
            heuristic_list = list()
            #on charge les heuristics demandées ainsi que leur poids
            for line in f :
                tab = line.split(" ")
                heuristic_list.append(tab[0])
                self.weights.append(float(tab[1]))
            self.define_heuristic(heuristic_list)
        #sinon erreur               
        else :
            raise FileNotFoundError(self.file + " doesn't exist.") 
