package main

/* global variable declaration */
// var a int = 20
//
/* function to add two integers */

// type definitions
type boolean bool

// type aliases
type al_bool0 = bool
type al_bool1 = al_bool0
type al_bool2 = al_bool1
type al_bool3 = boolean

// a: bool, b: boolean
func type_def_test(a al_bool1, b boolean) al_bool2 {
    return 3 < 4
}

func sum(a, b int) int {
	return a + b
}

func zoro(a int, b string) float32 {
    // types scope test
    type boolean int
    type al_bool0 = int
    var integer boolean = 45
    var bl al_bool0 = 4
    type_def_test(integer, bl)
	return 3.2
}

func array_test(a [2]int) {
}

func slice_test(a []int, b []string) {}

var return_int = func() int {
    return 4
}

func main() {
    A := [4]int{4, 5}
    func_int := func(g int, h bool) int { 
        return 4
    }
    var bin bool = 4 > A[1] && 4 == 5 && 4 < func_int(4, A[1])
	var a int = -3
	var b int = 20 * A[0] + return_int()
	var c int = 0 / func_int(4, 5 != 4)
    var b1_boolean boolean = 4 < 3
    var b2_al_bool2 al_bool2 = 4 == 4
    var b3_al_bool0 al_bool0 = 5 != 4
    var b4_bool bool = type_def_test(b1_boolean, b3_al_bool0)

	var str string = "str"
    var func_result int = return_int()
	var array2 []int = []int{2, 4}
	var array3 = [3]int{2, 4, 3}
    var str_slice = []string{ "hey", "there"}

    // should report errors
    var dummy t_unsure = 45
    var again_dummy return_int = "return_int"

    /* below declaration throws runtime error, but it does report error correctly

    var dummy_array []zoro = []zoro{}

    */

	// should report error: Arguments Number Mismatch Declaration
	sum(a, b, c)
	sum()
	sum(a)
	sum(a, zoro())
	sum(a, zoro(2))

	// should report error: Arguments Type Mismatch Declaration
	// and/or Arguments Number Mismatch Declaration
    type_def_test(b1_boolean, b2_al_bool2)
    type_def_test(b3_al_bool0, b1_boolean) // should report any errors on this
    type_def_test(b3_al_bool0, b4_bool)
    zoro(4.0, func_result)
    sum(sum(2, 4), bin)
    sum(sum(a, str), func_result)
	sum(a, str)
	sum(a, str)
	sum(a, zoro(2, "str"))
	sum(a, zoro(2, return_int()))
	sum(array2, b)
    sum("str", 4.5 + 1.4)
	sum("str", 4.8)
	sum("str", bin)

    array_test(array3)

    slice_test(str_slice, array2)
    slice_test(4, str)
}
