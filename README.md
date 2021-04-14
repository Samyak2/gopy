# gopy

A compiler for a subset of Go written in Python (PLY)

<sub>Developed as part of the project for the course "Compiler Design" (UE18CS351) at PES University</sub>

## Usage

`python go_parser.py .\tests\filename.go`

This will generate the following:
 - **AST (Abstract Syntax Tree)**
    - `ast.dot` in Graphviz format (best viewed in Dot format, not Neato)
    - `ast.png` the above in PNG format, if you don't have a Dot file viewer
    - `syntax_tree.txt` in ASCII text format
 - **Symbol Table**
    - printed in the terminal
    - printed in the file `symbol_table.txt`
 - **Type Table**
    - printed in the terminal
 - **Intermediate Code**
    - In a table of Quads (as in the Quadruple format)
    - In three address code (TAC) format
    - Both in terminal
 - **Optimized Intermediate Code**
    - Same as above

## Code Structure

 - [`./tests`](./tests): files to test the compiler on. All files may not work. [`./tests/binary_search.go`](./tests/binary_search.go) should work.
 - [`./ply`](./ply): the source code of [PLY](https://github.com/dabeaz/ply) is here (as suggested in their documentation)
 - [`./go_lexer.py`](./go_lexer.py)
 - [`./go_parser.py`](./go_parser.py): contains the grammar rules with appropriate SDDs to generate AST. This also calls AST optimizer, exports, IC generator, etc.
 - [`./syntree.py`](./syntree.py): everything related to the AST. Contains a class hierarchy of nodes as well as some semantic analysis. Also has a rudimentary AST optimizer.
 - [`./symbol_table.py`](./symbol_table.py): contains Symbol Table and Type Table
 - [`./utils.py`](./utils.py): some utilities for pretty printing errors, etc.
 - [`./tree_vis.py`](./tree_vis.py): to visualize the AST in Graphviz/dot format. Uses the [`pydot`](https://pypi.org/project/pydot/) library and performs a post-order traversal of the AST to generate the graph.
 - [`./pptree_mod.py`](./pptree_mod.py): modified version of the main file of the [`pptree`](https://pypi.org/project/pptree/) package to add support for custom name attribute.
 - [`./tac.py`](./tac.py): Intermediate Code generator (ICG) in Three Address Code (TAC) form using Quadruples. Uses the AST to generate the IC through a combination of pre and post-order traversal.
 - [`./ico.py`](./ico.py): Intermediate Code Optimizer (ICO)
