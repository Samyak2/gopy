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

var integer = func() int {
    return 4
}

func main() {
	/* local variable declaration in main function */
    A := [4]int{4, 5}
    func_int := func(g int, h bool) int { 
        return 4
    }
    var bin bool = 4 > A[1] && 4 == 5 && 4 < func_int(4, A[1])
	var a int = -3
	var b int = 20 * A[0] + integer()
	var c int = 0 / func_int(4, 5 != 4)
	var str string = "str"
    var func_result int = integer()
	var array2 []int = []int{2, 4}
	var array3 = [3]int{2, 4, 3}
    var str_slice = []string{ "hey", "there"}

	// should report error: Arguments Number Mismatch Declaration
	sum(a, b, c)
	sum()
	sum(a)

	// should report error: Arguments Type Mismatch Declaration
	// and/or Arguments Number Mismatch Declaration
    zoro(4.0, func_result)
    sum(sum(2, 4), bin)
    sum(sum(a, str), func_result)
	sum(a, str)
	sum(a, str)
	sum(a, zoro())
	sum(a, zoro(2))
	sum(a, zoro(2, "str"))
	sum(a, zoro(2, integer()))
	sum(array2, b)
    sum("str", 4.5 + 1.4)
	sum("str", 4.8)
	sum("str", bin)

    array_test(array3)

    slice_test(str_slice, array2)
    slice_test(4, str)
}
