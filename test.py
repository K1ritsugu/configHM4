import unittest
import subprocess
import os
import json
import tempfile
import shutil


class TestEVM(unittest.TestCase):
    def setUp(self):
        # Создаём временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()

        self.assembler = os.path.abspath('assembler.py')
        self.interpreter = os.path.abspath('interpreter.py')

    def tearDown(self):
        # Удаляем временную директорию после тестов
        shutil.rmtree(self.test_dir)

    def assemble_command(self, asm_content, asm_filename):
        # Записываем asm_content в файл
        asm_path = os.path.join(self.test_dir, asm_filename)
        with open(asm_path, 'w', encoding='utf-8') as f:
            f.write(asm_content)

        # Определяем пути для бинарного файла и лога
        bin_path = os.path.join(self.test_dir, asm_filename.replace('.asm', '.bin'))
        log_path = os.path.join(self.test_dir, asm_filename.replace('.asm', '_log.json'))

        # Запускаем assembler.py
        cmd = [
            'python', self.assembler,
            '-i', asm_path,
            '-o', bin_path,
            '-l', log_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Assembler Error: {result.stderr}")

        return bin_path, log_path

    def run_interpreter(self, bin_path, memstart, memend):
        # Определяем путь для результата
        result_path = os.path.join(self.test_dir, 'result.json')

        cmd = [
            'python', self.interpreter,
            '-i', bin_path,
            '-r', result_path,
            '--memstart', str(memstart),
            '--memend', str(memend)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Interpreter Error: {result.stderr}")

        with open(result_path, 'r', encoding='utf-8') as f:
            mem_result = json.load(f)

        return mem_result

    def test_load_const(self):
        # Ассемблерная команда: LOAD_CONST 52 473 + STORE_MEM 500 52
        asm_content = "LOAD_CONST 52 473\nSTORE_MEM 500 52\n"
        bin_path, log_path = self.assemble_command(asm_content, 'load_const_test.asm')

        # Запуск интерпретатора с memstart=500 и memend=500
        mem_result = self.run_interpreter(bin_path, 500, 500)

        # Проверяем, что mem[500] = 473
        self.assertEqual(mem_result[0], 473, "LOAD_CONST: mem[500] должен содержать 473")

    def test_load_mem(self):
        # Ассемблерная команда: LOAD_MEM 41 387 + STORE_MEM 501 41
        asm_content = "LOAD_CONST 0 100\nSTORE_MEM 387 0\nLOAD_MEM 41 387\nSTORE_MEM 501 41\n"
        bin_path, log_path = self.assemble_command(asm_content, 'load_mem_test.asm')

        mem_result = self.run_interpreter(bin_path, 501, 501)

        self.assertEqual(mem_result[0], 100, "LOAD_MEM: mem[501] должен содержать 100")

    def test_store_mem(self):
        # Ассемблерная команда: LOAD_CONST 5 123 + STORE_MEM 956 5
        asm_content = "LOAD_CONST 5 123\nSTORE_MEM 956 5\n"
        bin_path, log_path = self.assemble_command(asm_content, 'store_mem_test.asm')

        mem_result = self.run_interpreter(bin_path, 956, 956)

        self.assertEqual(mem_result[0], 123, "STORE_MEM: mem[956] должен содержать 123")

    def test_eq(self):
        # Ассемблерная команда: LOAD_CONST 60 50 + LOAD_CONST 9 50 + EQ 60 9 + STORE_MEM 502 60
        asm_content = "LOAD_CONST 60 50\nLOAD_CONST 9 50\nEQ 60 9\nSTORE_MEM 502 60\n"
        bin_path, log_path = self.assemble_command(asm_content, 'eq_test.asm')

        mem_result = self.run_interpreter(bin_path, 502, 502)

        self.assertEqual(mem_result[0], 1, "EQ: mem[502] должен содержать 1 (равны)")

        asm_content_neq = "LOAD_CONST 60 50\nLOAD_CONST 9 40\nEQ 60 9\nSTORE_MEM 503 60\n"
        bin_path_neq, log_path_neq = self.assemble_command(asm_content_neq, 'eq_test_neq.asm')

        mem_result_neq = self.run_interpreter(bin_path_neq, 503, 503)

        self.assertEqual(mem_result_neq[0], 0, "EQ: mem[503] должен содержать 0 (не равны)")

    def test_full_program(self):
        # Тестовая программа: поэлементное сравнение двух векторов длины 8
        asm_content = """
        # Загрузка констант: адреса начала векторов
        LOAD_CONST 10 100    # Регистр 10 = 100 (начало первого вектора)
        LOAD_CONST 11 200    # Регистр 11 = 200 (начало второго вектора)

        # Сравнение 1-го элемента
        LOAD_MEM 1 100        # R1 = mem[100]
        LOAD_MEM 2 200        # R2 = mem[200]
        EQ 1 2                # R1 = (R1 == R2) ? 1 : 0
        STORE_MEM 200 1        # mem[200] = R1

        # Сравнение 2-го элемента
        LOAD_MEM 1 101
        LOAD_MEM 2 201
        EQ 1 2
        STORE_MEM 201 1

        # Сравнение 3-го элемента
        LOAD_MEM 1 102
        LOAD_MEM 2 202
        EQ 1 2
        STORE_MEM 202 1

        # Сравнение 4-го элемента
        LOAD_MEM 1 103
        LOAD_MEM 2 203
        EQ 1 2
        STORE_MEM 203 1

        # Сравнение 5-го элемента
        LOAD_MEM 1 104
        LOAD_MEM 2 204
        EQ 1 2
        STORE_MEM 204 1

        # Сравнение 6-го элемента
        LOAD_MEM 1 105
        LOAD_MEM 2 205
        EQ 1 2
        STORE_MEM 205 1

        # Сравнение 7-го элемента
        LOAD_MEM 1 106
        LOAD_MEM 2 206
        EQ 1 2
        STORE_MEM 206 1

        # Сравнение 8-го элемента
        LOAD_MEM 1 107
        LOAD_MEM 2 207
        EQ 1 2
        STORE_MEM 207 1
        """
        bin_path, log_path = self.assemble_command(asm_content, 'full_program_test.asm')

        mem_result = self.run_interpreter(bin_path, 200, 207)

        expected = [1, 1, 0, 1, 0, 1, 1, 0]
        self.assertEqual(mem_result, expected, f"Full Program: Ожидалось {expected}, Получено {mem_result}")


if __name__ == '__main__':
    unittest.main()
