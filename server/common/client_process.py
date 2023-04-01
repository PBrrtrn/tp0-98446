import logging
import multiprocessing

from common.utils import Bet
from common.network import receive_int, receive_string

class ClientProcess:
    MAX_BATCH_SIZE = 8000

    def __init__(self, socket, storage):
        self._process = multiprocessing.Process(target=self.__handle_client_connection, args=(socket, storage,))
        self._server_pipe, self._client_pipe = multiprocessing.Pipe(duplex=True)

    def run(self):
        self._process.start()

    def recv(self):
        return self._server_pipe.recv()

    def send(self, msg):
        self._server_pipe.send(msg)

    def shutdown(self):
        self._process.join()


    # PRIVATE

    def _recv_from_server(self):
        return self._client_pipe.recv()

    def _send_to_server(self, msg):
        self._client_pipe.send(msg)

    def __handle_client_connection(self, socket, storage):
        client_id = self.__receive_client_id(socket)
        bets = self.__receive_bets(socket, client_id)
        storage.store_bets(bets)

        self._send_to_server(client_id) # Notify finished

        winners = self._recv_from_server() # Get winners when ready
        self.__handle_lottery_end(socket, winners)

        self._server_pipe.close()
        self._client_pipe.close()
        socket.close()




    def __receive_bets(self, socket, client_id):
        try:
            bets = []
            while True:
                batch, finished = self.__receive_client_message(socket, client_id)
                socket.send("OK\n".encode('utf-8'))
                if finished:
                    return bets
                else:
                    bets += batch

        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")




    def __receive_client_message(self, client_sock, client_id):
        first_byte = client_sock.recv(1)

        if str(first_byte[0]) == '4': # TODO: Arreglar. No es probable, pero el largo del nombre podría empezar con 0x04 y generar problemas
            return [], True
        else:
            remaining_bytes = client_sock.recv(3)
            n_bets_in_batch_raw = first_byte + remaining_bytes
            n_bets_in_batch = int.from_bytes(n_bets_in_batch_raw, 'big')

            batch = self.__receive_batch(client_sock, n_bets_in_batch, client_id)
            return batch, False



    def __receive_batch(self, client_sock, n_bets_in_batch, client_id):
        batch = []
        for _ in range(n_bets_in_batch):
            bet = self.__receive_bet(client_sock, client_id)
            batch.append(bet)

        return batch



    def __receive_bet(self, client_sock, client_id):
        first_name_len = receive_int(client_sock)
        first_name = receive_string(client_sock, first_name_len)

        last_name_len = receive_int(client_sock)
        last_name = receive_string(client_sock, last_name_len)

        birthdate_len = receive_int(client_sock)
        birthdate = receive_string(client_sock, birthdate_len)

        document = receive_int(client_sock)
        number = receive_int(client_sock)

        return Bet(client_id, first_name, last_name, str(document), birthdate, str(number))



    def __handle_lottery_end(self, client_sock, winners):
        client_id = self.__receive_client_id(client_sock)

        agency_winners = winners.get(int(client_id), 0)
        agency_winners_bytes = agency_winners.to_bytes(4, 'big')
        client_sock.send(agency_winners_bytes)




    def __receive_client_id(self, socket):
        return socket.recv(1).decode('utf-8')
