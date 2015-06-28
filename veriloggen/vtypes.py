class VeriloggenNode(object):
    """ Base class of Veriloggen AST object """
    pass

class _Numeric(VeriloggenNode):
    def __lt__(self, r):
        return LessThan(self, r)
    
    def __le__(self, r):
        return LessEq(self, r)
    
    def __eq__(self, r):
        return Eq(self, r)
    
    def __ne__(self, r):
        return NotEq(self, r)

    def __ge__(self, r):
        return GreaerEq(self, r)
    
    def __gt__(self, r):
        return GreaerThan(self, r)

    def __add__(self, r):
        return Plus(self, r)
    
    def __sub__(self, r):
        return Minus(self, r)
    
    def __pow__(self, r):
        return Power(self, r)
    
    def __mul__(self, r):
        return Times(self, r)
    
    def __div__(self, r):
        return Divide(self, r)
    
    def __truediv__(self, r):
        return Divide(self, r)
    
    def __and__(self, r):
        return And(self, r)

    def __and__(self, r):
        return And(self, r)

    def __or__(self, r):
        return Or(self, r)
    
    def __getitem__(self, r):
        return Bit(self, r)
    
    def __getslice__(self, l, r):
        return Slice(self, l, r)

    def delay(self, r):
        return Delay(self, r)
    
    def prev(self, r):
        return Prev(self, r)
    
class _Variable(_Numeric):
    def __init__(self, name, width=1, length=None, signed=False, value=None):
        self.name = name
        self.width = width
        self.length = length
        self.signed = signed
        self.value = value

    def set(self, r):
        return Subst(self, r)
    
    def __call__(self, r):
        return self.set(r)

    def connect(self, prefix='', postfix=''):
        ret = {
            prefix + self.name + postfix : self,
        }
        return ret
        
#-------------------------------------------------------------------------------
class Reg(_Variable): pass
class Wire(_Variable): pass
class Input(_Variable): pass
class Output(_Variable): pass
class Inout(_Variable): pass

#-------------------------------------------------------------------------------
class _Constant(_Variable):
    def __init__(self, name, value, width=None, signed=False):
        if isinstance(value, _Constant):
            value = value.value
        _Variable.__init__(self, name, width=width, signed=signed, value=value)
        
class Parameter(_Constant): pass
class Localparam(_Constant): pass

#-------------------------------------------------------------------------------
class Int(_Numeric):
    def __init__(self, value):
        self.value = value

class Float(_Numeric):
    def __init__(self, value):
        self.value = value

class Str(_Numeric):
    def __init__(self, value):
        self.value = value

#-------------------------------------------------------------------------------
class _Operator(_Numeric): pass
    
class _BinaryOperator(_Operator):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class _UnaryOperator(_Operator):
    def __init__(self, right):
        self.right = right
        
#-------------------------------------------------------------------------------
# class names should be same the ones in pyverilog.vparser.ast
class Power(_BinaryOperator): pass
class Times(_BinaryOperator): pass
class Divide(_BinaryOperator): pass
class Mod(_BinaryOperator): pass

class Plus(_BinaryOperator): pass
class Minus(_BinaryOperator): pass

class Sll(_BinaryOperator): pass
class Srl(_BinaryOperator): pass
class Sra(_BinaryOperator): pass

class LessThan(_BinaryOperator): pass
class GreaterThan(_BinaryOperator): pass
class LessEq(_BinaryOperator): pass
class GreaterEq(_BinaryOperator): pass

class Eq(_BinaryOperator): pass
class NotEq(_BinaryOperator): pass
class Eql(_BinaryOperator): pass # ===
class NotEql(_BinaryOperator): pass # !==

class And(_BinaryOperator): pass
class Xor(_BinaryOperator): pass
class Xnor(_BinaryOperator): pass
class Or(_BinaryOperator): pass
class Land(_BinaryOperator): pass
class Lor(_BinaryOperator): pass

class Unot(_UnaryOperator): pass
class Ulnot(_UnaryOperator): pass
Not = Unot

def LandList(*args):
    if len(args) == 0:
        raise ValueError("LandList requires at least one argument.")
    if len(args) == 1:
        return args[0]
    left = args[0]
    for right in args[1:]:
        left = Land(left, right)
    return left

def LorList(*args):
    if len(args) == 0:
        raise ValueError("LorList requires at least one argument.")
    if len(args) == 1:
        return args[0]
    left = args[0]
    for right in args[1:]:
        left = Lor(left, right)
    return left

#-------------------------------------------------------------------------------
class _SpecialOperator(_Operator):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class Bit(_Variable):
    def __init__(self, var, pos):
        self.var = var
        self.pos = pos
        
class Slice(_SpecialOperator):
    def __init__(self, var, msb, lsb):
        self.var = var
        self.msb = msb
        self.lsb = lsb

class Cond(_SpecialOperator):
    def __init__(self, condition, true_value, false_value):
        self.condition = condition
        self.true_value = true_value
        self.false_value = false_value
        
class Delay(_SpecialOperator):
    def __init__(self, var, step):
        self.var = var
        self.step = step
                 
class Prev(_SpecialOperator):
    def __init__(self, var, step):
        self.var = var
        self.step = step

#-------------------------------------------------------------------------------
class Always(VeriloggenNode):
    def __init__(self, sensitivity, *statement):
        self.sensitivity = sensitivity
        self.statement = tuple(statement)

    def __call__(self, *statement):
        if self.statement:
            raise ValueError("Statement is already assigned.")
        self.statement = tuple(statement)
        return self

class Assign(VeriloggenNode):
    def __init__(self, statement):
        self.statement = statement

#-------------------------------------------------------------------------------
class Edge(VeriloggenNode):
    def __init__(self, name):
        self.name = name

class Posedge(Edge): pass
class Negedge(Edge): pass

#-------------------------------------------------------------------------------
class Subst(VeriloggenNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class If(VeriloggenNode):
    def __init__(self, condition, true_statement=None, false_statement=None):
        self.condition = condition
        self.true_statement = true_statement
        self.false_statement = false_statement

    def __call__(self, *args):
        if self.true_statement is None:
            self.true_statement = tuple(args)
            return self
        if self.false_statement is None:
            self.false_statement = tuple(args)
            return self
        raise ValueError("True statement and False statement are already assigned.")

    def els(self, *args):
        if self.false_statement is None:
            self.false_statement = tuple(args)
            return self
        raise ValueError("False statement is already assigned.")
        
class For(VeriloggenNode):
    def __init__(self, pre, condition, post, statement):
        self.pre = pre
        self.condition = condition
        self.post = post
        self.statement = statement

class While(VeriloggenNode):
    def __init__(self, condition, statement):
        self.condition = condition
        self.statement = statement

#-------------------------------------------------------------------------------
class Instance(VeriloggenNode):
    def __init__(self, module, instname, params, ports):
        self.module = module
        self.instname = instname
        self.params = params
        self.ports = ports

