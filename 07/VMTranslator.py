import os
import argparse

# vm command types
CT_ARITHMETIC = "CT_ARITHMETIC"
CT_PUSH = "CT_PUSH"
CT_POP = "CT_POP"
CT_LABEL = "CT_LABEL"
CT_GOTO = "CT_GOTO"
CT_IF = "CT_IF"
CT_FUNCTION = "CT_FUNCTION"
CT_RETURN = "CT_RETURN"
CT_CALL = "CT_CALL"

# vm command keywords
C_ADD = "add"
C_SUB = "sub"
C_NEG = "neg"
C_EQ = "eq"
C_GT = "gt"
C_LT = "lt"
C_AND = "and"
C_OR = "or"
C_NOT = "not"
C_PUSH = "push"
C_POP = "pop"

# vm memory segments keywords
SEGMENT_LOCAL = "local"
SEGMENT_ARGUMENT = "argument"
SEGMENT_STATIC = "static"
SEGMENT_CONSTANT = "constant"
SEGMENT_THIS = "this"
SEGMENT_THAT = "that"
SEGMENT_POINTER = "pointer"
SEGMENT_TEMP = "temp"


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
    C_POP: CT_POP,
}

class PopTranslator:
    def __init__(self, output_file):
        self.output_file = output_file

    def _pop(self, segment, index, comment=None):
        translation = [f"@{segment}", "D=M", f"@{index}", "D=D+A", "@R13", "M=D", "@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]
        if comment:
            return [f"// {comment}"] + translation

        return translation

    def _local(self, index):
        return self._pop("LCL", index, "pop local")

    def _argument(self, index):
        return self._pop("ARG", index, "pop argument")

    def _this(self, index):
        return self._pop("THIS", index, "pop this")

    def _that(self, index):
        return self._pop("THAT", index, "pop that")

    def _temp(self, index):
        return ["// pop temp", "@5", "D=A", f"@{index}", "D=D+A", "@R13", "M=D", "@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]

    def _static(self, index):
        return ["// push static", "@SP", "AM=M-1", "D=M", f"@{self.output_file}.{index}", "M=D"]

    def _pointer(self, index):
        if index == "0":
            segment = "THIS"
        elif index == "1":
            segment = "THAT"
        else:
            raise ValueError

        return ["// pop pointer", "@SP", "AM=M-1", "D=M", f"@{segment}", "M=D"]

    def translate(self, segment, index):
        method = getattr(self, "_" + segment)
        return method(index)


class PushTranslator:
    def __init__(self, output_file):
        self.output_file = output_file

    def _push(self, segment, index, comment=None):
        translation = [f"@{segment}", "D=M", f"@{index}", "A=D+A", "D=M", "@SP", "AM=M+1", "A=A-1", "M=D"]

        if comment:
            return [f"// {comment}"] + translation

        return translation

    def _constant(self, index):
        return ["// push constant", f"@{index}", "D=A", "@SP", "AM=M+1", "A=A-1", "M=D"]

    def _local(self, index):
        return self._push("LCL", index, "push local")

    def _argument(self, index):
        return self._push("ARG", index, "push argument")

    def _this(self, index):
        return self._push("THIS", index, "push this")

    def _that(self, index):
        return self._push("THAT", index, "push that")

    def _temp(self, index):
        return ["// push temp", "@5", "D=A", f"@{index}", "A=D+A", "D=M", "@SP", "AM=M+1", "A=A-1", "M=D"]

    def _static(self, index):
        return ["// push static", f"@{self.output_file}.{index}", "D=M", "@SP", "AM=M+1", "A=A-1", "M=D"]

    def _pointer(self, index):
        if index == "0":
            segment = "THIS"
        elif index == "1":
            segment = "THAT"
        else:
            raise ValueError

        return ["// push pointer", f"@{segment}", "D=M", "@SP", "AM=M+1", "A=A-1", "M=D"]

    def translate(self, segment, index):
        method = getattr(self, "_" + segment)
        return method(index)


class ArithmeticTranslator:
    def __init__(self):
        self.compare_label_count = 0

    def _comparision_arithmetic(self, jump_condition, label_prefix, comment=None):
        true_label = label_prefix + "_TRUE_" + str(self.compare_label_count)
        end_label = label_prefix + "_END_" + str(self.compare_label_count)

        self.compare_label_count += 1

        translation = self._binary_arithmetic("-") + [
            "@SP",
            "AM=M-1",
            "D=M",
            f"@{true_label}",
            f"D;{jump_condition}",
            "D=0",
            f"@{end_label}",
            "0;JMP",
            f"({true_label})",
            "D=-1",
            f"({end_label})",
            "@SP",
            "AM=M+1",
            "A=A-1",
            "M=D",
        ]

        if comment:
            return [f"// {comment}"] + translation

        return translation

    def _eq(self):
        return self._comparision_arithmetic("JEQ", "EQUAL", "eq")

    def _lt(self):
        return self._comparision_arithmetic("JLT", "LESS", "lt")

    def _gt(self):
        return self._comparision_arithmetic("JGT", "GREATER", "gt")

    def _binary_arithmetic(self, operator, comment=None):
        translation = ["@SP", "AM=M-1", "D=M", "A=A-1", f"M=M{operator}D"]
        if comment:
            return [f"// {comment}"] + translation

        return translation

    def _add(self):
        return self._binary_arithmetic("+", "add")

    def _sub(self):
        return self._binary_arithmetic("-", "sub")

    def _and(self):
        return self._binary_arithmetic("&", "and")

    def _or(self):
        return self._binary_arithmetic("|", "or")

    def _unary_arithmetic(self, operator, comment=None):
        translation = ["@SP", "A=M-1", f"M={operator}M"]

        if comment:
            return [f"// {comment}"] + translation

        return translation

    def _neg(self):
        return self._unary_arithmetic("-")

    def _not(self):
        return self._unary_arithmetic("!")

    def translate(self, command):
        method = getattr(self, "_" + command)
        return method()


class Parser:
    def __init__(self, file):
        self._file = open(file, "r")
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
            if line == "" or line.startswith("//"):
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
    def __init__(self, file_name, output_dir):
        output_file_path = os.path.join(output_dir, file_name + ".asm")
        self.file = open(output_file_path, "w")

        self.push_translator = PushTranslator(file_name)
        self.pop_tranlator = PopTranslator(file_name)
        self.arithmetic_tranlator = ArithmeticTranslator()

    def write_arithmetic(self, command):
        code = self.arithmetic_tranlator.translate(command)
        self._write(code)

    def write_push_pop(self, command, segment, index):
        if command == C_PUSH:
            code = self.push_translator.translate(segment, index)
        elif command == C_POP:
            code = self.pop_tranlator.translate(segment, index)

        self._write(code)

    def _write(self, lines):
        cleand_lines = [line.strip() + "\n" for line in lines]
        self.file.writelines(cleand_lines)

    def close(self):
        self.file.close()


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="VM Translator: Translates a VM file to Hack Assembly code.")

    args_parser.add_argument("file", help="Path to the VM file to be translated.")

    args = args_parser.parse_args()

    basename = os.path.basename(args.file)
    file_dir = os.path.dirname(args.file)
    file_name = os.path.splitext(basename)[0]

    parser = Parser(args.file)
    code_writer = CodeWriter(file_name, file_dir)
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
