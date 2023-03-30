import socket
import logging

from common.utils import Bet
from common.utils import store_bets, load_bets, has_won

class Server:
    MAX_BATCH_SIZE = 8000
    N_CLIENTS = 1

    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._finished_clients = set()
        self._running = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        client_sockets = []
        while len(self._finished_clients) < self.N_CLIENTS:
            try:
                client_sock = self.__accept_new_connection()
                self.__receive_bets(client_sock)
                client_sockets.append(client_sock)
            except OSError:
                logging.debug('action: accept_and_handle_connection | result: interrupted')

        logging.debug('action: sorteo | result: success')
        for client_socket in client_sockets:
            self.__handle_lottery_end(client_socket)
            client_socket.close()



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




    def __receive_bets(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            client_id = self.__receive_client_id(client_sock)
            while True:
                batch, finished = self.__receive_client_message(client_sock, client_id)
                if finished:
                    break

                store_bets(batch)
                client_sock.send("OK\n".encode('utf-8'))

            # Marcar el cliente como terminado
            self._finished_clients.add(client_id)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")




    def __receive_client_id(self, client_sock):
        return client_sock.recv(1).decode('utf-8')




    def __receive_client_message(self, client_sock, client_id):
        raw_msg = client_sock.recv(self.MAX_BATCH_SIZE).rstrip()

        if str(raw_msg[0]) == '4': # TODO: No es probable, pero el largo del nombre podría empezar con 0x04 y generar problemas
            return [], True
        else:
            batch = self.__deserialize_batch(raw_msg, client_id)
            return batch, False




    def __deserialize_batch(self, raw_batch, client_id):
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

            bet = Bet(client_id, first_name, last_name, str(document), birthdate, str(number))
            # logging.debug(f"APUESTA DE {client_id}: {bet.first_name}, {bet.last_name}")
            batch.append(bet)

        return batch




    def __handle_lottery_end(self, client_sock):
        client_id = self.__receive_client_id(client_sock)

        all_bets = load_bets()
        agency_winners = 0
        for bet in all_bets:
            if bet.agency == int(client_id) and has_won(bet): agency_winners += 1

        agency_winners_bytes = agency_winners.to_bytes(4, 'big')

        client_sock.send(agency_winners_bytes)




    def die(self):
        logging.info('action: shutdown_socket | result: in_progress')
        self._running = False
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info('action: shutdown_socket | result: success')
