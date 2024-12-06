# Предполагаем, что R1, R2 - регистры для работы
# LOAD_MEM B C -> R[B] = mem[C]
# STORE_MEM B C -> mem[B] = R[C]
# EQ B C -> R[B] = (R[B] == R[C])?1:0

# i загружаем в регистр для вычисления адресов. Для простоты сделаем заранее.
# Загрузим константы 100 (начало первого вектора) и 200 (второго) в регистры.
LOAD_CONST 10 100   # R[10]=100
LOAD_CONST 11 200   # R[11]=200

# i в 0..7
# R[12] = i=0

LOAD_MEM 1 100
LOAD_MEM 2 200
EQ 2 1
STORE_MEM 200 2

LOAD_MEM 1 101
LOAD_MEM 2 201
EQ 2 1
STORE_MEM 201 2

LOAD_MEM 1 102
LOAD_MEM 2 202
EQ 2 1
STORE_MEM 202 2

LOAD_MEM 1 103
LOAD_MEM 2 203
EQ 2 1
STORE_MEM 203 2

LOAD_MEM 1 104
LOAD_MEM 2 204
EQ 2 1
STORE_MEM 204 2

LOAD_MEM 1 105
LOAD_MEM 2 205
EQ 2 1
STORE_MEM 205 2

LOAD_MEM 1 106
LOAD_MEM 2 206
EQ 2 1
STORE_MEM 206 2

LOAD_MEM 1 107
LOAD_MEM 2 207
EQ 2 1
STORE_MEM 207 2
