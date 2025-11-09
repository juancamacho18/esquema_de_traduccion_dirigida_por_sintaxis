# ESQUEMA DE TRADUCCION DIRIGIDA POR SINTAXIS
Este programa implementa algoritmos de traduccion dirigida por sintaxis de un gramatica libre de contexto para realizar operaciones aritmetica de suma, resta, multiplicaicon y division con numeros y variables, además de usar 
algoritmos de calculos de conjuntos, parseo y muestra de gramatica de atributos


# Explicación
Para el desarrollo de este EDTS se tuve en cuenta y se implementaron algunos algoritmos que lo apoyaran, lo primero de todo
• 1.Desarrollo de la gramatica

    Expr-> Term Expr_op
    Expr_op-> + Term Expr_op
    Expr_op-> - Term Expr_op
    Expr_op-> ε
    Term-> Fact Term_op
    Term_op-> * Fact Term_op 
    Term_op-> / Fact Term_op 
    Term_op-> ε
    Fact-> ( Expr )
    Fact-> num
    Fact-> id
De esta manera fue que se definio la gramatica de manera basica para el trabajo de operaciones aritmeticas, esta es aceptada para parseo LL(1), al no usra recursividad a la izquierda ni ambiguedad para el desarrollo a lo largo en el EDTS.

• 2.Definir atributos

De la gramatica establecida, se definen los atributos dependiendo el simbolo de esta manera 
| Símbolo | Atributo |	Tipo  |  	
|---------------|-------|-------|
| Expr	 | trad |	Sintetizado	|
| Term	 | trad |	Sintetizado |	
| Fact |	trad |	Sintetizado |	
| Id | valor |	Sintetizado |

• 3.Calcular los conjuntos: F,S,P

Se calcula los conjuntos de primero, siguientes y de predccion para poder usar en el analisis predictivo, de acuerdo a la gramatica, los conjuntos quedan asi:

    Primeros:
    Primero(Expr)= {'id', '(', 'num'}
    Primero(Expr_op)= {'ε', '+', '-'}
    Primero(Term)= {'id', '(', 'num'}
    Primero(Term_op)= {'/', '*', 'ε'}
    Primero(Fact)= {'id', '(', 'num'}
    
    Siguientes:
    Siguiente(Expr)= {'$', ')'}
    Siguiente(Expr_op)= {'$', ')'}
    Siguiente(Term)= {'$', '-', '+', ')'}
    Siguiente(Term_op)= {'$', '-', '+', ')'}
    Siguiente(Fact)= {'*', '-', '+', '/', ')', '$'}
    
    Conjuntos de prediccion:
    Expr -> Term Expr_op {'id', '(', 'num'}
    Expr_op -> + Term Expr_op {'+'}
    Expr_op -> - Term Expr_op {'-'}
    Expr_op -> ε {'$', ')'}
    Term -> Fact Term_op {'id', '(', 'num'}
    Term_op -> * Fact Term_op {'*'}
    Term_op -> / Fact Term_op {'/'}
    Term_op -> ε {')', '$', '+', '-'}
    Fact -> ( Expr ) {'('}
    Fact -> num {'num'}
    Fact -> id {'id'}
  
• 4.Generar el AST decorado

Al ejecutar el programa, dependiendo de la expresión, se hara una construcción de un arból sintactico con la traducción por sintaxis, mostrando incluso el resultado de este
un ejemplo de ua expresion y como se muestra el arbol es asi:
>2+1
>
>AST decorado:
>
>└─op(+) val=3.0
>
>       ├─num(2.0)
>
>       └─num(1.0)
>

Generando nodos  ya sea de una operación o un numero, indicando el valor o el tipo de este mismo y mostrando el resultado de dicha operación en la raiz del arbol
• 5.Generar la tabla de símbolos

El programa mantiene una tabla de símbolos que almacena información de las variables encontradas en la expresión, por ejemplo así:

| Identificador	| Tipo	| Valor |
|---------------|-------|-------|
| a | number	| 10 |
| b	| number |	5 |

Esta estructura permite manejar expresiones que combinan números y variables.

• 6.Generar la gramatica de atributos

Finalmente se realiza la contrucción de la gramatica de atributos, usando las reglas  y los propios atributos definidos, para generar las reglas semanticas que conectan para cada regla de la gramatica, las reglas según la gramatica quedan definidas de esta manera:

    Expr → Term Expr_op { Expr.trad:=Term.trad + Expr_op.trad }
    Expr_op → + Term Expr_op { Expr_op.trad:=Term.trad + Expr_op1.trad }
    Expr_op → - Term Expr_op { Expr_op.trad:=-Term.trad+ Expr_op1.trad }
    Expr_op → ε { Expr_op.trad:=0 }
    Term → Fact Term_op { Term.trad:=Fact.trad * Term_op.trad }
    Term_op → * Fact Term_op { Term_op.trad:= Fact.trad * Term_op1.trad }
    Term_op → / Fact Term_op { Term_op.trad:= Fact.trad / Term_op1.trad }
    Term_op → ε { Term_op.trad:= 1 }
    Fact → ( Expr ) { Fact.trad:= Expr.trad }
    Fact → num { Fact.trad:= valor(num.lexema) }
    Fact → id { Fact.trad:= buscar(symtab, id.lexema) }

Y cumpliendo con estas condiciones, es como se tiene todo el EDTS para el programa, y para ejecutarlo, dentro del programa se hace un llamado a la funcion de ejecutar y agrega como parametro una cadena con la 
expresión a utilizar, además de incluir la definicion y asignacion de valor a una variable, en caso de estar usando una en la cadena ingresada, y al ejecutarlo, el programa generara la tabla de simbolos de la cadena (si utiliza variables) y el AST decorado de la cadena
junto al reusltado de este mismo, así.
>ejecutar("12/(4-2)+x", {'x':7})

# Pruebas y ejemplos
A continuación, se muestra algunas pruebas con algunas expresiones junto a los resultados que estos mostro el programa al ejecutarlos:
# Ejemplo 1: a+3 *(b-2) ; a: 10, b: 5
    tabla de simbolos:
      a : {'tipo': 'number', 'valor': 10}
      b : {'tipo': 'number', 'valor': 5}
    
    AST decorado:
    └─op(+) val=19.0
       ├─id(a) valor=10
       └─op(*) val=9.0
          ├─num(3.0)
          └─op(-) val=3.0
             ├─id(b) valor=5
             └─num(2.0)
    
    resultado: 19.0
  
# Ejemplo 2: (1+2)*(3+4)

    tabla de simbolos:
        
        AST decorado:
        └─op(*) val=21.0
           ├─op(+) val=3.0
           │  ├─num(1.0)
           │  └─num(2.0)
           └─op(+) val=7.0
              ├─num(3.0)
              └─num(4.0)
        
        resultado: 21.0

# Ejemplo 3: 12/(4-2)+x ; x:7

     tabla de simbolos:
      x : {'tipo': 'number', 'valor': 7}
    
    AST decorado:
    └─op(+) val=13.0
       ├─op(/) val=6.0
       │  ├─num(12.0)
       │  └─op(-) val=2.0
       │     ├─num(4.0)
       │     └─num(2.0)
       └─id(x) valor=7
    
    resultado: 13.0

# Ejemplo 4: (1+2)*(3+4)
    tabla de simbolos:
        
        AST decorado:
        └─op(*) val=21.0
           ├─op(+) val=3.0
           │  ├─num(1.0)
           │  └─num(2.0)
           └─op(+) val=7.0
              ├─num(3.0)
              └─num(4.0)
        
        resultado: 21.0
      
# Ejemplo 5: a+4*8-b/c ; a:2, b:4, c:8

     tabla de simbolos:
          a : {'tipo': 'number', 'valor': 2}
          b : {'tipo': 'number', 'valor': 4}
          c : {'tipo': 'number', 'valor': 8}
        
        AST decorado:
        └─op(-) val=33.5
           ├─op(+) val=34.0
           │  ├─id(a) valor=2
           │  └─op(*) val=32.0
           │     ├─num(4.0)
           │     └─num(8.0)
           └─op(/) val=0.5
              ├─id(b) valor=4
              └─id(c) valor=8
        
        resultado: 33.5
