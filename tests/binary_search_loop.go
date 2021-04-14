package main

import "fmt"

func main() {
    var arr [5]int = [5]int{1, 2, 3, 4, 5}

    low := 0
    high := 5
    mid := (low + high) / 2
    key := 4

    for low <= high {
        mid = (low + high) / 2

        if (arr[mid] == key) {
            break
        } else if (key > arr[mid]) {
            low = mid + 1
        } else {
            high = mid - 1
        }
    }

    fmt.Println(mid)
}
