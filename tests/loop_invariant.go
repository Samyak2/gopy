package main

import "fmt"

func main() {
    var arr [5]int = [5]int{1, 2, 3, 4, 5}

    low := 0
    high := 5
    mid := (low + high) / 2
    key := 4

    some_const := 10

    for low <= high {
        a := 10
        e := some_const + 10

        mid = (low + high) / 2

        if (arr[mid] == key) {
            break
        } else if (key > arr[mid]) {
            low = mid + 1
        } else {
            high = mid - 1
        }

        b := a + 10
        c := mid + 1

        fmt.Println(a, b, c, e)
    }

    fmt.Println(mid)
}
