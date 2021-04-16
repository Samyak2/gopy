package main

import "fmt"

func something(a int) bool {
    if (a < 5) {
        return true

        a = 25 + 60; // unreachable
    } else {
        return false

        var b = 2 * 6 // unreachable
        a = b + 1 // unreachable
    }

    var arg int = 20
    var arg2 int = 30 // dead code

    fmt.Println(arg)

    return true
    return false // unreachable
}

func main() {
    var abc int = 10
    var bcd int = abc // dead code

    something(abc)

    return abc

    fmt.Println(bcd) // unreachable
}
