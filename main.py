from CPU import *
## LA UC SE ELIGE LO QUE FUNCIONA EN LA ALU EN LA FASE EX
    ## Hay que proteger el registro de acoplamiento exmem hasta que termine el mem()
    ## La clase segmentacion tendra wb(), ex(), mem(), id(), if() y esta clase se inicializa en UC
    ##id recibe ifid y devuelve idex, iugal if recibe +pc tiene que devolver el valor a donde vamos y se guarda en ifid
    ## en ex() hay que actualizar el pc para que cuando lleguemos a if coja el salto
    ## Cada registro de acoplamiento será una clase
    ## ifid recibe la instruccion y el pc
    ## idex recibe la instruccion troceada por la uc, regdst(y valor), regcode, regcode2(si es addi es null)(NOMBRES), etiqueta, offset, reg1,reg2 (numeros) y regdst(NOMBRE) se guarda y se arrastra para los cortocircuitos
    ##en exmem recibe el tipo de instruccion, offset, regDst (y valor), valor de la ALU, reg1 y reg2
    ## memwb valor, regdst(y su valor)
    ##normalmente se actualiza al final de cada fase

if __name__ == "__main__":
    # 1. Construimos el procesador físico
    mi_procesador = CPU()

    # 2. Cargamos los archivos de código (Asegúrate de crearlos en tu misma carpeta)
    mi_procesador.cargar_archivos("instrucciones.txt", "datos.txt")

    # 3. Arrancamos el pipeline
    mi_procesador.simulate()

    # 4. Comprobamos los resultados finales
    print("\n--- RESULTADOS FINALES ---")
    print("Valor del registro $t1:", mi_procesador.UP.banco_registros.registros["$t1"])
    print("Valor del registro $t2:", mi_procesador.UP.banco_registros.registros["$t2"])
    print("Valor del registro $t3:", mi_procesador.UP.banco_registros.registros["$t3"])