# constants representing command types
CT_ARITHMETIC = 'CT_ARITHMETIC'
CT_PUSH = 'CT_PUSH'
CT_POP = 'CT_POP'
CT_LABEL = 'CT_LABEL'
CT_GOTO = 'CT_GOTO'
CT_IF = 'CT_IF'
CT_FUNCTION = 'CT_FUNCTION'
CT_RETURN = 'CT_RETURN'
CT_CALL = 'CT_CALL'

# constants represeting vm command keyword
C_ADD = 'add'
C_SUB = 'sub'
C_NEG = 'neg'
C_EQ = 'eq'
C_GT = 'gt'
C_LT = 'lt'
C_AND = 'and'
C_OR = 'or'
C_NOT = 'not'
C_PUSH = 'push'
C_POP = 'pop'

#
SEGMENT_LOCAL = 'local'
SEGMENT_ARGUMENT  = 'argument'
SEGMENT_STATIC  = 'static'
SEGMENT_CONSTANT = 'constant'
SEGMENT_THIS = 'this'
SEGMENT_THAT = 'that'
SEGMENT_POINTER = 'pointer'
SEGMENT_TEMP = 'temp'


COMMAND_TYPE_MAP = {
    C_ADD: CT_ARITHMETIC,
    C_SUB: CT_ARITHMETIC,
    C_NEG: CT_ARITHMETIC,
    C_EQ: CT_ARITHMETIC,
    C_GT: CT_ARITHMETIC,
    C_LT: CT_ARITHMETIC,
    C_AND: CT_ARITHMETIC,
    C_OR: CT_ARITHMETIC,
    C_NOT: CT_ARITHMETIC,
    C_PUSH: CT_PUSH,
    C_POP: CT_POP
}

COMMAND_SYMBOL_MAP = {
    C_ADD: '+',
    C_SUB: '-',
    C_NEG: '-',
    C_AND: '&',
    C_OR: '|',
    C_NOT: '!'
}

class Parser:

    def __init__(self, file):
        self._file = open(file, 'r')
        self._current_command = None
        self._next_line = self._read_next_valid_line()


    def _read_next_valid_line(self):
        while True:
            line = self._file.readline()

            if not line:
                line = None
                break

            line = line.rstrip()
            
            # Ignore the line if its empty or a comment
            if line == '' or line.startswith('//'):
                continue

            break

        return line


    def advance(self):
        if self.has_more_lines():
            self._current_command = self._next_line.split()
            self._next_line = self._read_next_valid_line()
        else:
            raise EOFError


    def has_more_lines(self):
        return bool(self._next_line)

    def command_type(self):
        command = self._current_command[0]
        command_type = COMMAND_TYPE_MAP.get(command)

        if command_type is None:
            raise ValueError(f"Invalid command: {command}")
    
        return command_type

    def arg1(self):
        if self.command_type() == CT_ARITHMETIC:
            return self._current_command[0]
        else:
            return self._current_command[1]

    def arg2(self):
        if self.command_type == CT_ARITHMETIC:
            raise ValueError
        else:
            return self._current_command[2]

    def command(self):
        return self._current_command[0]

    def close(self):
        self._file.close()


class CodeWriter:

    def __init__(self, file):
        self.file = open(file, 'w')
        pass


    def _get_symbol(self, command):
        symbol = COMMAND_SYMBOL_MAP.get(command, None)
        if symbol:
            return symbol
        
        raise SyntaxError

    def write_arithmetic(self, command):
        
        symbol = self._get_symbol(command)
        lines = ['// START {}'.format(command)]
        if command in (C_NOT, C_NEG):
            lines += ['@SP', 'A=M-1', 'M={}M'.format(symbol), '']
        elif command in (C_ADD, C_SUB, C_OR, C_AND):
            lines += ['@SP', 'AM=M-1 //SP--', 'D=M', 'A=A-1', 'M=D{}M'.format(symbol)]
        else:
            print(command)
            raise SyntaxError
        lines += ['// END {}'.format(command), '']

        self.file.writelines([line + '\n' for line in lines])

    def write_push_pop(self, command, segment, index):
        
        if segment == SEGMENT_CONSTANT:
            line = ['@{}'.format(index), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        elif segment in (SEGMENT_LOCAL, SEGMENT_ARGUMENT, SEGMENT_THIS, SEGMENT_THAT):
            if command == C_POP:
                line = ['@SP', 'AM=M-1', 'D=M', '@LCL', 'A=A+{}'.format(index), 'M=D']
            elif command == C_PUSH:
                line = ['@LCL', 'A=A+{}'.format(index), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']


    def close(self):
        self.file.close()

if __name__ == '__main__':
    parser = Parser('./MemoryAccess/BasicTest/BasicTest.vm')
    code_writer = CodeWriter('./MemoryAccess/BasicTest/sac.vm')
    while parser.has_more_lines():
        parser.advance()
        command_type = parser.command_type()

        if command_type == CT_ARITHMETIC:
            code_writer.write_arithmetic(parser.command())
        elif command_type in (CT_POP, CT_PUSH):
            code_writer.write_push_pop(parser.command(), parser.arg1(), parser.arg2())
        else:
            raise Exception

    parser.close()
    code_writer.close()
        
    

    