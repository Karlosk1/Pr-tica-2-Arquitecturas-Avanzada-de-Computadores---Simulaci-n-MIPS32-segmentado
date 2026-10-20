class Mux:
    def operar(self, signal, entrada0, entrada1, entrada2):
        if signal == 0:
            return entrada0
        elif signal == 1:
            return entrada1
        elif signal == 2:
            return entrada2
        else:
            print(f"Señal de selección '{signal}' fuera de rango soportado.")
            return None


class Memoria_Inst:
    def __init__(self, instrucciones_iniciales, etiquetas_iniciales):
        if instrucciones_iniciales is None:
            self.memoria = {}
        else:
            self.memoria = instrucciones_iniciales

        if etiquetas_iniciales is None:
            self.tabla_simbolos = {}
        else:
            self.tabla_simbolos = etiquetas_iniciales

    def leer_instruccion(self, pc):
        return self.memoria.get(pc, "nop")

    def agregar_etiqueta(self, nombre_etiqueta, direccion_pc):
        self.tabla_simbolos[nombre_etiqueta] = direccion_pc

    def obtener_direccion_etiqueta(self, nombre_etiqueta):
        if nombre_etiqueta in self.tabla_simbolos:
            return self.tabla_simbolos[nombre_etiqueta]
        else:
            raise ValueError(f"Error: La etiqueta '{nombre_etiqueta}' no existe.")


class Memoria_Data:
    def __init__(self, datos_iniciales):
        if datos_iniciales is None:
            self.memoria = {}
        else:
            self.memoria = datos_iniciales

    def leer_dato(self, address, mem_read):
        if mem_read:
            return self.memoria.get(address, 0)
        return 0

    def escribir_dato(self, address, write_data, mem_write):
        if mem_write:
            self.memoria[address] = write_data


class Registros:
    def __init__(self):
        self.registros = {
            "$zero": 0x00000000, "$at": 0, "$v0": 0, "$v1": 0, "$a0": 0, "$a1": 0, "$a2": 0, "$a3": 0,
            "$t0": 0, "$t1": 0, "$t2": 0, "$t3": 0, "$t4": 0, "$t5": 0, "$t6": 0, "$t7": 0,
            "$s0": 0, "$s1": 0, "$s2": 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0,
            "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0, "$gp": 0, "$sp": 0, "$fp": 0, "$ra": 0,
            "pc": 0, "hi": 0, "lo": 0
        }


class ALU:
    def __init__(self):
        self.zero = False

    def add_calculo(self, entrada1, entrada2):
        return entrada1 + entrada2

    def sub_calculo(self, entrada1, entrada2):
        resultado = entrada1 - entrada2
        self.zero = (resultado == 0)
        return resultado

    def and_calculo(self, entrada1, entrada2):
        return entrada1 & entrada2

    def or_calculo(self, entrada1, entrada2):
        return entrada1 | entrada2

    def xor_calculo(self, entrada1, entrada2):
        return entrada1 ^ entrada2

    def slt_calculo(self, entrada1, entrada2):
        if entrada1 < entrada2:
            return 1
        else:
            return 0

    def sgt_calculo(self, entrada1, entrada2):
        if entrada1 > entrada2:
            return 0
        else:
            return 1


class Segmentacion:
    pass


class ForwardingUnit:
    def get_forward_alu(self, id_ex_rs, id_ex_rt, ex_mem_rd, mem_wb_rd, ex_mem_inst, mem_wb_inst):
        forward_a = 0
        forward_b = 0
        inst_escritura = ["add", "sub", "and", "or", "xor", "nor", "slt", "sll", "addi", "lw", "lui"]

        if ex_mem_inst in inst_escritura and ex_mem_rd not in [None, "$zero"]:
            if ex_mem_rd == id_ex_rs: forward_a = 2
            if ex_mem_rd == id_ex_rt: forward_b = 2

        if mem_wb_inst in inst_escritura and mem_wb_rd not in [None, "$zero"]:
            if mem_wb_rd == id_ex_rs and forward_a != 2: forward_a = 1
            if mem_wb_rd == id_ex_rt and forward_b != 2: forward_b = 1

        return forward_a, forward_b


class IFID:
    def __init__(self):
        self.instruccion = None
        self.PC = None


class IDEX:
    def __init__(self):
        self.tipo_Inst = None
        self.rd = None
        #borrar nombres
        self.rs = None
        self.rt = None
        self.val_rs = None
        self.val_rt = None
        #Meter pc
        self.pc = None
        self.offset = None


class EXMEM:
    def __init__(self):
        self.tipo_Inst = None
        self.rd = None
        #borrar nombres
        self.rs = None
        self.rt = None
        self.val_rt = None
        self.ALU_Valor = None
        self.pc = None


class MEMWB:
    def __init__(self):
        self.tipo_Inst = None
        self.valor_WB = None
        self.rd = None
        self.pc = None




        #QUE ES LA SEGMENTACION? SOLO SE PUEDE MAX 8 FASES DE SEGMENTACION, la mayoria en mem y ex