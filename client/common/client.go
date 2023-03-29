package common

import (
	"bytes"
	"encoding/binary"
	"bufio"
	"fmt"
	"net"
	"time"

	log "github.com/sirupsen/logrus"
)

const SERIALIZED_BET_LEN = 98
const BATCH_SIZE_INDICATOR_LEN = 4

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	MaxBatchBytes int
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

func (self *Client) SendBets(bets []Bet) {
	log.Infof("SEND %d BETS IN BATCHES OF %dkB", len(bets), self.config.MaxBatchBytes)

	totalSentBets := 0
	for totalSentBets < len(bets) {
		sentBets, err := self.sendBatch(bets, totalSentBets)

		if err != nil {
			log.Errorf("action: enviar_batch | result: fail | err: %v", err)
			// Posiblemente notificar error al server
			return
		} else {
			totalSentBets += sentBets
		}
	}
}

func (self *Client) sendBatch(bets []Bet, int batchStart) (int, error) {
	batch := []byte {}

	currentBet := batchStart
	for currentBet < len(bets) {
		serializedBet := self.serializeBet(bets[currentBet])

		if BATCH_SIZE_INDICATOR_LEN + len(batch) + len(serializedBet) < self.config.MaxBatchBytes {
			batch = append(batch, serializedBet)
			currentBet++
		} else {
			break
		}
	}

	betsInBatch := currentBet - batchStart

	return betsInBatch, nil
}

func (self *Client) serializeBet(bet Bet) []byte {
	buffer := new(bytes.Buffer)

	binary.Write(buffer, bytes.BigEndian, len(bet.FirstName))
	binary.Write(buffer, bytes.BigEndian, bet.FirstName)

	binary.Write(buffer, bytes.BigEndian, len(bet.LastName))
	binary.Write(buffer, bytes.BigEndian, bet.LastName)

	binary.Write(buffer, bytes.BigEndian, len(bet.Birthdate))
	binary.Write(buffer, bytes.BigEndian, bet.Birthdate)

	binary.Write(buffer, bytes.BigEndian, bet.Document)
	binary.Write(buffer, bytes.BigEndian, bet.Number)

	return buffer.Bytes()
}

func (self *Client) _SendBet(bet Bet) bool {
	msgID := 1

	serializedBet := fmt.Sprintf("%32s%32s%8d%16s%8d",
		bet.FirstName,
		bet.LastName,
		bet.Document,
		bet.Birthdate,
		bet.Number,
	)

	self.createClientSocket()
	n_sent, err := fmt.Fprintf(
		self.conn,
		"%x",
		serializedBet,
	)

	msg, err := bufio.NewReader(self.conn).ReadString('\n')
	msgID++
	self.conn.Close()

	if n_sent != SERIALIZED_BET_LEN {
		log.Errorf("action: apuesta_enviada | result: fail | short write: sent %v expected %v",
			self.config.ID,
			n_sent,
			SERIALIZED_BET_LEN,
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
