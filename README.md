# projet_nao

## Détails et Objectifs du projet
Ce projet est réalisé par 5 étudiants de l'Université Paul Sabatier de Toulouse en M2.

Le but de ce projet était de créer un "compagnon de jeu" simulé par le robot Nao de SoftBank Robotics. A la demande des clients, le jeu devait prendre la forme d'un tétris deux joueurs. 

Ainsi, nous pouvons séparer ce projet en trois grandes parties : 
* Le développement du jeu.
* Le développement et entrainement des Intelligences Artificielles contre lesquels l'utilisateur peut jouer.
* Le développement d'intéraction sur le robot Nao (Gestuelle et Vocale). Le Nao doit être capable de s'exprimer, et de comprendre l'utilisateur pour pouvoir jouer à sa place si ce dernier lui dicte un coup.

Ce projet comporte donc les technologies suivantes : 
* Des algorithmes génétiques
* De l'apprentissage par renforcement
* De la Reconnaissance Vocale (et mise en place de grammaire)
      

## Installer les dépendances

* Python 3.6
* [multi_key_dict](https://pypi.python.org/pypi/multi_key_dict/2.0.3) (2.0.3)
* [numpy](https://pypi.python.org/pypi/numpy/1.14.2) (1.14.2)
* [tensorflow](https://pypi.python.org/pypi/tensorflow/1.5.0) (1.5.0)
* [tensorforce](https://pypi.python.org/pypi/tensorforce/0.3.5.1) (0.3.5.1)
* [websockets](https://pypi.python.org/pypi/websockets/4.0.1) (4.0.1)
* [SpeechRecognition](https://pypi.python.org/pypi/SpeechRecognition/3.8.1) (3.8.1)
* [PyAudio](https://pypi.python.org/pypi/PyAudio/0.2.11) (0.2.11)
* [Arpeggio](https://pypi.python.org/pypi/Arpeggio/1.7.1) (1.7.1)

Les modules peuvent être installés avec pip : `python -m pip install <module>` ou `python` désigne la commande permettant de lancer python (`python3` ou `python3.6` sur certaines machines). Pour éviter les problèmes, un environnement virtuel conda peut-être créé avec `conda create` : https://conda.io/docs/commands.html.

## Structure de l’application
L’application se décompose en plusieurs modules distincts, qui communiquent en utilisant la technologie websocket:
* le **serveur** (fichiers du sous-dossier [`projet_nao/tetris/Serveur/`](/tetris/Serveur/)): instantie et expose aux autres modules le jeu (définie dans [`projet_nao/tetris/Jeu/`](/tetris/Jeu/).
* **l'interface utilisateur**: écrite en HTML/Javascript (dans [`projet_nao/tetris/JoueurGUI/tetris_ui.html`](/tetris/JoueurGUI/tetris_ui.html)).
* les modules de **stratégies des intelligence artificielle**: définies dans [`projet_nao/tetris/JoueurIA/Client/`](/tetris/JoueurIA/Client/), elles peuvent être invoquées par l'interface utilisateur pour les affronter, ou bien directement en tant que scripts pour les entraînements (voir [Entraîner une IA](#entra%C3%AEner-une-ia)).
* les modules **d'interactions avec le Nao**: voir [`projet_nao/tetris/JoueurIA/Client/NaoSpeech.py`](/tetris/JoueurIA/Client/NaoSpeech.py), et [`projet_nao/tetris/JoueurIA/Client/Voice.py`](/tetris/JoueurIA/Client/Voice.py). Pour éxecuter les actions sur un robot Nao, celui-ci doit être connecté sur le même sous-réseau que le PC hôte (soit par cable ethernet, soit par Wi-Fi): l'adresse IP du PC hôte, ainsi que celle du Nao doivent être renseignées dans [`projet_nao/tetris/JoueurIA/Client/Nao.py`](/tetris/JoueurIA/Client/Nao.py).

## Lancer l’application
### Lancer une partie
Pour lancer le jeu, il faut se placer dans le répertoire [`projet_nao/tetris/`](/tetris/) et lancer le script [`projet_nao/tetris/launcher.py`](/tetris/launcher.py) avec python 3 (ex : `python3 launcher.py`). Si jamais la page HTML ne s'est pas ouverte automatiquement ou ne s’est pas ouverte correctement, ouvrir le fichier [`projet_nao/tetris/JoueurGUI/tetris_ui.html`](/tetris/JoueurGUI/tetris_ui.html) avec un navigateur web.
### Entraîner une IA
Pour lancer un entraînement, il faut lancer `projet_nao/tetris/launcher.py`](/tetris/launcher.py) dans une console, et le script de l’IA à entraîner ([`projet_nao/tetris/JoueurIA/Client/Train_Entropy.py`](/tetris/JoueurIA/Client/Train_Entropy.py) ou ([`projet_nao/tetris/JoueurIA/Client/Reinforcement.py`](/tetris/JoueurIA/Client/Reinforcement.py)) dans une autre console.

## Jouer au jeu
Dans l'interface, on peut choisir le mode de jeu : `Human VS Human`, `Human VS Nao` ou `Nao VS Nao`. On peut choisir deux niveaux IA : le 1er est utilisé par l'IA dans le mode `Human VS Nao`, et par la première IA dans le mode `Nao VS Nao`. La 2nde est utilisée par la seconde IA dans le mode `Nao VS Nao`.
Pour déplacer une pièce, on utilise les touches [Z,Q,S,D] ou les flèches. Pour poser une pièce utiliser la touche Enter ou la barre d'espace. - Le nombre de tour pour chaque partie est fixé à 30, si jamais vous voulez le changer, modifier la variable `NOMBRE_DE_TOUR` dans le fichier [`projet_nao/tetris/GlobalParameters.py`](/tetris/GlobalParameters.py).

## Ajouter une IA
Les IAs sont définies dans le dossier [`projet_nao/tetris/JoueurIA/Client/`](/tetris/JoueurIA/Client/). La façon la plus simple de créer une IA est de définir une fonction qui associe une action à un état du jeu, comment par exemple la fonction `random_ia` du fichier [`projet_nao/tetris/JoueurIA/Level.py`](/tetris/JoueurIA/Level.py). Il faut aussi ajouter le nom de l'IA dans la liste `LEVELS` du fichier [`projet_nao/tetris/GlobalParameters.py`](/tetris/GlobalParameters.py). C'est le nom qui sera affiché dans l'interface graphique. L'indice dans la liste correspond au numéro de l'IA. Enfin, il faut ajouter un `elif == <numéro de l'IA>` correspondant dans la fonction `create_ia` du fichier [`projet_nao/tetris/Serveur/`](tetris/Serveur/), comme pour l'IA `random`. A l'intérieur, on affecte un nouvel objet `Level` à la variable `IA_STRATEGIE`, en passant au constructeur la fonction associant l'action à l'état (par exemple, `Level.random_ia` pour l'IA `random` qui porte le numéro 0). Il est également possible de créer une classe qui hérite de `Level`, comme la classe `Entropy`. Cette classe devra alors au minimum implémenter la méthode `play`.

