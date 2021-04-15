package dc2

func fun() int {
    var a = 20; // dead code
    var b = 40;
    var c = b * b;
    return c;
    a = a + b; // unreachable code
}