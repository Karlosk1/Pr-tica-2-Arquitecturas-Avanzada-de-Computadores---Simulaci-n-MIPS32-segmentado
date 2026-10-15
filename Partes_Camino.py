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


class IFID:
    def __init__(self):
        self.instruccion = None
        self.PC = None


class IDEX:
    def __init__(self):
        self.tipo_Inst = None
        self.reg_Dst_Add = None
        self.registro1_Name = None
        self.registro2_Name = None
        self.registro1_Val = None
        self.registro2_Val = None
        self.offset = None


class EXMEM:
    def __init__(self):
        self.tipo_Inst = None
        self.reg_Dst_Add = None
        self.registro1_Name = None
        self.registro2_Name = None
        self.registro2_Val = None
        self.ALU_Valor = None


class MEMWB:
    def __init__(self):
        self.tipo_Inst = None
        self.valor_WB = None
        self.reg_Dst_Add = None