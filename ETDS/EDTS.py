
gramatica={
    'Expr': [['Term', 'Expr_op']],
    'Expr_op': [['+', 'Term', 'Expr_op'], ['-', 'Term', 'Expr_op'], ['ε']],
    'Term': [['Fact', "Term_op"]],
    'Term_op': [['*', 'Fact', 'Term_op'], ['/', 'Fact', 'Term_op'], ['ε']],
    'Fact': [['(', 'Expr', ')'], ['num'], ['id']]
}

todos_simbolos={t for reglas in gramatica.values() for prod in reglas for t in prod}
no_terminales=set(gramatica.keys())
terminales= todos_simbolos-no_terminales
simbolo_inicial='Expr'

def Primeros(gramatica, terminales):
    primero={}
    todos_los_simbolos=set()
    for producciones in gramatica.values():
        for produccion in producciones:
            todos_los_simbolos.update(produccion)
    todos_los_simbolos.update(gramatica.keys())

    def obtener_primero(simbolo):
        if simbolo in primero:
            return primero[simbolo]
        primero[simbolo] = set()
        if simbolo in terminales or simbolo == 'ε':
            primero[simbolo].add(simbolo)
            return primero[simbolo]

        for produccion in gramatica.get(simbolo, []):
            for s in produccion:
                primeros_s=obtener_primero(s)
                primero[simbolo].update(primeros_s - {'ε'})
                if 'ε' not in primeros_s:
                    break
            else:
                primero[simbolo].add('ε')
        return primero[simbolo]

    for simbolo in todos_los_simbolos:
        obtener_primero(simbolo)
    return primero


def Siguientes(gramatica, primero, simbolo_inicial):
    siguiente={}
    for nt in gramatica:
        siguiente[nt]=set()
    siguiente[simbolo_inicial].add('$')

    cambiado=True
    while cambiado:
        cambiado=False
        for nt in gramatica:
            for produccion in gramatica[nt]:
                for i, simbolo in enumerate(produccion):
                    if simbolo in gramatica:
                        rest=produccion[i + 1:]
                        antes=len(siguiente[simbolo])
                        if rest:
                            primero_rest=set()
                            for s in rest:
                                primeros_s=primero[s]
                                primero_rest.update(primeros_s - {'ε'})
                                if 'ε' not in primeros_s:
                                    break
                            else:
                                primero_rest.add('ε')
                            siguiente[simbolo].update(primero_rest - {'ε'})
                            if 'ε' in primero_rest:
                                siguiente[simbolo].update(siguiente[nt])
                        else:
                            siguiente[simbolo].update(siguiente[nt])
                        if len(siguiente[simbolo])>antes:
                            cambiado=True
    return siguiente


def Predicciones(gramatica, primero, siguiente):
    conjunto_prediccion={}
    for nt in gramatica:
        for prod in gramatica[nt]:
            regla=f"{nt} -> {' '.join(prod)}"
            pred=set()
            for s in prod:
                primeros_s=primero[s]
                pred.update(primeros_s - {'ε'})
                if 'ε' not in primeros_s:
                    break
            else:
                pred.add('ε')
            conjunto_prediccion[regla]= pred-{'ε'}
            if 'ε' in pred:
                conjunto_prediccion[regla].update(siguiente[nt])
    return conjunto_prediccion

def imprimir_gramatica_de_atributos(gramatica):
    print("--- Gramatica de Atributos ---\n")
    for nt, producciones in gramatica.items():
        for prod in producciones:
            regla=f"{nt} → {' '.join(prod)}"
            if nt=='Expr':
                accion="{ Expr.trad:=Term.trad + Expr_op.trad }"
            elif nt=='Expr_op':
                if '+' in prod:
                    accion="{ Expr_op.trad:=Term.trad + Expr_op1.trad }"
                elif '-' in prod:
                    accion="{ Expr_op.trad:=-Term.trad+ Expr_op1.trad }"
                else:
                    accion="{ Expr_op.trad:=0 }"
            elif nt=='Term':
                accion="{ Term.trad:=Fact.trad * Term_op.trad }"
            elif nt=='Term_op':
                if '*' in prod:
                    accion="{ Term_op.trad:= Fact.trad * Term_op1.trad }"
                elif '/' in prod:
                    accion="{ Term_op.trad:= Fact.trad / Term_op1.trad }"
                else:
                    accion="{ Term_op.trad:= 1 }"
            elif nt=='Fact':
                if 'Expr' in prod:
                    accion="{ Fact.trad:= Expr.trad }"
                elif 'num' in prod:
                    accion="{ Fact.trad:= valor(num.lexema) }"
                elif 'id' in prod:
                    accion="{ Fact.trad:= buscar(symtab, id.lexema) }"
                else:
                    accion=""
            else:
                accion=""
            print(f"{regla} {accion}")

def tokenize(expr):
    tokens=[]
    i=0
    while i<len(expr):
        c=expr[i]
        if c in ' \t\n':
            i+=1
            continue
        elif c.isdigit():
            num=c
            i+=1
            while i<len(expr) and expr[i].isdigit():
                num+=expr[i]
                i+=1
            tokens.append(('num', num))
        elif c.isalpha():
            ident=c
            i+=1
            while i<len(expr) and expr[i].isalnum():
                ident+=expr[i]
                i+=1
            tokens.append(('id', ident))
        elif c in '+-*/()':
            tokens.append((c, c))
            i+=1
        else:
            print("caracter inesperado:", c)
            i+=1
    tokens.append(('$', '$'))
    return tokens

class Num:
    def __init__(self, value):
        self.value=value

class Id:
    def __init__(self, name):
        self.name=name

class Op:
    def __init__(self, op, left, right):
        self.op=op
        self.left=left
        self.right=right
        self.val=None

class Parser:
    def __init__(self, tokens):
        self.tokens=tokens
        self.pos=0
        self.symtab={}  

    def mirar(self):
        return self.tokens[self.pos][0]

    def avance(self):
        t=self.tokens[self.pos]
        self.pos+=1
        return t

    def esperado(self, tipo):
        if self.mirar()==tipo:
            return self.avance()
        else:
            print("Error: se esperaba", tipo, "; se encontro", self.mirar())
            exit()

    def parse(self):
        node=self.expr()
        if self.mirar()!='$':
            print("Error: tokens extra al final")
        return node

    def expr(self):
        tnode=self.term()
        return self.expr_op(tnode)

    def expr_op(self, heredado):
        if self.mirar()=='+':
            self.avance()
            tnode=self.term()
            nodo=Op('+', heredado, tnode)
            return self.expr_op(nodo)
        elif self.mirar()=='-':
            self.avance()
            tnode=self.term()
            nodo=Op('-', heredado, tnode)
            return self.expr_op(nodo)
        else:
            return heredado

    def term(self):
        fnode=self.fact()
        return self.term_op(fnode)

    def term_op(self, heredado):
        if self.mirar()=='*':
            self.avance()
            fnode=self.fact()
            nodo=Op('*', heredado, fnode)
            return self.term_op(nodo)
        elif self.mirar()=='/':
            self.avance()
            fnode=self.fact()
            nodo=Op('/', heredado, fnode)
            return self.term_op(nodo)
        else:
            return heredado


    def fact(self):
        t=self.mirar()
        if t=='(':
            self.avance()
            node=self.expr()
            self.esperado(')')
            return node
        elif t=='num':
            valor=float(self.avance()[1])
            return Num(valor)
        elif t=='id':
            nombre=self.avance()[1]
            if nombre not in self.symtab:
                self.symtab[nombre]={'tipo': 'number', 'valor': None}
            return Id(nombre)
        else:
            print("Error: token inesperado", t)
            exit()

def evaluar(node, tabla):
    if isinstance(node, Num):
        return node.value
    elif isinstance(node, Id):
        if tabla[node.name]['valor'] is not None:
            return tabla[node.name]['valor']
        else:
            return None
    elif isinstance(node, Op):
        izq=evaluar(node.left, tabla)
        der=evaluar(node.right, tabla)
        if izq is None or der is None:
            node.val=None
            return None
        if node.op=='+':
            node.val= izq+der
        elif node.op=='-':
            node.val= izq-der
        elif node.op== '*':
            node.val= izq*der
        elif node.op == '/':
            node.val= izq/der
        return node.val

def imprimir_ast(node, tabla, prefijo="", es_ultimo=True):
    rama="└─" if es_ultimo else "├─"
    if isinstance(node, Num):
        print(f"{prefijo}{rama}num({node.value})")
    elif isinstance(node, Id):
        val=tabla[node.name]['valor']
        print(f"{prefijo}{rama}id({node.name}) valor={val}")
    elif isinstance(node, Op):
        print(f"{prefijo}{rama}op({node.op}) val={node.val}")
        hijos=[node.left, node.right]
        for i, hijo in enumerate(hijos):
            es_ult=(i== len(hijos)-1)
            nuevo_prefijo= prefijo+("   " if es_ultimo else "│  ")
            imprimir_ast(hijo, tabla, nuevo_prefijo, es_ult)

def ejecutar(expresion, valores=None):
    print(expresion)
    tokens=tokenize(expresion)
    parser=Parser(tokens)
    ast=parser.parse()

    if valores:
        for k in valores:
            if k in parser.symtab:
                parser.symtab[k]['valor']=valores[k]

    evaluar(ast, parser.symtab)

    print("\ntabla de simbolos:")
    for k in parser.symtab:
        print(" ", k, ":", parser.symtab[k])

    print("\nAST decorado:")
    imprimir_ast(ast, parser.symtab)

    print("\nresultado:", getattr(ast, 'val', None))
imprimir_gramatica_de_atributos(gramatica)
ejecutar("a+3 *(b - 2)", {'a': 10, 'b': 5})
