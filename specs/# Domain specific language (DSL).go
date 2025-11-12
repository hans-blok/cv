# Domain specific language (DSL)

program        := { statement | function_def }
function_def   := "FUNCTION" ":" ident newline { statement } &
statement      := write_stmt | if_stmt | loop_stmt | search_stmt
write_stmt     := "WRITE" ( text | attribute | resource )
if_stmt        := "IF" condition newline { statement } [ "ELSE" { statement } ] "END IF"
loop_stmt      := "DO FOR EACH" ident "IN" entity newline { statement } "END DO"
search_stmt    := "SEARCH_FILE name=" attribute
condition      := "EMPTY(" attribute ")"
attribute      := entity "." "`" ident "`"
entity         := "BLOCK" | "PERSONAL" | "EDUCATION" | ...
resource       := "logo-header.jpg" | "logo-header.png" | ...
ident          := /[a-zA-Z_][a-zA-Z0-9_]*/
