package structs

type struct1 struct{}

type struct2 struct {
	x, y int
	u    float32
	_    float32 // padding
	// A *[]int
}

func main() {
	hmm := struct {
		x, y int
		u    float32
		_    float32 // padding
		// A *[]int
	}{1, 2, 3.0, 4.0}
}
