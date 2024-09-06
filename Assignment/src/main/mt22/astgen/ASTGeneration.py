
from MT22Visitor import MT22Visitor
from MT22Parser import MT22Parser
from AST import *



class ASTGeneration(MT22Visitor):

    # program: listdecl EOF;
    def visitProgram(self, ctx: MT22Parser.ProgramContext):
        return Program(self.visit(ctx.listdecl()))

    # listdecl: decl listdecl | decl;
    # -> [VarDecl] | [FuncDecl] | [Stmt] (vi decl -> [VarDecl] nen phai xu li])
    def visitListdecl(self, ctx: MT22Parser.ListdeclContext):
        if ctx.listdecl():
            a = self.visit(ctx.decl())
            if isinstance(a, list):
                return a + self.visit(ctx.listdecl()) 
            return [a] + self.visit(ctx.listdecl()) 
        else: 
            a = self.visit(ctx.decl())
            if isinstance(a, list):
                return a
            return [a]

    # decl: vardecl | function | arrdecl;
    # -> [VarDecl] | FuncDecl | Stmt
    def visitDecl(self, ctx: MT22Parser.DeclContext):
        if ctx.vardecl():
            return self.visit(ctx.vardecl())
        elif ctx.function():
            return self.visit(ctx.function())
        else: 
            return self.visit(ctx.arrdecl())

    

    # atomic_type: INTEGER | FLOAT | BOOLEAN | STRING | auto_type | void_type;
    # -> IntegerType | FloatType | BooleanType | StringType
    def visitAtomic_type(self, ctx: MT22Parser.Atomic_typeContext):
        if ctx.INTEGER():
           return IntegerType()
        elif ctx.FLOAT():
            return FloatType()
        elif ctx.BOOLEAN():
            return BooleanType()
        elif ctx.auto_type():
            return AutoType()
        elif ctx.void_type():
            return VoidType()
        else:
            return StringType()

    # array_type: ARRAY LSBRACKET listinteger RSBRACKET OF atomic_type;
    # -> ArrayType
    def visitArray_type(self, ctx: MT22Parser.Array_typeContext):
        return ArrayType(self.visit(ctx.listinteger()), self.visit(ctx.atomic_type()))    


    # listinteger: INTEGER_LIT COMMA listinteger | INTEGER_LIT;
    # -> [int] 
    def visitListinteger(self, ctx: MT22Parser.ListintegerContext):
        if ctx.listinteger():
            return [(int)(ctx.INTEGER_LIT().getText())] + self.visit(ctx.listinteger())
        else:
            return [(int)(ctx.INTEGER_LIT().getText())]

    # void_type: VOID;
    # -> VoidType
    def visitVoid_type(self, ctx: MT22Parser.Void_typeContext):
        return VoidType()

    # auto_type: AUTO;
    # -> AutoType
    def visitAuto_type(self, ctx: MT22Parser.Auto_typeContext):
        return AutoType()

    # array_lit: LCBRACKET listexpr RCBRACKET;
    # -> ArrayLit
    def visitArray_lit(self, ctx: MT22Parser.Array_litContext):
        return ArrayLit(self.visit(ctx.listexpr()))



    # literal:
	# array_lit
	# | INTEGER_LIT
	# | FLOAT_LIT
	# | BOOLEAN_LIT
	# | STRING_LIT;
    # -> ArrayLit | IntegerLit | FloatLit | BooleanLit | StringLit
    def visitLiteral(self, ctx: MT22Parser.LiteralContext):
        if ctx.array_lit():
            return self.visit(ctx.array_lit())
        elif ctx.INTEGER_LIT():
            return IntegerLit(int(ctx.INTEGER_LIT().getText()))
        elif ctx.FLOAT_LIT():
            if "." in ctx.FLOAT_LIT().getText():
                return FloatLit(float('0'+ ctx.FLOAT_LIT().getText()))
            return FloatLit(float(ctx.FLOAT_LIT().getText()))
        elif ctx.BOOLEAN_LIT():
            return BooleanLit(bool(ctx.BOOLEAN_LIT().getText()))
        else:
            return StringLit(ctx.STRING_LIT().getText())
        



    # listid: ID COMMA listid | ID; 
    # -> [string]
    def visitListid(self, ctx: MT22Parser.ListidContext):
        if ctx.COMMA():
            return [ctx.ID().getText()] + self.visit(ctx.listid())
        else:
            return [ctx.ID().getText()]

    # vardecl: vardecl1 SEMICOLON | vardecl2 SEMICOLON;
    # -> [VarDecl()]
    def visitVardecl(self, ctx: MT22Parser.VardeclContext):
        if ctx.vardecl1():
            decl = self.visit(ctx.vardecl1())
            n = len(decl)//2
            resutl = []
            for i in range(n):
                resutl += [VarDecl(decl[i], decl[n], decl[i + n + 1])]
            return resutl
        else:
            return self.visit(ctx.vardecl2())

    # vardecl1: ID COMMA vardecl1 COMMA expr | ID COLON atomic_type ASSIGN expr;
    # -> [string + Type() + Expr()]
    def visitVardecl1(self, ctx: MT22Parser.Vardecl1Context):
        if ctx.atomic_type():
            return [ctx.ID().getText()] + [self.visit(ctx.atomic_type())] + [self.visit(ctx.expr())]
        else:
            return [ctx.ID().getText()] + self.visit(ctx.vardecl1()) + [self.visit(ctx.expr())]

    # vardecl2: listid COLON atomic_type;
    # -> [VarDecl()]
    def visitVardecl2(self, ctx: MT22Parser.Vardecl2Context):
        listid = self.visit(ctx.listid())
        return [VarDecl(id, self.visit(ctx.atomic_type())) for id in listid]


    # arrdecl: arrdecl1 SEMICOLON | arrdecl2 SEMICOLON;
    # -> [VarDecl()]
    def visitArrdecl(self, ctx: MT22Parser.ArrdeclContext):
        if ctx.arrdecl1():
            decl = self.visit(ctx.arrdecl1())
            n = len(decl)//2
            resutl = []
            for i in range(n):
                resutl += [VarDecl(decl[i], decl[n], decl[i + n + 1])]
            return resutl
        else:
            return self.visit(ctx.arrdecl2())
        
    # arrdecl1: ID COMMA arrdecl1 COMMA array_lit | ID COLON array_type ASSIGN array_lit;
    # -> [string + Type() + Expr()]
    def visitArrdecl1(self, ctx: MT22Parser.Arrdecl1Context):
        if ctx.array_type():
            return [ctx.ID().getText()] + [self.visit(ctx.array_type())] + [self.visit(ctx.array_lit())]
        else:
            return [ctx.ID().getText()] + self.visit(ctx.arrdecl1()) + [self.visit(ctx.array_lit())]


    # arrdecl2: listid COLON array_type;
    # -> [VarDecl()]
    def visitArrdecl2(self, ctx: MT22Parser.Arrdecl2Context):
        listid = self.visit(ctx.listid())
        return [VarDecl(id, self.visit(ctx.array_type())) for id in listid]
    
           
           




###################################################






    #paratype: atomic_type | array_type;
    # -> Type
    def visitParatype(self, ctx: MT22Parser.ParatypeContext):
        if ctx.array_type():
            return self.visit(ctx.array_type())
        else:
            return self.visit(ctx.atomic_type())

    #     // ID2 is parent function (must check return in function(not completed))
    # paradecl: ID COLON paratype
	# 	| INHERIT ID COLON paratype
	# 	| OUT ID COLON paratype
	# 	| INHERIT OUT ID COLON paratype;
    # -> ParamDecl
    def visitParadecl(self, ctx: MT22Parser.ParadeclContext):
        a = self.visit(ctx.paratype())
        if ctx.INHERIT() and ctx.OUT():
            return ParamDecl(ctx.ID().getText(), a, True, True )
        elif not ctx.INHERIT() and ctx.OUT():
            return ParamDecl(ctx.ID().getText(), a, True, False )
        elif ctx.INHERIT() and not ctx.OUT():
            return ParamDecl(ctx.ID().getText(), a, False, True )
        else:
            return ParamDecl(ctx.ID().getText(), a, False, False )
        
    # listparadecl: listparadeclprime | ;
    # -> [ParamDecl()]
    def visitListparadecl(self, ctx: MT22Parser.ListparadeclContext):
        if ctx.getChildCount() == 0:
            return []
        else:
            return self.visit(ctx.listparadeclprime())

    # listparadeclprime: ((paradecl COMMA listparadeclprime) | paradecl);
    # -> [ParamDecl()]
    def visitListparadeclprime(self, ctx: MT22Parser.ListparadeclprimeContext):
        if ctx.listparadeclprime():
            return [self.visit(ctx.paradecl())] + self.visit(ctx.listparadeclprime())
        else:
            return [self.visit(ctx.paradecl())]


    # returntypefunction: atomic_type | array_type | auto_type | void_type;
    # -> Type()
    def visitReturntypefunction(self, ctx: MT22Parser.ReturntypefunctionContext):
        if ctx.atomic_type():
            return self.visit(ctx.atomic_type())
        elif ctx.array_type():
            return self.visit(ctx.array_type())
        elif ctx.auto_type():
            return self.visit(ctx.auto_type())
        else:
            return self.visit(ctx.void_type())

    #   function:
    # 	ID COLON FUNCTION returntypefunction LPAREN listparadecl RPAREN block_statement
    # 	// this is for INHERIT function in oop
    # 	| ID COLON FUNCTION returntypefunction LPAREN listparadecl RPAREN INHERIT ID block_stament;
    # // is missing return and void function func_body: LCBRACKET ((statement | listvardecl)*) RCBRACKET;
    # -> FuncDecl()
    
    def visitFunction(self, ctx: MT22Parser.FunctionContext):
        if ctx.INHERIT():
            return FuncDecl(ctx.ID(0).getText(), self.visit(ctx.returntypefunction()), self.visit(ctx.listparadecl()), ctx.ID(1).getText(), self.visit(ctx.block_statement()))
        else:
            return FuncDecl(ctx.ID(0).getText(), self.visit(ctx.returntypefunction()), self.visit(ctx.listparadecl()), None ,self.visit(ctx.block_statement()))







    # expr: expr1 CONCAT expr1 | expr1;
    def visitExpr(self, ctx: MT22Parser.ExprContext):
        if ctx.CONCAT():
            return BinExpr(ctx.CONCAT().getText(), self.visit(ctx.expr1(0)), self.visit(ctx.expr1(1)))
        else:
            return self.visit(ctx.expr1(0))

    # expr1: expr2 (EQUAL| NOTEQUAL| LESS| LESSEQUAL| GREATER| GREATEREQUAL) expr2| expr2;
    def visitExpr1(self, ctx: MT22Parser.Expr1Context):
        if ctx.EQUAL() or ctx.NOTEQUAL() or ctx.LESS() or ctx.LESSEQUAL() or ctx.GREATER() or ctx.GREATEREQUAL():
            return BinExpr(ctx.getChild(1).getText(), self.visit(ctx.expr2(0)), self.visit(ctx.expr2(1)))
        else:
            return self.visit(ctx.expr2(0))
        
    # expr2: expr2 (AND | OR) expr3 | expr3;
    def visitExpr2(self, ctx: MT22Parser.Expr2Context):
        if ctx.AND() or ctx.OR():
            return BinExpr(ctx.getChild(1).getText(), self.visit(ctx.expr2()), self.visit(ctx.expr3()))
        else:
            return self.visit(ctx.expr3())

    # expr3: expr3 (ADD | SUB ) expr4 | expr4;
    def visitExpr3(self, ctx: MT22Parser.Expr3Context):
        if ctx.ADD() or ctx.SUB():
            return BinExpr(ctx.getChild(1).getText(), self.visit(ctx.expr3()), self.visit(ctx.expr4()))
        else:
            return self.visit(ctx.expr4())

    # expr4: expr4 (MULT | DIV | MOD) expr5 | expr5;
    def visitExpr4(self, ctx: MT22Parser.Expr4Context):
        if ctx.MULT() or ctx.DIV() or ctx.MOD():
            return BinExpr(ctx.getChild(1).getText(), self.visit(ctx.expr4()), self.visit(ctx.expr5()))
        else:
            return self.visit(ctx.expr5())  

    # expr5: NOT expr5 | expr6;
    def visitExpr5(self, ctx: MT22Parser.Expr5Context):
        if ctx.NOT():
            return UnExpr(ctx.NOT().getText(), self.visit(ctx.expr5()))
        else:
            return self.visit(ctx.expr6())

    # expr6: SUB expr6 | expr7;
    def visitExpr6(self, ctx: MT22Parser.Expr6Context):
        if ctx.SUB():
            return UnExpr(ctx.SUB().getText(), self.visit(ctx.expr6()))
        else:
            return self.visit(ctx.expr7())

    # expr7: ID LSBRACKET listexpr RSBRACKET | expr8;
    def visitExpr7(self, ctx: MT22Parser.Expr7Context):
        if ctx.ID():
            return ArrayCell(ctx.ID().getText(), self.visit(ctx.listexpr()))
        else:
            return self.visit(ctx.expr8())

    # expr8: literal | ID | function_call | subexpr;
    # -> Expr
    def visitExpr8(self, ctx: MT22Parser.Expr8Context):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.ID():
            return Id(ctx.ID().getText())
        elif ctx.function_call():
            return self.visit(ctx.function_call())
        else:
            return self.visit(ctx.subexpr())

    # subexpr: LPAREN expr RPAREN;
    # -> Expr
    def visitSubexpr(self, ctx: MT22Parser.SubexprContext):
        return self.visit(ctx.expr())

    # listexpr:expr COMMA listexpr| expr; // (listexpr is not null)
    # -> [Expr]
    def visitListexpr(self, ctx: MT22Parser.ListexprContext):
        if ctx.COMMA():
            return [self.visit(ctx.expr())] + self.visit(ctx.listexpr())
        else:
            return [self.visit(ctx.expr())]







    # statement:
	# assignment_statement
	# | if_statement
	# | for_statement
	# | while_statement
	# | do_while_statement
	# | break_statement
	# | continue_statement
	# | return_statement
	# | call_statement
	# | special_function
	# | block_statement;
    def visitStatement(self, ctx: MT22Parser.StatementContext):
        if ctx.assignment_statement():
            return self.visit(ctx.assignment_statement())
        elif ctx.if_statement():
            return self.visit(ctx.if_statement())
        elif ctx.for_statement():
            return self.visit(ctx.for_statement())
        elif ctx.while_statement():
            return self.visit(ctx.while_statement())
        elif ctx.do_while_statement():
            return self.visit(ctx.do_while_statement())
        elif ctx.break_statement():
            return self.visit(ctx.break_statement())
        elif ctx.continue_statement():
            return self.visit(ctx.continue_statement())
        elif ctx.return_statement():
            return self.visit(ctx.return_statement())
        elif ctx.call_statement():
            return self.visit(ctx.call_statement())
        else:
            return self.visit(ctx.block_statement())

    # assignment_statement: lhs ASSIGN expr SEMICOLON;
    # -> AssignStmt
    def visitAssignment_statement(self, ctx: MT22Parser.Assignment_statementContext):
        return AssignStmt(self.visit(ctx.lhs()), self.visit(ctx.expr()))

    # lhs: ID | expr7; // this is index operator (array cell)
    # -> LHS (Id or ArrayCell)
    def visitLhs(self, ctx: MT22Parser.LhsContext):
        if ctx.ID():
            return Id(ctx.ID().getText())
        else:
            return self.visit(ctx.expr7())

    # if_statement: IF LPAREN expr RPAREN statement | IF LPAREN expr RPAREN statement ELSE statement;
    # -> IfStmt
    def visitIf_statement(self, ctx: MT22Parser.If_statementContext):
        if ctx.ELSE():
            return IfStmt(self.visit(ctx.expr()), self.visit(ctx.statement(0)), self.visit(ctx.statement(1)))
        else:
            return IfStmt(self.visit(ctx.expr()), self.visit(ctx.statement(0)))

    # for_statement: FOR LPAREN lhs ASSIGN expr COMMA expr COMMA expr RPAREN statement;
    # -> ForStmt
    def visitFor_statement(self, ctx: MT22Parser.For_statementContext):
        return ForStmt(AssignStmt(self.visit(ctx.lhs()), self.visit(ctx.expr(0))), self.visit(ctx.expr(1)), self.visit(ctx.expr(2)), self.visit(ctx.statement()))

    # while_statement: WHILE LPAREN expr RPAREN statement; (expr must be boolean type)
    # -> WhileStmt
    def visitWhile_statement(self, ctx: MT22Parser.While_statementContext):
        return WhileStmt(self.visit(ctx.expr()), self.visit(ctx.statement()))

    # do_while_statement: DO block_statement WHILE expr SEMICOLON;
    # -> DoWhileStmt
    def visitDo_while_statement(self, ctx: MT22Parser.Do_while_statementContext):
        return DoWhileStmt(self.visit(ctx.expr()), self.visit(ctx.block_statement()))

    # break_statement: BREAK SEMICOLON;
    # -> BreakStmt
    def visitBreak_statement(self, ctx: MT22Parser.Break_statementContext):
        return BreakStmt()

    # continue_statement: CONTINUE SEMICOLON;
    # -> ContinueStmt
    def visitContinue_statement(self, ctx: MT22Parser.Continue_statementContext):
        return ContinueStmt()

    # return_statement: RETURN SEMICOLON| RETURN expr SEMICOLON;
    # -> ReturnStmt
    def visitReturn_statement(self, ctx: MT22Parser.Return_statementContext):
        if ctx.expr():
            return ReturnStmt(self.visit(ctx.expr()))
        else:
            return ReturnStmt()

    # call_statement: ID LPAREN listexpr RPAREN SEMICOLON 
    # | special_function_stmt SEMICOLON 
    # | ID LPAREN RPAREN SEMICOLON;
    # -> CallStmt
    def visitCall_statement(self, ctx: MT22Parser.Call_statementContext):
        if (ctx.special_function_stmt()):
            return self.visit(ctx.special_function_stmt())
        elif ctx.ID() and ctx.listexpr():
            return CallStmt(ctx.ID().getText(), self.visit(ctx.listexpr()))
        return CallStmt(ctx.ID().getText(), [])
    
    # function_call: ID LPAREN listexpr RPAREN 
    # | special_function_expr 
    # | ID LPAREN RPAREN SEMICOLON;
    # -> CallStmt
    def visitFunction_call(self, ctx: MT22Parser.Function_callContext):
        if (ctx.special_function_expr()):
            return self.visit(ctx.special_function_expr())
        elif ctx.ID() and ctx.listexpr():
            return FuncCall(ctx.ID().getText(), self.visit(ctx.listexpr()))
        else:
            return FuncCall(ctx.ID().getText(), []) 

    # block_body_prime: statement | vardecl | arrdecl;
    # -> Stmt | [VarDecl] 
    def visitBlock_body_prime(self, ctx: MT22Parser.Block_body_primeContext):
        if ctx.arrdecl():
            return self.visit(ctx.arrdecl())
        elif ctx.statement():
            return self.visit(ctx.statement())      
        else:
            return self.visit(ctx.vardecl())


    # block_body: block_body_prime block_body | block_body_prime;
    # -> List[Stmt|VarDecl|ArrayDecl] (do vardecl -> [VarDecl()] nen phai xu ly)
    def visitBlock_body(self, ctx: MT22Parser.Block_bodyContext):
        if ctx.block_body(): 
            a = self.visit(ctx.block_body_prime())
            if isinstance(a, list):
                return a + self.visit(ctx.block_body())
            return [a] + self.visit(ctx.block_body()) 
        else:
            a = self.visit(ctx.block_body_prime())
            if isinstance(a, list):
                return a
            return [a]

    # block_statement: LCBRACKET block_body RCBRACKET| LCBRACKET RCBRACKET;
    # -> BlockStmt
    def visitBlock_statement(self, ctx: MT22Parser.Block_statementContext):
        if ctx.block_body():
            return BlockStmt(self.visit(ctx.block_body())) 
        else:
            return BlockStmt([])



    # special_fuction_expr:
    # 	readinteger
    # 	| readfloat
    # 	| readboolean
    # 	| readstring;
    def visitSpecial_function_expr(self, ctx: MT22Parser.Special_function_exprContext):
        if ctx.readinteger():
            return self.visit(ctx.readinteger())
        elif ctx.readfloat():
            return self.visit(ctx.readfloat())
        elif ctx.readboolean():
            return self.visit(ctx.readboolean())
        else:
            return self.visit(ctx.readstring())





    # special_fuction treadted like call_stmt (in stmt)
    # special_function:
	# readinteger
	# | printinteger
	# | writefloat
	# | printboolean
	# | printstring
	# | r_super
	# | preventdefault;
    # -> CallStmt
    def visitSpecial_function_stmt(self, ctx: MT22Parser.Special_function_stmtContext):
        if ctx.printinteger():
            return self.visit(ctx.printinteger())
        elif ctx.writefloat():
            return self.visit(ctx.writefloat())
        elif ctx.printboolean():
            return self.visit(ctx.printboolean())
        elif ctx.printstring():
            return self.visit(ctx.printstring())
        elif ctx.r_super():
            return self.visit(ctx.r_super())
        else:
            return self.visit(ctx.preventdefault())

    # readinteger: READINTEGER LPAREN RPAREN;
    # -> FuncCall
    def visitReadinteger(self, ctx: MT22Parser.ReadintegerContext):
        return FuncCall(ctx.READINTEGER().getText(),[])

    # printinteger: PRINTINTEGER LPAREN (ID | ) RPAREN;
    # -> CallStmt
    def visitPrintinteger(self, ctx: MT22Parser.PrintintegerContext):
        if (ctx.ID()):
            return CallStmt(ctx.PRINTINTEGER().getText(),[Id(ctx.ID().getText())])
        else:
            return CallStmt(ctx.PRINTINTEGER().getText(),[self.visit(ctx.expr())])

    # readfloat: READFLOAT LPAREN RPAREN;
    # -> FuncCall
    def visitReadfloat(self, ctx: MT22Parser.ReadfloatContext):
        return FuncCall(ctx.READFLOAT().getText(),[])
    

    # //writeFloat()
    # writefloat: WRITEFLOAT LPAREN (ID | expr) RPAREN;
    # -> CallStmt
    def visitWritefloat(self, ctx: MT22Parser.WritefloatContext):
        if (ctx.ID()):
            return CallStmt(ctx.WRITEFLOAT().getText(),[Id(ctx.ID().getText())])
        else:
            return CallStmt(ctx.WRITEFLOAT().getText(),[self.visit(ctx.expr())])
    
    # //readString()
    # readstring: READSTRING LPAREN RPAREN;
    # -> FuncCall
    def visitReadstring(self, ctx: MT22Parser.ReadstringContext):
        return FuncCall(ctx.READSTRING().getText(),[])
    
    # //writeString()
    # writestring: WRITESTRING LPAREN (ID | expr) RPAREN;
    # -> CallStmt
    def visitPrintstring(self, ctx: MT22Parser.PrintstringContext):
        if (ctx.ID()):
            return CallStmt(ctx.PRINTSTRING().getText(),[Id(ctx.ID().getText())])
        else:
            return CallStmt(ctx.PRINTSTRING().getText(),[self.visit(ctx.expr())])

    # readboolean: READBOOLEAN LPAREN RPAREN;
    # -> FuncCall
    def visitReadboolean(self, ctx: MT22Parser.ReadbooleanContext):
        return FuncCall(ctx.READBOOLEAN().getText(),[])

    # printboolean: PRINTBOOLEAN LPAREN (ID | expr) RPAREN;
    # -> CallStmt
    def visitPrintboolean(self, ctx: MT22Parser.PrintbooleanContext):
        if (ctx.ID()):
            return CallStmt(ctx.PRINTBOOLEAN().getText(),[Id(ctx.ID().getText())])
        else:
            return CallStmt(ctx.PRINTBOOLEAN().getText(),[self.visit(ctx.expr())])
    
    
    # r_super: R_SUPER LPAREN RPAREN | R_SUPER LPAREN listexpr RPAREN;
    # -> CallStmt
    def visitR_super(self, ctx: MT22Parser.R_superContext):
        if (ctx.listexpr()):
            return CallStmt(ctx.R_SUPER().getText(),self.visit(ctx.listexpr()))
        else:
            return CallStmt(ctx.R_SUPER().getText(),[])
    
    # preventdefault: PREVENTDEFAULT LPAREN RPAREN;
    # -> CallStmt
    def visitPreventdefault(self, ctx: MT22Parser.PreventdefaultContext):
        return CallStmt(ctx.PREVENTDEFAULT().getText(),[])