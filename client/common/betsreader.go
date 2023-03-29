package common

import (
    "encoding/csv"
    "os"
    "strconv"
)

type BetsReader struct { }

func (self *BetsReader) ReadBets(filename string) ([]Bet, error) {
	f, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	data, err := csvReader.ReadAll()
	if err != nil {
		return nil, err
	}

	return self.createBets(data), nil
}

func (self *BetsReader) createBets(lines [][]string) []Bet {
	bets := []Bet {}

	for _, line := range lines {
		document, _ := strconv.Atoi(line[2])
		number, _ := strconv.Atoi(line[4])

		bet := Bet{
			FirstName: line[0],
			LastName:  line[1],
			Document:  int32(document),
			Birthdate: line[3],
			Number:	   int32(number),

		}
		bets = append(bets, bet)
	}

	return bets
}
