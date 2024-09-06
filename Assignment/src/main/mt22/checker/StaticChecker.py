from AST import *
from StaticError import *
from Visitor import Visitor
from collections import Counter

# config o: [[]]
# The first list is for local, the last list is for global
# visit expression must return their type
# check again about o: cause we have block statement


# assume we dont have empty array, super and preventDefault if call, is call just 1 time
# in static check we dont check result value of expression


class Utils:
    # infer for var and func (global)
    def infer(env, ctx, typ):
        infered_object = None
        if type(ctx) is LHS:
            infered_object = Utils.findId(env, ctx.name)
            infered_object.typ = typ
        elif type(ctx) is FuncCall:
            infered_object = Utils.findFunc(env, ctx.name)
            infered_object.return_type = typ
        return typ

    def inferParam(env, name_func, name_param, typ):
        func = Utils.findFunc(env, name_func)
        for param in func.params:
            if param.name == name_param:
                param.typ = typ
        return typ

    # findId should return Id, not function##########
    def findId(env, name):
        for symbol_list in env:
            if type(symbol_list) is dict:
                for symbol in symbol_list["declare"]:
                    if symbol.name == name:
                        return symbol
            else:
                for symbol in symbol_list:
                    if symbol.name == name:
                        return symbol
        raise Undeclared(Identifier(), name)

    def findFunc(env, name):
        for func in env[-1]:
            if func.name == name:
                return func
        raise Undeclared(Function(), name)

    def checkArrayDeclare(lhs, array_init, ctx):
        d = []
        d_init = array_init
        while type(d_init) is ArrayType:
            d += d_init.dimensions
            d_init = d_init.typ
        if d != lhs.dimensions:
            raise TypeMismatchInStatement(ctx)
        if type(d_init) != type(lhs.typ):
            raise TypeMismatchInStatement(ctx)
    
    def compareArrayType(arr1: ArrayType, arr2: ArrayType, ctx):
        d1 = arr1.dimensions
        d2 = arr2.dimensions
        t1 = arr1.typ
        t2 = arr2.typ
        while type(t1) is ArrayType and type(t2) is ArrayType:
            if d1 != d2:
                raise IllegalArrayLiteral(ctx)
            d1 = t1.dimensions
            d2 = t2.dimensions
            t1 = t1.typ
            t2 = t2.typ
        if type(t1) is ArrayType or type(t2) is ArrayType:
            raise IllegalArrayLiteral(ctx)
        if type(t1) != type(t2):
            raise IllegalArrayLiteral(ctx)


# check declare in the first visit
# in first visit, we need procedure of function and global variable (include infer type for them if need)
# o = [scope, scope,...,global scope]
# with funcscope is [{"declare": [], "return": None, "func": ctx}]
# scope is [ctx, ctx,..]
class GetPrototype(Visitor):
    def __init__(self):
        pass

    def visitProgram(self, ctx: Program, o: object):
        o = [
            [
                # just to check redeclare
                FuncDecl("readInteger", IntegerType(), [], None, None),
                FuncDecl("printInteger", VoidType(), [IntegerType()], None, None),
                FuncDecl("readFloat", FloatType(), [], None, None),
                FuncDecl("writeFloat", VoidType(), [FloatType()], None, None),
                FuncDecl("readBoolean", BooleanType(), [], None, None),
                FuncDecl("printBoolean", VoidType(), [BooleanType()], None, None),
                FuncDecl("readString", StringType(), [], None, None),
                FuncDecl("printString", VoidType(), [StringType()], None, None),
                FuncDecl("super", VoidType(), [], None, None),
                FuncDecl("preventDefault", VoidType(), [], None, None),
            ]
        ]
        for decl in ctx.decls:
            self.visit(decl, o)
        return o

    # FuncDecl:
    # name = str, return_type = Type(), params = List[ParamDecl], inherit = str or None, body = BlockStmt
    # o = [scope, scope,...[list of funcdecl and global variable]]
    # scope = (func, inherit, [vardecl and paramdecl or scope]) or [vardecl and paramdecl or scope]
    def visitFuncDecl(self, ctx: FuncDecl, o: object):
        # check for redeclare in global and add funcdecl to global scope
        for decl in o[-1]:
            if ctx.name == decl.name:
                raise Redeclared(Function(), ctx.name)
        o[-1] += [ctx]
        return o

    # VarDecl:
    # name = str, typ = Type(), init = Expr or None
    # o = [scope, scope,...[list of funcdecl and global variable]]
    # scope = (func, inherit, [vardecl and paramdecl or scope])
    def visitVarDecl(self, ctx: VarDecl, o: object):
        o[0].append(ctx)
        return o


# All redeclare is catch in first visit
class StaticChecker(Visitor):
    def __init__(self, ast):
        self.ast = ast
        self.env = [[]]
        # self.env = GetPrototype().visit(self.ast, [[]])

    def check(self):
        return self.visit(self.ast, self.env)

    # env: [function scope]
    def checkSuper(self, env, super):
        if env[0]["first_valid"] == True:
            # when invoke more 1 time
            if env[0]["number_call_special"] > 0:
                raise InvalidStatementInFunction(super.name)
            if env[0]["func"].inherit is None:
                raise InvalidStatementInFunction(super.name)
            func_parent = Utils.findFunc(env, env[0]["func"].inherit)
            if len(super.args) == len(func_parent.params):
                for param, arg in zip(func_parent.params, super.args):
                    if type(param.typ) != type(self.visit(arg, env)):
                        if type(self.visit(arg, env)) is FloatType and type(param.typ) is IntegerType:
                            continue
                        else:
                            raise TypeMismatchInExpression(arg)
            elif len(super.args) > len(func_parent.params):
                raise TypeMismatchInExpression(super.args[len(func_parent.params)])
            else:
                raise TypeMismatchInExpression()
        else:
            raise InvalidStatementInFunction(super.name)


    def checkPreventdefault(self, env, prevent):
        if env[0]["first_valid"] == True:
            # when invoke more 1 time
            if env[0]["number_call_special"] > 0:
                raise InvalidStatementInFunction(prevent.name)
            if env[0]["func"].inherit is None:
                raise InvalidStatementInFunction(prevent.name)
            if len(prevent.args) != 0:
                raise InvalidStatementInFunction(prevent.name)
        else:
            raise InvalidStatementInFunction(prevent.name)

       
    # program:
    # decls: List[Decl]
    def visitProgram(self, ctx: Program, o: object):
        env = GetPrototype().visit(ctx, o)
        entrypoint = False
        for decl in ctx.decls:
            self.visit(decl, env)
        for func in env[-1]:
            if type(func) is FuncDecl:
                if func.name == "main" and type(func.return_type) is VoidType:
                    entrypoint = True
                    break
        if entrypoint == False:
            raise NoEntryPoint()

    # FuncDecl:
    # name = str, return_type = Type(), params = List[ParamDecl], inherit = str or None, body = BlockStmt
    def visitFuncDecl(self, ctx: FuncDecl, o: object):
        # create function scope and add inherit param
        env = [
            {
                "declare": [],
                "return": None,
                "func": Utils.findFunc(o, ctx.name),
                "first_valid": False,
                "number_call_special": 0,
            }
        ] + o

        # check inherit
        if ctx.inherit is not None:
            func_parent = Utils.findFunc(o, ctx.inherit)
            if func_parent is None:
                raise Undeclared(Function(), ctx.inherit)
            env[0]["declare"] = [
                param for param in func_parent.params if param.inherit is True
            ]

            # check super and preventDefault in children function
            if len(ctx.body.body) > 0 and len(func_parent.params) == 0:
                env[0]["first_valid"] = True

            if len(ctx.body.body) > 0 and len(func_parent.params) > 0:
                if type(ctx.body.body[0]) is CallStmt:
                    if ctx.body.body[0].name == "super" or ctx.body.body[0].name == "preventDefault":
                        env[0]["first_valid"] = True
                    else:
                        env[0]["first_valid"] = False
                else:
                        raise InvalidStatementInFunction(ctx.name)


        unique = set()
        for element in ctx.params:
            if element.name in unique:
                raise Redeclared(Parameter(), element.name)
            else:
                unique.add(element.name)

        for param in env[0]["func"].params:
            env = self.visit(param, env)

       
        # visit body
        self.visit(ctx.body, (False, env))
        return o

    # VarDecl:
    # name = str, typ = Type(), init = Expr or None
    def visitVarDecl(self, ctx: VarDecl, o: object):
        # check invalid and infer type for vardecl
        if ctx.init is not None:
            type_init = self.visit(ctx.init, o)
            if type(ctx.typ) is AutoType:
                ctx.typ = type_init
            if type(ctx.typ) is type(type_init):
                if type(ctx.typ) is ArrayType:
                    Utils.checkArrayDeclare(ctx.typ, type_init, ctx)
                else:
                    pass
            elif type(ctx.typ) is FloatType and type(type_init) is IntegerType:
                pass
            else:
                raise TypeMismatchInExpression(ctx.init)

        if type(ctx.typ) is AutoType:
            raise Invalid(Variable(), ctx.name)

        # if in function or loop
        if type(o[0]) is dict:
            if "declare" in o[0]:
                for decl in o[0]["declare"]:
                    if ctx.name == decl.name:
                        raise Redeclared(Variable(), ctx.name)
            o[0]["declare"].append(ctx)
        # if in scope
        else:
            for decl in o[0]:
                if ctx.name == decl.name:
                    return o
            o[0].append(ctx)
        return o

    # ParamDecl:
    # name = str, typ = Type(), out = bool, inherit = bool
    def visitParamDecl(self, ctx: ParamDecl, o: object):
        # check redeclare param
        for decl in o[0]["declare"]:
            if ctx.name == decl.name:
                raise Invalid(Parameter(), ctx.name)
        o[0]["declare"].append(ctx)
        return o

    # Id:
    # name = str
    # o = [scope, scope,...[list of funcdecl and global variable]]
    def visitId(self, ctx: Id, o: object):
        Id = Utils.findId(o, ctx.name)
        return Id.typ

    # ArrayCell:
    # name: str, cell: List[Expr]
    def visitArrayCell(self, ctx: ArrayCell, o: object):
        array_cell = None
        array_cell = Utils.findId(o, ctx.name)
        if len(ctx.cell) != len(array_cell.typ.dimensions):
            raise TypeMismatchInExpression(ctx)
        for cell in ctx.cell:
            cellType = self.visit(cell, o)
            if type(cellType) is not IntegerType:
                raise TypeMismatchInExpression(ctx)
        return array_cell.typ.typ

    # AssignStmt:
    # lhs: LHS, rhs: Expr
    def visitAssignStmt(self, ctx: AssignStmt, o: object):
        inloop, env = o
        leftType = self.visit(ctx.lhs, env)
        rightType = self.visit(ctx.rhs, env)
        lhs = None
        rhs = None

        lhs = Utils.findId(env, ctx.lhs.name)
        if issubclass(type(ctx.rhs), LHS):
            rhs = Utils.findId(env, ctx.rhs.name)
        if type(leftType) is VoidType or type(leftType) is ArrayType:
            raise TypeMismatchInStatement(ctx)

        # type Inference
        if type(leftType) is AutoType and type(rightType) is AutoType:
            return
        if type(leftType) is AutoType:
            leftType = Utils.infer(env, ctx.lhs, rightType)
        if type(rightType) is AutoType:
            rightType = Utils.infer(env, ctx.rhs, leftType)
        if type(leftType) is FloatType and type(rightType) is IntegerType:
            return
        if type(leftType) is type(rightType):
            return

        # in function

        # for array
        raise TypeMismatchInStatement(ctx)

    # BlockStmt:
    # body: List[Stmt or VarDecl]
    def visitBlockStmt(self, ctx: BlockStmt, o: object):
        inloop, env = o
        for line in ctx.body:
            if type(line) is VarDecl:
                env = self.visit(line, env)
            elif type(line) in [
                CallStmt,
                ReturnStmt,
                ContinueStmt,
                BreakStmt,
                AssignStmt,
                FuncCall,
            ]:
                self.visit(line, (inloop, env))
            # if create new scope
            else:
                env1 = [[]] + env
                self.visit(line, (inloop, env1))

    # IfStmt:
    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None
    def visitIfStmt(self, ctx: IfStmt, o: object):
        inloop, env = o
        typ_cond = self.visit(ctx.cond, env)
        if type(typ_cond) is not BooleanType:
            raise TypeMismatchInStatement(ctx.cond)
        self.visit(ctx.tstmt, (inloop, env))
        if ctx.fstmt is not None:
            self.visit(ctx.fstmt, (inloop, env))

    # ForStmt:
    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ctx: ForStmt, o: object):
        inloop, env = o
        self.visit(ctx.init, (False, env))
        scalar = Utils.findId(env, ctx.init.lhs.name)
        init_expr = self.visit(ctx.init.rhs, env)
        typ_cond = self.visit(ctx.cond, env)
        typ_upd = self.visit(ctx.upd, env)
        if type(scalar.typ) is not IntegerType:
            raise TypeMismatchInStatement(ctx)
        if type(init_expr) is not IntegerType:
            raise TypeMismatchInStatement(ctx)
        if type(typ_upd) is not IntegerType:
            raise TypeMismatchInStatement(ctx)
        if type(typ_cond) is not BooleanType:
            raise TypeMismatchInStatement(ctx)
        self.visit(ctx.stmt, (True, env))

    # WhileStmt:
    # cond: Expr, stmt: Stmt
    def visitWhileStmt(self, ctx: WhileStmt, o: object):
        inloop, env = o
        typ_cond = self.visit(ctx.cond, env)
        if type(typ_cond) is not BooleanType:
            raise TypeMismatchInStatement(ctx)
        self.visit(ctx.stmt, (True, env))

    # DoWhileStmt:
    # cond: Expr, stmt: BlockStmt
    def visitDoWhileStmt(self, ctx: DoWhileStmt, o: object):
        inloop, env = o
        typ_cond = self.visit(ctx.cond, env)
        if type(typ_cond) is not BooleanType:
            raise TypeMismatchInStatement(ctx)
        self.visit(ctx.stmt, (True, env))

    # BreakStmt:
    def visitBreakStmt(self, ctx: BreakStmt, o: object):
        inloop, env = o
        if inloop is False:
            raise MustInLoop(ctx)

    # ContinueStmt:
    def visitContinueStmt(self, ctx: ContinueStmt, o: object):
        inloop, env = o
        if inloop is False:
            raise MustInLoop(ctx)

    # ReturnStmt:
    # expr = Expr or None
    def visitReturnStmt(self, ctx: ReturnStmt, o: object):
        # check if return in function
        inloop, env = o
        func_info = None
        for func in env:
            if type(func) is dict:
                func_info = func
                break
        if func_info is None:
            raise TypeMismatchInStatement(ctx)

        # if dont visit return stmt yet
        if func_info["return"] is None:
            if ctx.expr is None:
                if type(func_info["func"].return_type) is VoidType:
                    func_info["return"] = VoidType()
                else:
                    raise TypeMismatchInStatement(ctx)
            else:
                # infer type for function
                if type(func_info["func"].return_type) is AutoType:
                    func_info["return"] = self.visit(ctx.expr, env)
                    func_info["func"].return_type = func_info["return"]
                elif type(func_info["func"].return_type) is type(
                    self.visit(ctx.expr, env)
                ):
                    func_info["return"] = func_info["func"].return_type
                else:
                    raise TypeMismatchInStatement(ctx)
        # if visited return stmt
        else:
            # 1. return not in any stmt
            if env[0] is dict:
                pass
            # 2. return in stmt
            else:
                typ_return = self.visit(ctx.expr, env)
                if type(typ_return) is type(func["return"]):
                    pass
                else:
                    raise TypeMismatchInStatement(ctx)

    # CallStmt:
    # name = str, args = List[Expr]
    def visitCallStmt(self, ctx: CallStmt, o: object):
        inloop, env = o
        func_scope = None

        for scope in env:
            if type(scope) is dict:
                func_scope = [scope] + [env[-1]]
                break
        if ctx.name == "super":
            self.checkSuper(func_scope, ctx)
            func_scope[0]["number_call_special"] += 1
        elif ctx.name == "preventDefault":
            self.checkPreventdefault(func_scope, ctx)
            func_scope[0]["number_call_special"] += 1

        elif ctx.name in ["printInteger", "writeFloat", "printBoolean", "printString"]:
            if len(ctx.args) != 1:
                raise TypeMismatchInStatement(ctx)
            type_arg = self.visit(ctx.args[0], env)
            if ctx.name == "printInteger" and type(type_arg) is IntegerType:
                pass
            elif ctx.name == "writeFloat" and type(type_arg) is FloatType:
                pass
            elif ctx.name == "printBoolean" and type(type_arg) is BooleanType:
                pass
            elif ctx.name == "printString" and type(type_arg) is StringType:
                pass
            else:
                raise TypeMismatchInStatement(ctx)
        else:
            func = Utils.findFunc(env, ctx.name)
            if type(func.return_type) is not VoidType:
                raise TypeMismatchInStatement(ctx)
            if len(ctx.args) != len(func.params):
                raise TypeMismatchInStatement(ctx)
            for arg, param in zip(ctx.args, func.params):
                type_arg = self.visit(arg, o)      
                if type(type_arg) != type(param.typ):
                    if type(type_arg) is FloatType and type(param.typ) is IntegerType:
                        continue
                    else:
                        raise TypeMismatchInStatement(ctx)
                

    # BinExpr:
    # op = str, left = Expr, right = Expr
    def visitBinExpr(self, ctx: BinExpr, o: object):
        leftType = self.visit(ctx.left, o)
        rightType = self.visit(ctx.right, o)
        if ctx.op in ["::"]:
            if type(leftType) is AutoType:
                leftType = Utils.infer(o, ctx.left, StringType)
            if type(rightType) is AutoType:
                rightType = Utils.infer(o, ctx.right, StringType)
            if type(leftType) is StringType and type(rightType) is StringType:
                return StringType()
            raise TypeMismatchInExpression(ctx)
        elif ctx.op in ["==", "!="]:
            if type(leftType) is AutoType:
                leftType = Utils.infer(o, ctx.left, rightType)
            if type(rightType) is AutoType:
                rightType = Utils.infer(o, ctx.right, leftType)
            if type(leftType) is IntegerType and type(rightType) is IntegerType:
                return BooleanType()
            if type(leftType) is BooleanType and type(rightType) is BooleanType:
                return BooleanType()
            raise TypeMismatchInExpression(ctx)
        elif ctx.op in ["&&", "||"]:
            if type(leftType) is AutoType:
                leftType = Utils.infer(o, ctx.left, BooleanType)
            if type(rightType) is AutoType:
                rightType = Utils.infer(o, ctx.right, BooleanType)
            if type(leftType) is BooleanType and type(rightType) is BooleanType:
                return BooleanType()
            raise TypeMismatchInExpression(ctx)
        if ctx.op in ["<", ">", "<=", ">="]:
            if type(leftType) is AutoType:
                leftType = Utils.infer(o, ctx.left, rightType)
            if type(rightType) is AutoType:
                rightType = Utils.infer(o, ctx.right, leftType)
            if type(leftType) in [IntegerType, FloatType] and type(rightType) in [
                IntegerType,
                FloatType,
            ]:
                return BooleanType()
            raise TypeMismatchInExpression(ctx)
        elif ctx.op in ["+", "-", "*", "/"]:
            if type(leftType) is AutoType:
                leftType = Utils.infer(o, ctx.left, rightType)
            if type(rightType) is AutoType:
                rightType = Utils.infer(o, ctx.right, leftType)
            if type(leftType) is FloatType and type(rightType) in [
                IntegerType,
                FloatType,
            ]:
                return FloatType()
            if type(rightType) is FloatType and type(leftType) in [
                IntegerType,
                FloatType,
            ]:
                return FloatType()
            if type(leftType) is IntegerType and type(rightType) is IntegerType:
                return IntegerType()
            raise TypeMismatchInExpression(ctx)
        elif ctx.op in ["%"]:
            if type(leftType) is AutoType:
                leftType = Utils.infer(o, ctx.left, rightType)
            if type(rightType) is AutoType:
                rightType = Utils.infer(o, ctx.right, leftType)
            if type(leftType) is IntegerType and type(rightType) is IntegerType:
                return IntegerType()
            raise TypeMismatchInExpression(ctx)
        else:
            raise TypeMismatchInExpression(ctx)

    # UnExpr:
    # op = str, val = Expr
    def visitUnExpr(self, ctx: UnExpr, o: object):
        exprType = self.visit(ctx.val, o)
        if ctx.op == "!":
            if type(exprType) is BooleanType:
                return BooleanType()
            raise TypeMismatchInExpression(ctx)
        elif ctx.op == "-":
            if type(exprType) is IntegerType:
                return IntegerType()
            if type(exprType) is FloatType:
                return FloatType()
            raise TypeMismatchInExpression(ctx)
        else:
            raise TypeMismatchInExpression(ctx)

    def visitIntegerLit(self, ctx: IntegerLit, o: object):
        return IntegerType()

    def visitFloatLit(self, ctx: FloatLit, o: object):
        return FloatType()

    def visitBooleanLit(self, ctx: BooleanLit, o: object):
        return BooleanType()

    def visitStringLit(self, ctx: StringLit, o: object):
        return StringType()

    # ArrayLit:
    # explist = List[Expr]
    # Assume we dont have empty array
    def visitArrayLit(self, ctx: ArrayLit, o: object):
        typ_check = self.visit(ctx.explist[0], o)
        for expr in ctx.explist[1:]:
            typ_expr = self.visit(expr, o)
            if type(typ_expr) != type(typ_check):
                raise IllegalArrayLiteral(ctx)
            elif type(typ_expr) is ArrayType:
                Utils.compareArrayType(typ_expr, typ_check, ctx)
        return ArrayType([len(ctx.explist)], typ_check)

    # FuncCall:
    # name = str, args = List[Expr]
    def visitFuncCall(self, ctx: FuncCall, o: object):
        func = Utils.findFunc(o, ctx.name)
        if func.return_type is VoidType:
            raise TypeMismatchInExpression(ctx)
        if len(ctx.args) != len(func.params):
            raise TypeMismatchInExpression(ctx)
        for arg, param in zip(ctx.args, func.params):
            type_arg = self.visit(arg, o)
            if type(param.typ) is AutoType:
                param.typ = Utils.inferParam(o, ctx.name, param.name, type_arg)
            elif type(type_arg) != type(param.typ):
                if type(type_arg) is FloatType and type(param.typ) is IntegerType:
                    continue
                else:
                    raise TypeMismatchInExpression(ctx)
        return func.return_type