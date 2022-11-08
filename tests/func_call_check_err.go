package main

/* global variable declaration */
// var a int = 20
//
/* function to add two integers */
func sum(a, b int) int {
	return a + b
}

func zoro(a int, b string) float32 {
	return 3.2
}

func array_test(a [2]int) {
}

func slice_test(a []int, b []string) {}

func main() {
	/* local variable declaration in main function */
	var a int = 3
	var b int = 20
	var c int = 0
	var str string = "str"
	var bin bool = true
	var array2 = [2]int{2, 4}
	var array3 = [3]int{2, 4, 3}
    var int_slice = []int{4, 5}
    var str_slice = []string{ "hey", "there"}

	// should report error: Arguments Number Mismatch Declaration
	sum(a, b, c)
	sum()
	sum(a)

	// should report error: Arguments Type Mismatch Declaration
	// and/or Arguments Number Mismatch Declaration
    sum(sum(2, 4), bin)
    sum(sum(a, str), 3)
	sum(a, str)
	sum(a, zoro())
	sum(a, zoro(2))
	sum(a, zoro(2, "str"))
	sum(array2, b)
    sum("str", 4.5 + 1.4)
	sum("str", 4.8)
	sum("str", bin)

    array_test(array3)

    slice_test(str_slice, array2)
    slice_test(4, str)
}
