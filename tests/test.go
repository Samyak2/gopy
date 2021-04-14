package main

import "fmt"

// hi
var c, python, java bool
var boolean float64
var b int = 5
// ???

func main() {
  var i int = 1
  var f float64 = 1.5
  var g int
  k := 3
  fmt.Println("hello")
  fmt.Println(i, f)

	x,y,z,min,max := 1,2,3,4,5
	if x > max {
		if(y<min) {
			return 0
		} else if z > 0 {
			return 1
		} else {
			a := 20
      return a
		}
	}

  if z := 5; x < z {
      return x
  }

	if x := 25; x < y {
		return x
	} else if x > z {
    a := 5
		return a
	} else {
		return y
	}
}

func main2() {
	/* testing
	for
	*/
	a,b := 1,2

	for a < b {
		a *= 2
	}

	for i := 0; i < 10; i++ {
		//do something
	}

	// var numbers [6]int
	// for i,x:= range numbers {
	// 	fmt.Printf("value of x = %d at %d\n", x,i)
	// }

	for true  {
		fmt.Printf("This loop will run forever.\n");
	}

	a = 10
	// break stmt
	for a < 20 {
		fmt.Printf("value of a: %d\n", a);
		a++;
		if a > 15 {
		   break;
		}
	}

	a = 10
	// continue stmt
	for a < 20 {
		if a == 15 {
		   a = a + 1;
		   continue;
		}
		fmt.Printf("value of a: %d\n", a);
		a++;     
	}

}
