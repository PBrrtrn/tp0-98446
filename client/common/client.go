package common

import (
	"bufio"
	"net"
	"time"
	"encoding/binary"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (self *Client) SendBet(bet Bet) bool {
	msgID := 1

	serializedBet := self.serializeBet(bet)
	log.Debugf("action: apuesta_serializada | apuesta: %x", serializedBet)

	self.createClientSocket()

	n_sent, err := self.conn.Write(serializedBet)

	msg, err := bufio.NewReader(self.conn).ReadString('\n')
	msgID++
	self.conn.Close()

	if n_sent != len(serializedBet) {
		log.Errorf("action: apuesta_enviada | result: fail | short write: sent %v expected %v",
			self.config.ID,
			n_sent,
			len(serializedBet),
		)
		return false
	}

	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
		bet.Document,
		bet.Number,
	)

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
            self.config.ID,
			err,
		)
		return false
	}

	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
        self.config.ID,
        msg,
    )

    return true
}

func (self *Client) serializeBet(bet Bet) []byte {
	serializedBet := []byte {}

	firstNameLenBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(firstNameLenBytes, uint32(len(bet.FirstName)))
	serializedBet = append(serializedBet, firstNameLenBytes...)

	firstNameBytes := []byte(bet.FirstName)
	serializedBet = append(serializedBet, firstNameBytes...)

	lastNameLenBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(lastNameLenBytes, uint32(len(bet.LastName)))
	serializedBet = append(serializedBet, lastNameLenBytes...)

	lastNameBytes := []byte(bet.LastName)
	serializedBet = append(serializedBet, lastNameBytes...)

	birthdateLenBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(birthdateLenBytes, uint32(len(bet.Birthdate)))
	serializedBet = append(serializedBet, birthdateLenBytes...)

	birthdateBytes := []byte(bet.Birthdate)
	serializedBet = append(serializedBet, birthdateBytes...)

	documentBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(documentBytes, uint32(bet.Document))
	serializedBet = append(serializedBet, documentBytes...)

	numberBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(numberBytes, uint32(bet.Number))
	serializedBet = append(serializedBet, numberBytes...)

	return serializedBet
}

/*
// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// autoincremental msgID to identify every message sent
	msgID := 1

loop:
	// Send messages if the loopLapse threshold has not been surpassed
	for timeout := time.After(c.config.LoopLapse); ; {
		select {
		case <-timeout:
	        log.Infof("action: timeout_detected | result: success | client_id: %v",
                c.config.ID,
            )
			break loop
		default:
		}

		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		// TODO: Modify the send to avoid short-write
		fmt.Fprintf(
			c.conn,
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		)
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		msgID++
		c.conn.Close()

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
                c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
            c.config.ID,
            msg,
        )

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
*/
