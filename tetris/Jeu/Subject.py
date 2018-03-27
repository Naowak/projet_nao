#coding : utf-8
import asyncio


class Subject:
    """ Classe permettant de représenter une Game pour le Serveur :
            C'est elle qui gère les connexions et déconnexion à une Game. 
            Elle gère les joueurs comme les observateurs.
    """

    def __init__(self, gid):
        """ Instancie une nouvelle instance de Subject.

        Paramètres :
            - gid : int : Game ID, identifiant de la partie pour le serveur
        """
        self.gid = gid
        self.is_finished = False
        self.clients = {"players": {}, "viewers": {}}

    def bind_player(self, client):
        """ Lie un joueur à la partie.

        Paramètre :
            - client : instance Serveur.Client : représente le client connecté au serveur 
                qui va être l'un des joueurs de la partie
        """
        self.clients["players"][client.id] = client
        print(client.name, "playerbind to the game ", self.gid)

    def unbind_client(self, client):
        """ Délie un joueur ou un observateur de la partie.

        Paramètre :
            - client : instance Serveur.Client : représente le client (observateur ou joueur)
            connecté au serveur qui va être délié de la partie
        """
        if client.id in self.clients["players"]:
            print("game cancelled")
            self.is_finished = True
        elif client.id in self.clients["viewers"]:
            client.on_quit_game(self)
            del self.clients["viewers"][client.id]
        else:
            print("Error, client key not find .")

    def bind_viewer(self, viewer):
        """ Lie un observateur à la partie.

        Paramètre :
            - client : instance Serveur.Client : représente le client connecté au serveur 
                qui va être l'un des observateurs de la partie
        """
        self.clients["viewers"][viewer.id] = viewer
        viewer.on_view_game(self)
        print(viewer.name, "observebind to the game ", self.gid)

    async def notify_all_viewers(self):
        """ Notifie tous les clients (observateurs comme joueur) liés à la partie de son état actuel :
                envois un message à tous les clients liés
        """
        mess = self.get_etat()
        for client in self.clients["players"].values():
            await client.send_message(mess)
        for viewer in self.clients["viewers"].values():
            await viewer.send_message(mess)

    async def notify_player(self):
        """ Notifie tous les players de l'état actuel de la partie
                envois un message à tous les players."""
        mess = self.get_etat()
        for player in self.clients["players"].values():
            await player.send_message(mess)

    async def notify_view(self,viewer_to_notify = None):
        """ Notifie tous les observateurs de l'état actuel de la partie
                envois un message à tous les observateurs."""
        mess = self.get_etat()
        if viewer_to_notify is None:
            for viewer in self.clients["viewers"]:
                await viewer.send_message(mess)
        else:
           await viewer_to_notify.send_message(mess) 

    def quit(self):
        """ Déconnecte tous les clients de la partie. Fonction à appelé à la fin de la partie. """
        clients = list(self.clients["viewers"].values())+list(self.clients["players"].values())
        for client in clients:
            client.on_quit_game(self)
        print("Game ", self.gid, "close")


    async def set_action(self, command):
        """ Définie une action à réalisé selon le message 'command' reçu par le serveur"""
        pass

    def get_etat(self):
        """ Retourne l'état de la partie"""
        pass

    def __str__(self):
        """ Retourne un String représentant l'instance Subject"""
        string_ret = "players: {"
        for player in self.clients["players"].values():
            string_ret += str(player)+" "
        string_ret += "}; viewers: {"
        for obs in self.clients["viewers"].values():
            string_ret += str(obs)+" "
        string_ret += "}"
        return string_ret
