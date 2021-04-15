package main

import "fmt"

func something(a int) bool {
    if (a < 5) {
        return true
    } else {
        return false
    }

    var something2 int = 20
    fmt.Println(something2)

    return true
}

func main() {
    var abc int = 10

    something(abc)

    return abc

    var bcd int = abc

    fmt.Println(bcd)
}
