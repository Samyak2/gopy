package main

import "fmt"

func BubbleSort(array [7]int) [7]int {
	for i := 0; i < 6; i++ {
		for j := 0; j < 7-i-1; j++ {
			if array[j] > array[j+1] {
				var temp int = array[j]
				array[j] = array[j+1]
				array[j+1] = temp
			}
		}
	}
	return array
}
func main() {
	array := [7]int{11, 14, 3, 8, 18, 17, 43}
	fmt.Println(BubbleSort(array))
}
