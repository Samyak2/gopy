package forr

import "fmt"

func main() {
	a,b := 1,2

	for a < b {
		a *= 2
	}

	for i := 0; i < 10; i++ {
		//do something
	}

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
