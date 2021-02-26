// Golang program to illustrate
// the flag.Bool() Function
package main

import (
    "flag"
    "fmt"
)

func main() {

    // Define multiple bool arguments
    plainArgPtr := flag.Bool("plaintext", false, "Enable plaintext")
    jsonArgPtr := flag.Bool("json", false, "Enable JSON")
    csvArgPtr := flag.Bool("csv", false, "Enable CSV")

    // Parse command line into the defined flags
    flag.Parse()

    fmt.Println("Enable plaintext:", *plainArgPtr)
    fmt.Println("Enable JSON:", *jsonArgPtr)
    fmt.Println("Enable CSV:", *csvArgPtr)
}
