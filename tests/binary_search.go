package main

import "fmt"

func bin_search(key int, arr []int, low int, high int) int {
    var mid int = (low + high) / 2

    if (arr[mid] == key) {
        return mid
    }

    if (key > arr[mid]) {
        return bin_search(key, arr, mid + 1, high)
    } else {
        return bin_search(key, arr, low, mid - 1)
    }
}

func main() {
    var arr []int = []int{1, 2, 3, 4, 5}

    fmt.Println(bin_search(4, arr, 0, 5))
}
