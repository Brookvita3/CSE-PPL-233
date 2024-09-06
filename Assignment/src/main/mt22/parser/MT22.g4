grammar MT22;

@lexer::header {
from lexererr import *
}

options{
	language = Python3;
}

//listxx: bnf xxs: ebnf r_xx: because symbol super conflicts with generated code in target language
// or runtime so add prefix r_ NEED CHECK SYNTAX ANALYST

// function
program: listdecl EOF;
listdecl: decl listdecl | decl;
decl: vardecl | function | arrdecl;
//main_func: 'main' COLON FUNCTION VOID LPAREN RPAREN LCBRACKET (vardecl | func)* RCBRACKET;

// 4 Type system and value
atomic_type: INTEGER | FLOAT | BOOLEAN | STRING | auto_type | void_type;
// index in array can be state or literal
array_type: ARRAY LSBRACKET listinteger RSBRACKET OF atomic_type;
listinteger: INTEGER_LIT COMMA listinteger | INTEGER_LIT;
void_type: VOID;
auto_type: AUTO;
array_lit: LCBRACKET listexpr RCBRACKET;
literal:
	array_lit
	| INTEGER_LIT
	| FLOAT_LIT
	| BOOLEAN_LIT
	| STRING_LIT;

// 5 Declarations

listid: ID COMMA listid | ID;
// // solution 1: (check size of index list with size of expression)
// vardecl: listid COLON atomic_type SEMICOLON | listid COLON atomic_type ASSIGN listexpr SEMICOLON;

// solution 2: (but wrong when do assign statement)
vardecl: vardecl1 SEMICOLON | vardecl2 SEMICOLON;
vardecl1: ID COMMA vardecl1 COMMA expr | ID COLON atomic_type ASSIGN expr;
vardecl2: listid COLON atomic_type;



arrdecl: arrdecl1 SEMICOLON | arrdecl2 SEMICOLON;
arrdecl1: ID COMMA arrdecl1 COMMA array_lit | ID COLON array_type ASSIGN array_lit;
arrdecl2: listid COLON array_type;
//arrdecl: listid COLON array_type SEMICOLON | listid COLON array_type ASSIGN array_lit SEMICOLON;



// ID2 is parent function (must check return in function(not completed))
paratype: atomic_type | array_type;
paradecl: ID COLON paratype
		| INHERIT ID COLON paratype
		| OUT ID COLON paratype
		| INHERIT OUT ID COLON paratype;
listparadecl: listparadeclprime | ;
listparadeclprime: ((paradecl COMMA listparadeclprime) | paradecl);

returntypefunction: atomic_type | array_type | auto_type | void_type;
function:
	ID COLON FUNCTION returntypefunction LPAREN listparadecl RPAREN block_statement
	// this is for INHERIT function in oop
	| ID COLON FUNCTION returntypefunction LPAREN listparadecl RPAREN INHERIT ID block_statement;


//state_block: LCBRACKET  RCBRACKET

// 6 Expressions check if number of argument is right (now is wrong: expr = list of arguments, must
// join in expression)

expr: expr1 CONCAT expr1 | expr1;
expr1:
	expr2 (
		EQUAL
		| NOTEQUAL
		| LESS
		| LESSEQUAL
		| GREATER
		| GREATEREQUAL
	) expr2
	| expr2;
expr2: expr2 (AND | OR) expr3 | expr3;
expr3: expr3 (ADD | SUB) expr4 | expr4;
expr4: expr4 (MULT | DIV | MOD) expr5 | expr5;
expr5: NOT expr5 | expr6;
expr6: SUB expr6 | expr7;
// this is index operator (array cell)
expr7: ID LSBRACKET listexpr RSBRACKET | expr8;
expr8: literal | ID | function_call | subexpr;
subexpr: LPAREN expr RPAREN;
listexpr:
	expr COMMA listexpr
	| expr; // (listexpr is not null)

//index_expr: ID LSBRACKET listexpr RSBRACKET;

// 7  Statements
// special function is a statement ?!
statement:
	assignment_statement
	| if_statement
	| for_statement
	| while_statement
	| do_while_statement
	| break_statement
	| continue_statement
	| return_statement
	| call_statement
	| block_statement;

assignment_statement: lhs ASSIGN expr SEMICOLON;
// lhs is SCALAR VARABLE: indexoperator, id
lhs: ID | expr7;
if_statement: 	IF LPAREN expr RPAREN statement
				| IF LPAREN expr RPAREN statement ELSE statement;
// statement must in {} in for
for_statement: FOR LPAREN lhs ASSIGN expr COMMA expr COMMA expr RPAREN statement;
while_statement: WHILE LPAREN expr RPAREN statement;
do_while_statement: DO block_statement WHILE expr SEMICOLON;
break_statement: BREAK SEMICOLON;
continue_statement: CONTINUE SEMICOLON;
return_statement: RETURN SEMICOLON
				| RETURN expr SEMICOLON;
call_statement: ID LPAREN listexpr RPAREN SEMICOLON | special_function_stmt SEMICOLON | ID LPAREN RPAREN SEMICOLON;
function_call: ID LPAREN listexpr RPAREN | special_function_expr | ID LPAREN RPAREN SEMICOLON;
block_body_prime: statement | vardecl | arrdecl;
block_body: block_body_prime block_body | block_body_prime;
block_statement: LCBRACKET block_body RCBRACKET
			   | LCBRACKET RCBRACKET;

// 8 Special functions
special_function_expr:
	readinteger
	| readfloat
	| readboolean
	| readstring;

special_function_stmt:
	printinteger	
	| writefloat
	| printboolean
	| printstring
	| r_super
	| preventdefault;
//readInteger()
readinteger: READINTEGER LPAREN RPAREN;

//printInteger(anArg: integer)
printinteger: PRINTINTEGER LPAREN (ID | expr) RPAREN;

//readFloat()
readfloat: READFLOAT LPAREN RPAREN;

//writeFloat()
writefloat: WRITEFLOAT LPAREN (ID | expr) RPAREN;

//readBoolean()
readboolean: READBOOLEAN LPAREN RPAREN;

//printBoolean(anArg: boolean)
printboolean: PRINTBOOLEAN LPAREN (ID | expr) RPAREN;

//readString()
readstring: READSTRING LPAREN RPAREN;

//printString()
printstring: PRINTSTRING LPAREN (ID | expr) RPAREN;

//super(<expr-list>) 
r_super: R_SUPER LPAREN RPAREN | R_SUPER LPAREN listexpr RPAREN;

//preventDefault() 
preventdefault: PREVENTDEFAULT LPAREN RPAREN;



// 9 Keywords
AUTO: 'auto';
BREAK: 'break';
BOOLEAN: 'boolean';
DO: 'do';
ELSE: 'else';
FALSE: 'false';
FLOAT: 'float';
FOR: 'for';
FUNCTION: 'function';
IF: 'if';
INTEGER: 'integer';
RETURN: 'return';
STRING: 'string';
TRUE: 'true';
WHILE: 'while';
VOID: 'void';
OUT: 'out';
CONTINUE: 'continue';
OF: 'of';
INHERIT: 'inherit';
ARRAY: 'array';

// Operators
ADD: '+';
SUB: '-';
MULT: '*';
DIV: '/';
MOD: '%';
NOT: '!';
AND: '&&';
OR: '||';
EQUAL: '==';
NOTEQUAL: '!=';
LESS: '<';
LESSEQUAL: '<=';
GREATER: '>';
GREATEREQUAL: '>=';
CONCAT: '::';
ASSIGN: '=';

// Separators
LPAREN: '(';
RPAREN: ')';
LSBRACKET: '[';
RSBRACKET: ']';
DOT: '.';
COMMA: ',';
SEMICOLON: ';';
COLON: ':';
LCBRACKET: '{';
RCBRACKET: '}';
UNDERSCORE: '_';
DOUBLEQUOTE: '"';

//NEWLINE: [\n];

// Function special
READINTEGER: 'readInteger';
PRINTINTEGER: 'printInteger';
READFLOAT: 'readFloat';
WRITEFLOAT: 'writeFloat';
READBOOLEAN: 'readBoolean';
PRINTBOOLEAN: 'printBoolean';
READSTRING: 'readString';
PRINTSTRING: 'printString';
R_SUPER: 'super';
PREVENTDEFAULT: 'preventDefault';


// Identifiers
ID: [a-zA-Z_] [a-zA-Z_0-9]*;

// Literals
fragment DIGIT: [0-9];
fragment NON_ZERO_DIGIT: [1-9];
fragment NUMBER_WITH_UNDERSCORE: (DIGIT | (UNDERSCORE DIGIT))*;
INTEGER_LIT:
	'0'
	| NON_ZERO_DIGIT NUMBER_WITH_UNDERSCORE {self.text=self.text.replace("_","")};

//fragment NUMBER: DIGIT+;
//fragment DECIMAL: DOT DIGIT*;
fragment EXPONENT: [eE] [+-]? DIGIT+;
FLOAT_LIT:

		INTEGER_LIT DOT DIGIT* EXPONENT
		| INTEGER_LIT DOT DIGIT*
		| INTEGER_LIT EXPONENT
		| DOT DIGIT+ EXPONENT
		| DOT EXPONENT
		;

	// may be redundant (because it will be removed in INTEGER_LIT)
	//{self.text=self.text.replace("_","")};

BOOLEAN_LIT: TRUE | FALSE;

fragment ESC_SEQ: '\\' ["bfrnt'\\];
fragment ALLOWEDCHAR: (ESC_SEQ | ~['"\\]);
fragment LISTALLOWEDCHAR: (ALLOWEDCHAR | ' ')*;
STRING_LIT:
	DOUBLEQUOTE LISTALLOWEDCHAR DOUBLEQUOTE {self.text=self.text[1:-1]};

// array literal not define an array as a token (lexer rule), but rather as a parser rule

// comment:
BLOCK_COMMENT: DIV MULT .*? MULT DIV -> skip;

LINE_COMMENT: DIV DIV ~[\r\nEOF]* -> skip;

WS: [ \t\r\n\f\b]+ -> skip; // skip spaces, tabs, newlines



// Error (Currently there is no need to add action block))
UNCLOSE_STRING:
	DOUBLEQUOTE LISTALLOWEDCHAR ('\r\n' | '\n' | EOF) {
    if self.text[-1] == '\n' and self.text[-2] == '\r':
        raise UncloseString(self.text[1:-2])
    elif self.text[-1] == '\n':
        raise UncloseString(self.text[1:-1])
    else:
        raise UncloseString(self.text[1:])
 	};

ILLEGAL_ESCAPE: '\\' ~[btnfr"'\\];

ERROR_CHAR: . {raise ErrorToken(self.text)};
//  -------------------------- end Lexical structure ------------------- //