## CPU contiene todo, dentro de esta tendra una unidad de proceso y una unidad de control
## La UP tiene memorias, registros, ALU
## LA UC tiene registros de acoplamiento y clase segmentacion y luego dentro de segmentacion id,if,ex,mem y wb
## Cuando if da la direccion de memoria, tu lo buscas en memoria y la memoria te devuelve un string, eso se lo pasas al ID luego esa la parsea,
# y busca la memoria estos datos
#IMPLEMENTACION ALTERNATIVA ALU
#def __init__(self):
        # El estado interno resultante tras una operación
#        self.resultado = 0
 #       self.zero = 0

#  def operar(self, entrada1, entrada2, alu_control):
        # El string 'alu_control' simula los bits que entran desde la unidad de control a la ALU
   #     if alu_control == "0000":    # AND
    #        self.resultado = entrada1 & entrada2
     #   elif alu_control == "0001":  # OR
      #      self.resultado = entrada1 | entrada2
       # elif alu_control == "0010":  # ADD
        #    self.resultado = entrada1 + entrada2
        #elif alu_control == "0110":  # SUB (Resta)
        #    self.resultado = entrada1 - entrada2
        #elif alu_control == "0111":  # SLT (Set on Less Than)
        #    self.resultado = 1 if entrada1 < entrada2 else 0
        #elif alu_control == "1100":  # NOR (Ejemplo adicional común)
        #    self.resultado = ~(entrada1 | entrada2)
        #else:
        #    self.resultado = 0

        # Generación física de la señal Zero
        #if self.resultado == 0:
        #    self.zero = 1
        #else:
        #    self.zero = 0

        # La ALU siempre escupe ambas señales al mismo tiempo
        #return self.resultado, self.zero#

## ifid recibe la instruccion y el pc
    ## idex recibe la instruccion troceada por la uc, regdst(y valor), regcode, regcode2(si es addi es null)(NOMBRES), etiqueta, offset, reg1,reg2 (numeros) y regdst(NOMBRE) se guarda y se arrastra para los cortocircuitos
    ##en exmem recibe el tipo de instruccion, offset, regDst (y valor), valor de la ALU, reg1 y reg2
    ## memwb valor, regdst(y su valor)
    ##normalmente se actualiza al final de cada fase
import re
from Partes_Camino import *


class Parseador:
    def __init__(self, mem_inst, mem_data):
        self.mem_inst = mem_inst
        self.mem_data = mem_data

    def cargar_memoria_instrucciones(self, nombre_archivo):
        pc_actual = 0x00400000
        lineas_codigo = []

        try:
            with open(nombre_archivo, 'r') as f:
                for linea in f:
                    linea = linea.split('#')[0].strip()

                    if not linea:
                        continue

                    if linea.endswith(':'):
                        etiqueta = linea[:-1].strip()
                        self.mem_inst.agregar_etiqueta(etiqueta, pc_actual)
                        continue
                    lineas_codigo.append([pc_actual, linea])
                    pc_actual += 4

            for pc, linea in lineas_codigo:
                partes = re.split(r'[,\s]+', linea)
                opcode = partes[0]

                if opcode in ['j', 'jal', 'beq', 'bne']:
                    ultima_parte = partes[-1]
                    if ultima_parte in self.mem_inst.tabla_simbolos:
                        direccion_real = self.mem_inst.tabla_simbolos[ultima_parte]
                        partes[-1] = str(direccion_real)
                        linea = ' '.join(partes)
                self.mem_inst.memoria[pc] = linea

        except FileNotFoundError:
            print(f"Error: El archivo {nombre_archivo} no se encontró.")

    def cargar_memoria_datos(self, nombre_archivo):
        direccion_base = 0x10010000
        direccion_actual = direccion_base

        try:
            with open(nombre_archivo, 'r') as f:
                for linea in f:
                    linea = linea.split('#')[0].strip()
                    if not linea:
                        continue

                    if ':' in linea:
                        partes = linea.split(':', 1)
                        contenido = partes[1].strip()

                        if contenido.startswith('.word'):
                            texto_sin_directiva = contenido.replace('.word', '')
                            trozos_texto = texto_sin_directiva.split(',')
                            valores = []

                            for v in trozos_texto:
                                texto_limpio = v.strip()
                                numero_entero = int(texto_limpio, 0)
                                valores.append(numero_entero)

                            for valor in valores:
                                self.mem_data.escribir_dato(direccion_actual, valor, True)
                                direccion_actual += 4
                        elif contenido.startswith('.asciiz'):
                            pass
        except FileNotFoundError:
            print(f"Error: El archivo {nombre_archivo} no se encontró.")


class CPU:
    def __init__(self):
        self.UP = UP()
        self.UC = UC(self.UP)
        self.parseador = Parseador(self.UP.mem_inst, self.UP.mem_data)

    def cargar_archivos(self, archivo_instrucciones, archivo_datos):
        self.parseador.cargar_memoria_instrucciones(archivo_instrucciones)
        self.parseador.cargar_memoria_datos(archivo_datos)
        self.UP.banco_registros.registros["pc"] = 0x00400000

    def simulate(self):
        ciclo = 0
        fin = False

        print("Iniciando simulación Procesador Segmentado...")

        while not fin:
            ciclo += 1

            # 1. EJECUCION DEL PIPELINE
            self.fase_wb()
            ex_aux = self.fase_ex()
            self.fase_mem()

            self.UC.ex_mem = ex_aux

            # ID devuelve True si necesita inyectar una burbuja
            stall = self.fase_id()

            # Si hay burbuja, IF no se ejecuta
            if not stall:
                self.fase_if()

            # 2. IMPRESION DEL ESTADO
            print(f"--- Ciclo {ciclo} ---")
            print(f"IF/ID  : {self.UC.if_id.instruccion}")
            print(f"ID/EX  : {self.UC.id_ex.tipo_Inst}")
            print(f"EX/MEM : {self.UC.ex_mem.tipo_Inst}")
            print(f"MEM/WB : {self.UC.mem_wb.tipo_Inst}")
            print(f"PC     : {hex(self.UP.banco_registros.registros['pc'])}")
            print("-" * 25)

            # 3. CONDICION DE PARADA
            if (self.UC.if_id.instruccion in [None, "nop"] and
                    self.UC.id_ex.tipo_Inst in [None, "nop"] and
                    self.UC.ex_mem.tipo_Inst in [None, "nop"] and
                    self.UC.mem_wb.tipo_Inst in [None, "nop"]):
                print(f"Simulación terminada correctamente en el ciclo {ciclo}.")
                fin = True

    def imprimir_estado_memoria(self):
        etiquetas_inversas = {}
        for nombre, direccion in self.UP.mem_inst.tabla_simbolos.items():
            etiquetas_inversas[direccion] = nombre

        print("=" * 74)
        print(f"{'Dirección':<14} | {'Etiqueta':<16} | Instrucción")
        print("-" * 74)

        direcciones_ordenadas = sorted(self.UP.mem_inst.memoria.keys())

        for pc in direcciones_ordenadas:
            inst_str = self.UP.mem_inst.memoria[pc]
            etiqueta = etiquetas_inversas.get(pc, "")
            pc_formateado = f"0x{pc:08x}"
            print(f"{pc_formateado:<14} | {etiqueta:<16} | {inst_str}")

        print("=" * 74)

    def fase_if(self):
        pc_actual = self.UP.banco_registros.registros["pc"]
        nueva_instruccion = self.UP.mem_inst.leer_instruccion(pc_actual)

        self.UC.if_id.instruccion = nueva_instruccion
        self.UC.if_id.PC = pc_actual

        self.UP.banco_registros.registros["pc"] += 4

    def fase_id(self):
        instruccion_str = self.UC.if_id.instruccion

        if instruccion_str is None or instruccion_str == "nop":
            self.UC.id_ex.tipo_Inst = "nop"
            return False

        partes = re.split(r'[,\s]+', instruccion_str)
        opcode = partes[0]
        rs, rt, rd, imm = None, None, None, None

        if opcode in ['add', 'sub', 'and', 'or', 'xor', 'nor', 'slt']:
            rd = partes[1] if len(partes) > 1 else None
            rs = partes[2] if len(partes) > 2 else None
            rt = partes[3] if len(partes) > 3 else None

        elif opcode == 'sll':
            rd = partes[1] if len(partes) > 1 else None
            rs = partes[2] if len(partes) > 2 else None
            imm = partes[3] if len(partes) > 3 else None
            if imm:
                try:
                    imm = int(imm, 0)
                except ValueError:
                    pass

        elif opcode in ['addi', 'beq', 'bne']:
            rt = partes[1] if len(partes) > 1 else None
            rs = partes[2] if len(partes) > 2 else None
            imm = partes[3] if len(partes) > 3 else None
            if imm:
                try:
                    imm = int(imm, 0)
                except ValueError:
                    print(f"-> [ALERTA ID] Etiqueta o inmediato no resuelto: '{imm}'. Convirtiendo a NOP.")
                    self.UC.id_ex.tipo_Inst = "nop"
                    return False

        elif opcode in ['lw', 'sw']:
            rt = partes[1] if len(partes) > 1 else None
            if len(partes) > 2:
                match = re.match(r'(-?\d+)\((.*?)\)', partes[2])
                if match:
                    imm = int(match[1], 0)
                    rs = match[2]

        elif opcode == 'lui':
            rt = partes[1] if len(partes) > 1 else None
            if len(partes) > 2:
                imm = int(partes[2], 0)

        elif opcode == 'j':
            imm = partes[1] if len(partes) > 1 else None
            if imm is not None:
                try:
                    imm = int(imm, 0)
                except ValueError:
                    print(f"-> [ALERTA ID] Etiqueta no resuelta: '{imm}'. Ignorando salto.")
                    self.UC.id_ex.tipo_Inst = "nop"
                    return False

        if opcode in ["add", "sub", "slt", "and", "or", "nor", "xor"]:
            regBase1 = rs
            regBase2 = rt
            regDst = rd
            offset = None

        elif opcode == "sll":
            regBase1 = rs
            regBase2 = None
            regDst = rd
            offset = imm

        elif opcode == "j":
            self.UP.banco_registros.registros["pc"] = imm
            self.UC.id_ex.tipo_Inst = "nop"
            return False

        else:
            regBase1 = rs
            regBase2 = rt
            regDst = rt
            offset = imm

        offset_procesado = self.extender_signo(offset)

        # UNIDAD DE DETECCION DE RIESGOS - BURBUJAS
        stall = False
        if self.UC.ex_mem.tipo_Inst == "lw":
            if self.UC.ex_mem.reg_Dst_Add in [regBase1, regBase2] and self.UC.ex_mem.reg_Dst_Add not in [None, "$zero"]:
                stall = True

        val_reg1 = self.UP.banco_registros.registros[regBase1] if regBase1 else 0
        val_reg2 = self.UP.banco_registros.registros[regBase2] if regBase2 else 0

        instrucciones_escritura = ["add", "sub", "and", "or", "xor", "nor", "slt", "sll", "addi", "lw", "lui"]

        # CORTOCIRCUITOS EXCLUSIVOS PARA RESOLVER SALTOS EN ID
        if opcode in ["beq", "bne"]:
            # Corto desde EX/MEM
            if self.UC.ex_mem.tipo_Inst in instrucciones_escritura:
                if self.UC.ex_mem.reg_Dst_Add in [regBase1, regBase2] and self.UC.ex_mem.reg_Dst_Add not in [None,
                                                                                                             "$zero"]:
                    if self.UC.ex_mem.tipo_Inst == "lw":
                        stall = True
                    else:
                        if self.UC.ex_mem.reg_Dst_Add == regBase1: val_reg1 = self.UC.ex_mem.ALU_Valor
                        if self.UC.ex_mem.reg_Dst_Add == regBase2: val_reg2 = self.UC.ex_mem.ALU_Valor

            # Corto desde MEM/WB
            if self.UC.mem_wb.tipo_Inst in instrucciones_escritura:
                if self.UC.mem_wb.reg_Dst_Add in [regBase1, regBase2] and self.UC.mem_wb.reg_Dst_Add not in [None,
                                                                                                             "$zero"]:
                    if self.UC.mem_wb.reg_Dst_Add == regBase1: val_reg1 = self.UC.mem_wb.valor_WB
                    if self.UC.mem_wb.reg_Dst_Add == regBase2: val_reg2 = self.UC.mem_wb.valor_WB

        if stall:
            print(f"-> [BURBUJA] Riesgo Load-Use detectado. Inyectando NOP.")
            self.UC.id_ex.tipo_Inst = "nop"
            return True

        # Ejecucion de saltos tras aplicar los cortos
        if opcode == "beq":
            if val_reg1 == val_reg2:
                self.UP.banco_registros.registros["pc"] = imm
                self.UC.id_ex.tipo_Inst = "nop"
                return False
        elif opcode == "bne":
            if val_reg1 != val_reg2:
                self.UP.banco_registros.registros["pc"] = imm
                self.UC.id_ex.tipo_Inst = "nop"
                return False

        self.UC.id_ex.tipo_Inst = opcode
        self.UC.id_ex.registro1_Name = regBase1
        self.UC.id_ex.registro2_Name = regBase2
        self.UC.id_ex.registro1_Val = val_reg1
        self.UC.id_ex.registro2_Val = val_reg2
        self.UC.id_ex.reg_Dst_Add = regDst
        self.UC.id_ex.offset = offset_procesado

        return False

    def extender_signo(self, offset_original):
        if offset_original is None:
            return None

        valor_16bits = offset_original & 0xFFFF

        if valor_16bits & 0x8000:
            return valor_16bits - 0x10000

        return valor_16bits

    def fase_ex(self):
        ex_aux = EXMEM()

        if self.UC.id_ex.tipo_Inst is None or self.UC.id_ex.tipo_Inst == "nop":
            ex_aux.tipo_Inst = "nop"
            return ex_aux

        ex_aux.tipo_Inst = self.UC.id_ex.tipo_Inst
        ex_aux.reg_Dst_Add = self.UC.id_ex.reg_Dst_Add
        ex_aux.registro1_Name = self.UC.id_ex.registro1_Name
        ex_aux.registro2_Name = self.UC.id_ex.registro2_Name

        val_reg1 = self.UC.id_ex.registro1_Val
        val_reg2 = self.UC.id_ex.registro2_Val

        rs = self.UC.id_ex.registro1_Name
        rt = self.UC.id_ex.registro2_Name
        instrucciones_escritura = ["add", "sub", "and", "or", "xor", "nor", "slt", "sll", "addi", "lw", "lui"]

        # UNIDAD DE CORTOCIRCUITOS EN EX - Forwarding
        # Prioridad 2: Rescatar datos de MEM/WB
        if self.UC.mem_wb.tipo_Inst in instrucciones_escritura:
            if self.UC.mem_wb.reg_Dst_Add == rs and rs not in [None, "$zero"]:
                val_reg1 = self.UC.mem_wb.valor_WB
            if self.UC.mem_wb.reg_Dst_Add == rt and rt not in [None, "$zero"]:
                val_reg2 = self.UC.mem_wb.valor_WB

        # Prioridad 1: Rescatar datos de EX/MEM (sobreescribe la prioridad 2 si ambos modifican el mismo registro)
        if self.UC.ex_mem.tipo_Inst in instrucciones_escritura and self.UC.ex_mem.tipo_Inst != "lw":
            if self.UC.ex_mem.reg_Dst_Add == rs and rs not in [None, "$zero"]:
                val_reg1 = self.UC.ex_mem.ALU_Valor
            if self.UC.ex_mem.reg_Dst_Add == rt and rt not in [None, "$zero"]:
                val_reg2 = self.UC.ex_mem.ALU_Valor

        # Es obligatorio actualizar registro2_Val para la instruccion SW que usa los datos en la fase MEM
        ex_aux.registro2_Val = val_reg2

        offset = self.UC.id_ex.offset
        resultado_calculo = 0

        operaciones_ALU = {
            "add": self.UP.alu.add_calculo,
            "sub": self.UP.alu.sub_calculo,
            "and": self.UP.alu.and_calculo,
            "or": self.UP.alu.or_calculo,
            "xor": self.UP.alu.xor_calculo,
            "slt": self.UP.alu.slt_calculo
        }

        if ex_aux.tipo_Inst in operaciones_ALU:
            funcion_a_ejecutar = operaciones_ALU[ex_aux.tipo_Inst]
            resultado_calculo = funcion_a_ejecutar(val_reg1, val_reg2)

        elif ex_aux.tipo_Inst in ["addi", "lw", "sw"]:
            resultado_calculo = self.UP.alu.add_calculo(val_reg1, offset)

        elif ex_aux.tipo_Inst == "lui":
            resultado_calculo = offset << 16

        elif ex_aux.tipo_Inst == "sll":
            resultado_calculo = val_reg1 << offset

        ex_aux.ALU_Valor = resultado_calculo
        return ex_aux

    def fase_mem(self):
        operacion = self.UC.ex_mem.tipo_Inst

        if operacion is None or operacion == "nop":
            self.UC.mem_wb.tipo_Inst = "nop"
            return

        self.UC.mem_wb.tipo_Inst = operacion
        self.UC.mem_wb.reg_Dst_Add = self.UC.ex_mem.reg_Dst_Add

        if operacion == "lw":
            direccion = self.UC.ex_mem.ALU_Valor
            dato_leido = self.UP.mem_data.leer_dato(direccion, True)
            self.UC.mem_wb.valor_WB = dato_leido

        elif operacion == "sw":
            direccion = self.UC.ex_mem.ALU_Valor
            dato_a_escribir = self.UC.ex_mem.registro2_Val
            self.UP.mem_data.escribir_dato(direccion, dato_a_escribir, True)
            self.UC.mem_wb.valor_WB = None

        else:
            self.UC.mem_wb.valor_WB = self.UC.ex_mem.ALU_Valor

    def fase_wb(self):
        operacion = self.UC.mem_wb.tipo_Inst

        if operacion is None or operacion == "nop":
            return

        if operacion in ["sw", "j", "beq", "bne"]:
            return

        registro_destino = self.UC.mem_wb.reg_Dst_Add
        dato_final = self.UC.mem_wb.valor_WB

        if registro_destino is not None and registro_destino != "$zero":
            self.UP.banco_registros.registros[registro_destino] = dato_final


class UP:
    def __init__(self):
        self.mem_inst = Memoria_Inst(None, None)
        self.mem_data = Memoria_Data(None)
        self.banco_registros = Registros()
        self.alu = ALU()
        self.mux = Mux()


class UC:
    def __init__(self, UP):
        self.UP = UP
        self.if_id = IFID()
        self.id_ex = IDEX()
        self.ex_mem = EXMEM()
        self.mem_wb = MEMWB()