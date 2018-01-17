# projet_nao


Pour lancer le tetris:
	Lancer le fichier "launcher.py" avec python 3 ex : "python3 launcher.py"

Si jamais la page HTML ne s'est pas lancée automatiquement:
	Ouvrir le fichier "/JoueurGUI/tetris_ui.html" avec un navigateur web.

Une fois sur la page html et le serveur lancé (launcher.py lance tout, normalement):
	- Sélectionner le niveau de l'IA dans les petits menus déroulants.
	- Lancer une partie contre une IA ou un joueur humain en cliquant sur un des liens (on ne peut pas, pour l'instant, observer une partie).
	- Pour bouger une pièce utiliser les touches [Z,Q,S,D] ou les flèches (ne fonctionne pas sur tout les ordinateurs).
	- Pour poser une pièce utiliser la toucher Enter ou la barre d'espace.
	- Le nombre de tour est fixé à 30, si jamais vous voulez le changer, modifier la variable "NOMBRE_DE_TOUR" dans le fichier "GlobalParameters.py", mettez le nombre de tour que vous voulez.
