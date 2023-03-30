import socket
import logging

from common.utils import Bet
from common.utils import store_bets

class Server:
    MAX_BATCH_SIZE = 8000

    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError:
                logging.debug('action: accept_and_handle_connection | result: interrupted')

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            batch = self.__receive_batch(client_sock)
            store_bets(batch)
            client_sock.send("OK\n".encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __receive_batch(self, client_sock):
        raw_batch = client_sock.recv(self.MAX_BATCH_SIZE).rstrip()

        seek = 0
        n_bets_in_batch = int.from_bytes(raw_batch[seek:seek+4], 'big')
        seek += 4

        batch = []
        for i in range(n_bets_in_batch):
            first_name_len = int.from_bytes(raw_batch[seek:seek+4], 'big')
            seek += 4
            first_name = raw_batch[seek:seek+first_name_len].decode('utf-8')
            seek += first_name_len

            last_name_len = int.from_bytes(raw_batch[seek : seek+4], 'big')
            seek += 4
            last_name = raw_batch[seek:seek+last_name_len].decode('utf-8')
            seek += last_name_len

            birthdate_len = int.from_bytes(raw_batch[seek : seek+4], 'big')
            seek += 4
            birthdate = raw_batch[seek : seek + birthdate_len].decode('utf-8')
            seek += birthdate_len

            document = int.from_bytes(raw_batch[seek : seek+4], 'big')
            seek += 4

            number = int.from_bytes(raw_batch[seek : seek+4], 'big')
            seek += 4

            bet = Bet("0", first_name, last_name, str(document), birthdate, str(number))
            batch.append(bet)

        return batch

    def die(self):
        logging.info('action: shutdown_socket | result: in_progress')
        self._running = False
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info('action: shutdown_socket | result: success')
