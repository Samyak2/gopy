package main

import "fmt"

/* global variable declaration */
var a int = 20

/* function to add two integers */
func sum(a, b int) int {
	fmt.Printf("value of a in sum() = %d\n", a)
	fmt.Printf("value of b in sum() = %d\n", b)

	return a + b
}

func zoro(a int, b string) float32 {
	return 3.2
}

func main() {
	/* local variable declaration in main function */
	var a int = 3
	var b int = 20
	var c int = 0
	var str string = "str"
	var bin bool = true
	var array = [2]int{2, 4}

	// should produce: Arguments Number Mismatch Declaration
	sum(a, b, c)
	sum()
	sum(a)

	// should produce: Arguments Type Mismatch Declaration
	// and/or Arguments Number Mismatch Declaration
	zoro(a, "str")
	sum(a, str)
	sum(a, zoro())
	sum(a, zoro(2))
	sum(a, zoro(2, "str"))
	sum(array, b)
	sum("str", 4.8)
	sum("str", bin)
}
