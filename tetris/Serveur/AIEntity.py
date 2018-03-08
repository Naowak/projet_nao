from Serveur import Client


class AIEntity(Client.Client):
    """
    Representation d'un niveau de jeu dans le serveur. Client du serveur ne pouvant
    ni observer, ni lancer une partie.

    Attributs:
        -games : dictionnaire de Game(classe) representant les parties dans lesquelles
                ce niveau est actuellement engage. Indexe par l'identifiant des parties;
        -ids_in_games : dictionnaire des identifiants (eventuellement plusieurs) attribues
                dans chacunes des parties dans lesquelles ce niveau est actuellement engage.
                Indexe par l'identifiant des parties.
    """
    def __init__(self, server, name, ws, cid):
        """
        Constructeur de la classe AIEntity
        """
        super().__init__(server, name, ws, cid)
        self.ids_in_games = {}
        self.games = {}

    async def request_unlink(self, mess):
        """
        Methode asynchrone appele quand un niveau decide de quitter une partie.
        Configuration impossible.

        Attributs:
            -mess : dictionnaire representant le message recues.
        """
        print("Level doesn't do an unlink request")

    async def request_new_game(self, mess):
        """
        Methode asynchrone appele quand un niveau decide de demarer une nouvelle partie.
        configuration impossible.

        Attributs:
            -mess : dictionnaire representant le message recu.
        """
        print("Level doesn't do an new_game request")

    async def request_link(self, mess):
        """
        Methode asynchrone appele quand un niveau decide de demarrer une partie.
        Configuration impossible.

        Attributs:
            -mess : dictionnaire representant le message recu.
        """
        print("Level doesn't do an link request")

    async def request_action(self, mess):
        """
        Methode asynchrone appele lorsqu'un coup est joue.

        Attributs:
            -mess : dictionnaire representant le message recu.
        """
        if self.games[mess["gid"]].actual_player in self.ids_in_games[mess["gid"]]:
            await self.games[mess["gid"]].set_action(mess["action"])
        else:
            super.print_error("Error message receive IA_Server :" + self.name +\
                        "(" + str(self.id) + "): not his/her/its turn", mess)
            print(mess["gid"])
            print(self.ids_in_games[mess["gid"]])

    def on_quit_game(self, game):
        """
        Methode appele par le serveur lors de la deconnexion a une partie.

        Attributs:
            -game : partie a quitter.
        """        
        super().on_quit_game(game)
        del self.games[game.gid]
        del self.ids_in_games[game.gid]

    def on_begin_game(self, game, ids_in_game):
        """
        Methode appele par le serveur lors de la connexion en tant que joueur a une partie.

        Attributs:
            -game : partie a rejoindre;
            -ids_in_game : ids attribues dans la partie game.
        """
        super().on_begin_game(game, ids_in_game)
        self.games[game.gid] = game
        self.ids_in_games[game.gid] = ids_in_game

    def on_disconnect(self):
        """
        Methode appele par le serveur lors de la deconnexion a une partie.

        Attributs:
            -game : partie a quitter.
        """
        super().print_error("Error :"+ self.name + " : Level disconnect")
        super().on_disconnect()
        assert(False)

    def on_view_game(self, game):
        """
        Methode appele par le serveur lors de la connexion en tant qu'observeur a une partie.

        Attributs:
            -game : partie a rejoindre.
        """
        super().on_view_game(game)
        print(self.name, " : Level doesn't watch the game")
