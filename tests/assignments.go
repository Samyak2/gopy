package main

func add(a int, b int) int {
    return a + b
}

func main() {
    var foo int = 4
    var bar float32 = 4.3
    foo = bar
    foo = add
    bar = 4 == 3
}
