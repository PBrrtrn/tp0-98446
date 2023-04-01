import socket
import logging

from common.client_process import ClientProcess
from common.socket import Socket
from common.utils import Bet
from common.utils import has_won

class Server:
    N_CLIENTS = 5

    def __init__(self, port, listen_backlog, storage):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._storage = storage

    def run(self):
        client_processes = []
        for i in range(self.N_CLIENTS):
            try:
                client_sock = self.__accept_new_connection()
                client_process = ClientProcess(client_sock, self._storage)
                client_process.run()
                client_processes.append(client_process)
            except OSError:
                logging.debug('action: accept_and_handle_connection | result: interrupted')

        for client_process in client_processes:
            finished_client_id = client_process.recv()

        winners = self._execute_lottery()
        logging.info('action: sorteo | result: success')

        for client_process in client_processes:
            client_process.send(winners)

        for client_process in client_processes:
            client_process.shutdown()

        self.die()



    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        socket = Socket(c)
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return socket



    def _execute_lottery(self):
        winners = {}
        all_bets = self._storage.load_bets()

        for bet in all_bets:
            if has_won(bet):
                winners[bet.agency] = winners.get(bet.agency, 0) + 1

        return winners


    def die(self):
        logging.info('action: shutdown_socket | result: in_progress')
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info('action: shutdown_socket | result: success')
