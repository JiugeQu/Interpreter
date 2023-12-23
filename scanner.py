
import math
from tokens import TokenType


class Token:
    def __init__(self, type, lexeme, value=None, func_ptr=None):
        self.type = type
        self.lexeme = lexeme
        self.value = value
        self.func_ptr = func_ptr

    def show(self):
        print(self.type.name.ljust(15), self.lexeme.ljust(15), str(self.value).ljust(15), str(self.func_ptr).ljust(15))


class Lexer:
    def __init__(self):
        self.table = {"PI": Token(TokenType.CONST_ID, "PI", math.pi),
                      "E": Token(TokenType.CONST_ID, "E", math.e),
                      "TRUE": Token(TokenType.CONST_ID, "TRUE", 1.0),
                      "FALSE": Token(TokenType.CONST_ID, "FALSE", 0.0),
                      "T": Token(TokenType.T, "T"),
                      "SIN": Token(TokenType.FUNC, "SIN", 0.0, math.sin),
                      "COS": Token(TokenType.FUNC, "COS", 0.0, math.cos),
                      "TAN": Token(TokenType.FUNC, "TAN", 0.0, math.tan),
                      "SQRT": Token(TokenType.FUNC, "SQRT", 0.0, math.sqrt),
                      "EXP": Token(TokenType.FUNC, "EXP", 0.0, math.exp),
                      "LN": Token(TokenType.FUNC, "LN", 0.0, math.log),
                      "ORIGIN": Token(TokenType.ORIGIN, "ORIGIN"),
                      "SCALE": Token(TokenType.SCALE, "SCALE"),
                      "ROT": Token(TokenType.ROT, "ROT"),
                      "IS": Token(TokenType.IS, "IS"),
                      "FOR": Token(TokenType.FOR, "FOR"),
                      "FROM": Token(TokenType.FROM, "FROM"),
                      "TO": Token(TokenType.TO, "TO"),
                      "STEP": Token(TokenType.STEP, "STEP"),
                      "DRAW": Token(TokenType.DRAW, "DRAW"),
                      "BGCOLOUR": Token(TokenType.BGCOLOUR, "BGCOLOUR"),
                      "FGCOLOUR": Token(TokenType.FGCOLOUR, "FGCOLOUR"),
                      "CLEAR": Token(TokenType.CLEAR, "CLEAR"),
                      "TITLE": Token(TokenType.TITLE, "TITLE"),
                      "COMMENT": Token(TokenType.COMMENT, "COMMENT"),
                      ";": Token(TokenType.SEMICO, ";"),
                      "(": Token(TokenType.L_BRACKET, "("),
                      ")": Token(TokenType.R_BRACKET, ")"),
                      ",": Token(TokenType.COMMA, ","),
                      "'": Token(TokenType.QUOTE, "'"),
                      ":": Token(TokenType.COLON, ":"),
                      "+": Token(TokenType.PLUS, "+"),
                      "-": Token(TokenType.MINUS, "-"),
                      "*": Token(TokenType.MUL, "*"),
                      "/": Token(TokenType.DIV, "/"),
                      "**": Token(TokenType.POWER, "**"), }

    def dfa(self, char, state):
        if state == 0:
            if char.isspace():
                return 0
            elif char.isalpha():
                return 1
            elif char.isdigit():
                return 2
            elif char == '*':
                return 4
            elif char == '/':
                return 6
            elif char == '-':
                return 8
            elif char in '+();:,':
                return 9
            elif char == "'":
                return 13
            else:
                return -1
        elif state == 1:
            if char.isalpha():
                return 1
            if char.isdigit():
                return 1
            else:
                return 10
        elif state == 2:
            if char == '.':
                return 3
            elif char.isdigit():
                return 2
            elif char in '+-*/,;) ':
                return 12
            else:
                return -1
        elif state == 3:
            if char.isdigit():
                return 3
            elif char.isspace():
                return 12
            elif char in '+-*/,;) ':
                return 12
            else:
                return -1
        elif state == 4:
            if char == '*':
                return 5
        elif state == 6:
            if char == '/':
                return 7
        elif state == 8:
            if char == '-':
                return 7
        elif state == 7:
            if char == ';':
                return 11
            else:
                return 7
        elif state == 13:
            if char in "';":
                return 14
            else:
                return 13

    def lex(self, code):
        tokens = []
        position_temp = 0
        current_state = 0
        current_lexeme = ""

        while position_temp < len(code):
            char = code[position_temp]
            while position_temp + 1 < len(code) and current_state == 0 and char.isspace():
                position_temp += 1
                char = code[position_temp]

            new_state = self.dfa(char, current_state)

            if new_state == -1:  # 错误状态
                current_lexeme += char
                token = self.table.get(current_lexeme, Token(TokenType.ERROR, current_lexeme))
                tokens.append(token)
                current_lexeme = ""
                current_state = 0
                position_temp += 1
            elif new_state == 1:  # 当前读取到字符，加入
                current_lexeme += char
                current_state = new_state
                position_temp += 1
            elif new_state == 10:
                token = self.table.get(current_lexeme.upper(), Token(TokenType.ERROR, current_lexeme))
                tokens.append(token)
                current_lexeme = ""
                current_state = 0
            elif new_state == 9:  # 当前读取到+();:
                current_lexeme += char
                token = self.table[current_lexeme]
                tokens.append(token)
                current_lexeme = ""
                current_state = 0
                position_temp += 1
            elif new_state == 4:  # 当前*
                current_lexeme += char
                if position_temp + 1 < len(code) and self.dfa(code[position_temp + 1], new_state) == 5:  # **
                    position_temp += 1
                    current_lexeme += code[position_temp]
                token = self.table[current_lexeme]
                tokens.append(token)
                current_lexeme = ""
                current_state = 0
                position_temp += 1
            elif new_state == 6:  # /或//注释
                current_lexeme += char
                current_state = new_state
                if position_temp + 1 < len(code) and self.dfa(code[position_temp + 1], current_state) == 7:
                    position_temp += 1
                    current_lexeme += code[position_temp]
                    new_state = self.dfa(code[position_temp], current_state)
                    current_state = new_state
                    position_temp += 1
                    while position_temp < len(code) and self.dfa(code[position_temp], current_state) != 11:
                        current_lexeme += code[position_temp]
                        new_state = self.dfa(code[position_temp], current_state)
                        position_temp += 1
                        current_state = new_state
                    # token = self.table.get(current_lexeme, Token(TokenType.COMMENT, current_lexeme))
                    # tokens.append(token)
                else:
                    token = self.table[current_lexeme]
                    tokens.append(token)
                current_lexeme = ""
                position_temp += 1
                current_state = 0
            elif new_state == 8:  # -或--注释
                current_lexeme += char
                current_state = new_state
                if position_temp + 1 < len(code) and self.dfa(code[position_temp + 1], current_state) == 7:
                    position_temp += 1
                    current_lexeme += code[position_temp]
                    new_state = self.dfa(code[position_temp], current_state)
                    current_state = new_state
                    position_temp += 1
                    while position_temp < len(code) and self.dfa(code[position_temp], current_state) != 11:
                        current_lexeme += code[position_temp]
                        new_state = self.dfa(code[position_temp], current_state)
                        position_temp += 1
                        current_state = new_state
                    # token = self.table.get(current_lexeme, Token(TokenType.COMMENT, current_lexeme))
                    # tokens.append(token)
                    token = self.table[';']
                    tokens.append(token)
                else:
                    token = self.table[current_lexeme]
                    tokens.append(token)
                current_lexeme = ""
                position_temp += 1
                current_state = 0
            elif new_state == 2:  # 数字
                current_lexeme += char
                current_state = new_state
                position_temp += 1
            elif new_state == 3:  # 数字
                current_lexeme += char
                current_state = new_state
                position_temp += 1
            elif new_state == 12:  # 数字接收
                token = self.table.get(current_lexeme, Token(TokenType.CONST_ID, current_lexeme, float(current_lexeme)))
                tokens.append(token)
                current_lexeme = ""
                current_state = 0
            elif new_state == 13:  # 第一个'
                if current_state == 0:
                    token = self.table["'"]
                    tokens.append(token)
                else:
                    current_lexeme += char
                position_temp += 1
                current_state = new_state
            elif new_state == 14:  # 第二个'，接收中间内容和'
                token = self.table.get(current_lexeme, Token(TokenType.CONST_ID, current_lexeme))
                tokens.append(token)
                token = self.table[char]
                tokens.append(token)
                position_temp += 1
                current_lexeme = ""
                current_state = 0
            elif new_state == 0 and position_temp + 1 == len(code):
                break
        if current_lexeme != "":
            if new_state in [1, 10]:
                token = self.table.get(current_lexeme.upper(), Token(TokenType.ERROR, current_lexeme))
            elif new_state in [9, 4, 5, 6, 8, 13]:
                token = self.table[current_lexeme]
            elif new_state in [2, 3]:
                token = self.table.get(current_lexeme, Token(TokenType.CONST_ID, current_lexeme, float(current_lexeme)))
            elif new_state == 7:
                token = self.table.get(current_lexeme, Token(TokenType.COMMENT, current_lexeme))
            elif new_state == -1:
                token = self.table.get(current_lexeme, Token(TokenType.ERROR, current_lexeme))
            tokens.append(token)

        return tokens


def show_tokens(tokens):
    print("类别".ljust(15), "原始输入".ljust(15), "值".ljust(15), "地址".ljust(15))
    for token in tokens:
        token.show()


if __name__ == "__main__":
    # code = "bgcolouris bgcolour BGCOLOUR bgcolour1 ta 8a 8. .3 @"
    file_path = "2.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    lexer = Lexer()
    tokens = lexer.lex(code)
    show_tokens(tokens)
