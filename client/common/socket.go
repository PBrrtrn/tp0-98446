package common

import (
	"net"
)

type Socket struct {
	conn net.Conn
}

func NewSocket(conn net.Conn) *Socket {
	socket := &Socket {
		conn: conn,
	}

	return socket
}

func (self *Socket) Send(msg []byte) error {
	sendTotal := len(msg)
	sent := 0

	for sent < sendTotal {
		nSent, err := self.conn.Write(msg[sent:])
		if err != nil {
			return err
		}

		sent += nSent
	}

	return nil
}

func (self *Socket) Receive(recvTotal int) ([]byte, error) {
	buf := []byte {}
	received := 0

	for received != recvTotal {
		partialBuf := make([]byte, recvTotal)
		nReceived, err := self.conn.Read(partialBuf)

		if err != nil {
			return buf, err
		}

		buf = append(buf, partialBuf...)
		received += nReceived
	}

	return buf, nil
}

func (self *Socket) Close() {
	self.conn.Close()
}