package common

import (
	"bufio"
	"encoding/binary"
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

func (self *Client) ParticipateInLottery(bets []Bet) {
	self.createClientSocket()
	self.sendId()
	self.sendAllBets(bets)
	self.notifyFinishedSending()
	self.receiveLotteryWinners()
	self.conn.Close()
}

func (self *Client) sendId() {
	idByte := []byte(self.config.ID)
	self.conn.Write(idByte)
}

func (self *Client) sendAllBets(bets []Bet) {
	totalSentBets := 0
	for totalSentBets < len(bets) {
		sentBets, err := self.sendBatch(bets, totalSentBets)

		if err != nil {
			log.Errorf("action: enviar_batch | result: fail | err: %v", err)
			// Posiblemente notificar error al server
		} else {
			totalSentBets += sentBets
		}
	}
}

func (self *Client) notifyFinishedSending() {
	delimiterByte := []byte {4}
	self.conn.Write(delimiterByte) // TODO: Chequear short write?
}

func (self *Client) receiveLotteryWinners() {
	self.sendId()

	nWinnersBytes := make([]byte, 4)
	self.conn.Read(nWinnersBytes) // TODO: Manejar short-read y errores

	nWinners := binary.BigEndian.Uint32(nWinnersBytes)
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", nWinners)
}

/*  sendBatch receives a slice of Bet structs and the index of the Bet that should
be the first one in the batch, and serializes the following Bets into a batch of
size < MaxBatchBytes

MaxBatchBytes may be configured in the ClientConfiguration    */
func (self *Client) sendBatch(bets []Bet, batchStart int) (int, error) {
	// Serialize batch
	batch := []byte{}

	currentBet := batchStart
	for currentBet < len(bets) {
		serializedBet := self.serializeBet(bets[currentBet])

		if BATCH_SIZE_INDICATOR_LEN+len(batch)+len(serializedBet) < self.config.MaxBatchBytes {
			batch = append(batch, serializedBet...)
			currentBet++
		} else {
			break
		}
	}

	betsInBatch := currentBet - batchStart
	betsInBatchBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(betsInBatchBytes, uint32(betsInBatch))

	batch = append(betsInBatchBytes, batch...)

	// Send batch
	nSent, err := self.conn.Write(batch)
	bufio.NewReader(self.conn).ReadString('\n')

	if nSent != len(batch) {
		log.Errorf("action: send_batch | result: fail | short write: sent %v expected %v",
			self.config.ID,
			nSent,
			len(batch),
		)
		return betsInBatch, err
	}

	return betsInBatch, nil
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
