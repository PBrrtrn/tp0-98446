import socket
import logging

from common.utils import Bet
from common.utils import store_bets


class Server:
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

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            bet = self.__receive_bet(client_sock)
            store_bets([bet])
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")

            client_sock.send("OK\n".encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

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

    def __receive_bet(self, client_sock):
        # TODO: Modify the receive to avoid short-reads
        raw_msg = client_sock.recv(128).rstrip().decode('utf-8')
        logging.info(f'action: receive_apuesta | result: read {len(raw_msg)}')

        first_name = raw_msg[0:32].lstrip()
        last_name = raw_msg[32:64].lstrip()
        document = raw_msg[64:72].lstrip()
        birthdate = raw_msg[72:88].lstrip()
        number = raw_msg[88:96].lstrip()

        return Bet("0", first_name, last_name, document, birthdate, number)

    def die(self):
        logging.info('action: shutdown_socket | result: in_progress')
        self._running = False
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info('action: shutdown_socket | result: success')
