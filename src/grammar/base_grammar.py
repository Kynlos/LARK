"""Base grammar for the Casebook language."""

BASE_GRAMMAR = r'''
// Base Casebook Grammar
// This file defines the core language rules

// Keywords and operators (highest priority)
SCENE.3: "SCENE"
DO.3: "DO"
LET.3: "LET"
WHILE.3: "WHILE"
RETURN.3: "RETURN"
THEN.3: "THEN"
IF.3: "$if"
ELIF.3: "$elif"
ELSE.3: "ELSE"
FOR.3: "$for"
IN.3: "in"
TRUE.3: "true"
FALSE.3: "false"
NULL.3: "null"
AND.3: "&&"
OR.3: "||"
NOT.3: "!"
EQ.3: "=="
NE.3: "!="
GT.3: ">"
LT.3: "<"
GE.3: ">="
LE.3: "<="

// Punctuation (high priority)
HASH.2: "#"
DOUBLE_HASH.2: "##"
DOLLAR.2: "$"
LPAREN.2: "("
RPAREN.2: ")"
LBRACE.2: "{"
RBRACE.2: "}"
LSQB.2: "["
RSQB.2: "]"
COLON.2: ":"
COMMA.2: ","
EQUALS.2: "="
PLUS.2: "+"
MINUS.2: "-"
TIMES.2: "*"
DIVIDE.2: "/"
TRIPLE_LT.2: "<<<"
TRIPLE_GT.2: ">>>"


// Complex tokens (medium priority)
SECTION_TYPE.2: "OPTIONS" | "SETUP" | "COVER" | "FRONT" | "HINTS" | "DOCUMENTS" | "LEADS" | "DAY_SECTION" | "GENERIC" | "END"
FUNCTION_NAME.2: /[a-zA-Z][a-zA-Z0-9_]*(?:configure|check|get|set|is|has|find|create|update|delete|validate|process)[A-Za-z0-9_]*/
IDENTIFIER.2: /[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*/
CHARACTER.2: /[A-Z][A-Z0-9_]+(?:\s*[A-Z][A-Z0-9_]+)*/
ID_TEXT.2: /[a-zA-Z0-9][a-zA-Z0-9_\-\.\/]*/

// String literals (medium priority)
DOUBLE_QUOTE_STRING.2: /\"(?:[^\"\\]|\\.)*\"/
SINGLE_QUOTE_STRING.2: /\'(?:[^\'\\]|\\.)*\'/
TRIPLE_QUOTE_STRING.2: /\"\"\"(?:[^\"\\]|\\.)*\"\"\"|\'\'\'(?:[^\'\\]|\\.)*\'\'\'/
UNICODE_STRING.2: /[\u201C\u201D](?:[^\u201C\u201D\\]|\\.)*[\u201C\u201D]/

// Comments (low priority)
COMMENT.1: /\/\/[^\n]*/
BLOCK_COMMENT.1: /\/\*(?:[^*]|\*[^\/])*\*\//

// Raw text (lowest priority)
RAW_CONTENT.0: /[^$#{}()<>\/\n][^$#{}()<>\/\n]*/
TEXT.0: /[^$#{}()<>\/\n][^$#{}()<>\/\n]*/

// Whitespace
NEWLINE: /\r?\n/
WS: /[ \t]+/

// Import common tokens
%import common.NUMBER

// Ignore whitespace and comments
%ignore WS
%ignore COMMENT
%ignore BLOCK_COMMENT

// Rules
start: section_or_comment*
section_or_comment: section | COMMENT

section: section_header entry_content

section_header: HASH section_type_opt id_and_string options_opt NEWLINE
section_type_opt: SECTION_TYPE?
id_and_string: ID_TEXT string?
options_opt: options?

entry_content: blocks child_entries
blocks: block*
child_entries: child_entry*

child_entry: child_header entry_content
child_header: DOUBLE_HASH id_and_string options_opt NEWLINE

options: DOLLAR LPAREN args_opt RPAREN
args_opt: args?
args: positional_args named_args_opt | named_args
named_args_opt: (COMMA named_args)?

positional_args: expression (COMMA expression)*
named_args: named_arg (COMMA named_arg)*
named_arg: IDENTIFIER EQUALS expression

block: code_or_text NEWLINE*
code_or_text: code_block | text_block | COMMENT

code_block: function_call | control_statement | scene_block | action_block | character_line

scene_block: SCENE IDENTIFIER LBRACE blocks RBRACE
action_block: DO string
character_line: CHARACTER COLON string

function_call: DOLLAR name LPAREN args_opt RPAREN brace_block_opt
name: FUNCTION_NAME | IF | ELIF | ELSE | FOR
brace_block_opt: (COLON brace_block)?

brace_block: LBRACE blocks RBRACE

control_statement: if_statement | for_statement | while_statement | let_statement | return_statement

if_statement: IF LPAREN expression RPAREN (THEN | COLON) brace_block elif_parts else_part
elif_parts: elif_part*
elif_part: ELIF LPAREN expression RPAREN (THEN | COLON) brace_block
else_part: (ELSE (THEN | COLON) brace_block)?

for_statement: FOR LPAREN IDENTIFIER IN expression RPAREN (THEN | COLON) brace_block
while_statement: WHILE expression DO brace_block
let_statement: LET IDENTIFIER EQUALS expression
return_statement: RETURN expression

expression: or_expr
or_expr: and_expr (OR and_expr)*
and_expr: not_expr (AND not_expr)*
not_expr: NOT not_expr | comparison
comparison: sum_expr (compare_op sum_expr)*
sum_expr: product_expr ((PLUS|MINUS) product_expr)*
product_expr: atom ((TIMES|DIVIDE) atom)*

atom: LPAREN expression RPAREN -> group
    | function_call -> func
    | NUMBER -> number
    | string -> str
    | IDENTIFIER -> var
    | list -> list
    | dict -> dict
    | boolean -> bool
    | NULL -> null

compare_op: GE | LE | GT | LT | EQ | NE | IN

list: LSQB list_items RSQB
list_items: (expression (COMMA expression)*)?

dict: LBRACE dict_items RBRACE
dict_items: (key_value (COMMA key_value)*)?
key_value: key COLON expression
key: string | IDENTIFIER

boolean: TRUE | FALSE

text_block: TEXT | raw_text
raw_text: TRIPLE_LT RAW_CONTENT TRIPLE_GT

string: DOUBLE_QUOTE_STRING | SINGLE_QUOTE_STRING | TRIPLE_QUOTE_STRING | UNICODE_STRING
''' 
