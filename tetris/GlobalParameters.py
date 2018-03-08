"""
Fichier de reglage des parametres du jeu :
    -TAILLE_X : taille du tetris en nombre de colonne;
    -TAILLE_Y : taille du tetris en nombre de colonne;
    -TAILLE_Y_LIMITE : hauteur de depassement tetris en nombre de colonne;
    -PORT : port reseau utilise pour comuniquer avec le serveur;
    -ADRESSE : adresse de comunication avec le serveur;
    -NOMBRE_DE_JOUEUR : nombre de joueur dans la partie;
    -NOMBRE_DE_CHOIX : nombre de choix posible a chaques tours (en nombre de pieces);
    -SCORE_DEPASSEMENT : score obtenu en cas de depassement;
    -NOMBRE_DE_TOUR : nombre limite de tour dans la partie;
    -LEVELS : tableau des differents niveau du jeu.
    ["random" : coup aleatoire
    ,"smart1":  realise une ligne si possible, dans le cas contraire un coup aleatoire est joue
    ,"4-heuristic": le coup est chosit comme l'argmin d'une fonction 4-heuristique
                    avec des poids genere par entropy croise voir entropy  
    ,"6-heuristic": le coup est chosit comme l'argmin d'une fonction 6-heuristique
                    avec des poids genere par entropy croise voir entropy 
    ]
"""
TAILLE_X = 10
TAILLE_Y = 22
TAILLE_Y_LIMITE = TAILLE_Y - 4
PORT = 9001
ADRESSE = "ws://localhost:"
NOMBRE_DE_JOUEUR = 2
NOMBRE_DE_CHOIX = 3
SCORE_DEPASSEMENT = -1000
NOMBRE_DE_TOUR = 6000
LEVELS = ["random", "smart1","4-heuristic", "6-heuristic"]
