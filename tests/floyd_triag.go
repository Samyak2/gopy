package main

import "fmt"

func main(){
    var temp int = 1
    fmt.Print("Enter number of rows : ")
    // fmt.Scan(&rows)
    var rows int = 10;
    for i := 1; i <= rows; i++ {

        for k := 1; k <= i; k++ {

            fmt.Printf(" %d",temp)
            temp++
        }
        fmt.Println("")
    }

}
