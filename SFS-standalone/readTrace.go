package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

type Action struct {
	JobName string
	Exec    string
	Para1   int
	// Para2   int
	Start    int // 控制任务到达间隔, 应该都是 0.
	Id       int
	ConStart string
}

func GetTrace(path string) ([]Action, int) {
	file, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
	}

	defer file.Close()
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var txtlines []string
	for scanner.Scan() {
		txtlines = append(txtlines, scanner.Text())
	}

	return ParseTrace(txtlines)
}

func ParseTrace(traces []string) ([]Action, int) {
	results := []Action{}
	var s []string
	var i int
	// var j int
	var f int
	var id int
	var newAction Action
	var num int = 0

	for _, eachline := range traces {
		fmt.Println(eachline)
		s = strings.Split(eachline, " ")
		i, _ = strconv.Atoi(s[2])
		// j, _ = strconv.Atoi(s[3])
		f, _ = strconv.Atoi(s[3])
		id, _ = strconv.Atoi(s[4])
		newAction = Action{s[0], s[1], i, f * 9, id, s[5] + " " + s[6]}
		// newAction = Action{s[0], s[1], i, j, f * 9, id}
		results = append(results, newAction)
		num += 1
	}

	return results, num
}
