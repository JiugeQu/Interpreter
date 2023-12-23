from scanner import Lexer, Token
from tokens import TokenType, FUNC
import matplotlib.pyplot as plt
from painter import CacuSyntaxTree, CacuColor, GenerateT, Modify, singleLoopNoDelete, singleLoopDelete
from painter import doubleLoopNoDelete, doubleLoopDelete


# 表达式节点类
class ExprNode:
    def __init__(self, opcode, content=None):
        self.OpCode = opcode
        self.Content = content


origin_x, origin_y = (0, 0)
scale_x, scale_y = (1.0, 1.0)
rot_rad = 0.0
bg_color = (0.9608, 0.9608, 0.8627)
dot_color = (1, 0.6471, 0)
delete = False
fig, ax = plt.subplots()
temp = ()
title_t = None


# 创建表达式节点
def MakeExprNode(opcode, *args):
    if opcode == TokenType.CONST_ID:
        return ExprNode(opcode, args[0])
    elif opcode == TokenType.T:
        return ExprNode(opcode, args[0])
    elif opcode == TokenType.FUNC:
        return ExprNode(opcode, (args[0], args[1]))
    else:
        return ExprNode(opcode, (args[0], args[1]))


# 打印语法树
def PrintSyntaxTree(root, indent):
    if root is None:
        return
    print("  " * indent + "OpCode: " + str(root.OpCode))
    if root.OpCode == TokenType.CONST_ID:
        print("  " * indent + "Value: " + str(root.Content))
    elif root.OpCode == TokenType.T:
        print("  " * indent + "Parameter: " + str(root.Content))
    elif root.OpCode == TokenType.FUNC:
        print("  " * indent + "Function: " + str(root.Content[0]))
        PrintSyntaxTree(root.Content[1], indent + 1)
    else:
        print("  " * indent + "Left:")
        PrintSyntaxTree(root.Content[0], indent + 1)
        print("  " * indent + "Right:")
        PrintSyntaxTree(root.Content[1], indent + 1)


token = None  # 当前记号
tokens = None  # 记号流


def FetchToken():
    global token
    try:
        token = next(tokens)
        # next(cpy_tokens)无法进入Doublefor，迭代完毕退出
        if TokenType.ERROR == token.type:
            SyntaxError("词法错误")
    except StopIteration:
        print("所有翻译完毕\n")
        exit()


def MatchToken(The_Token):
    if token.type == The_Token:
        FetchToken()
        return True
    else:
        # if token.type!=TokenType.COLON:
        SyntaxError("语法错误")
        return False


def SyntaxError(err):  # 报错
    print(err)


# 表达式
def Atom():
    if token.type == TokenType.CONST_ID or token.type == TokenType.T:
        leaf = MakeExprNode(token.type, token.lexeme)
        token_tmp = token.type
        MatchToken(token_tmp)
        return leaf
    elif token.type == TokenType.FUNC:
        global father_type
        father_type = token.type
        token_tmp = token.type
        token_fun = token.lexeme.lower()  # 3.0 修改token为token.lexeme.lower()，小写
        # print(token_fun.lexeme)，大写
        if token_fun in [FUNC.SIN, FUNC.COS, FUNC.TAN, FUNC.SQRT, FUNC.EXP, FUNC.LN]:
            funct = [FUNC.SIN, FUNC.COS, FUNC.TAN, FUNC.SQRT, FUNC.EXP, FUNC.LN].index(
                token_fun)  # 3.0，把词法内置数学函数改为语法自定义函数，方便语义操作
            # print(funct)
            functi = [FUNC.SIN, FUNC.COS, FUNC.TAN, FUNC.SQRT, FUNC.EXP, FUNC.LN][funct]  # 语义要的对象
            # print(functi)
        MatchToken(token_tmp)
        MatchToken(TokenType.L_BRACKET)
        t = Expression()
        father_type = None
        MatchToken(TokenType.R_BRACKET)
        leaf = MakeExprNode(token_tmp, token_fun, t)
        return leaf
    elif token.type == TokenType.L_BRACKET:
        father_type = token.type
        MatchToken(TokenType.L_BRACKET)
        leaf = Expression()
        father_type = None
        MatchToken(TokenType.R_BRACKET)
        return leaf


# 右递归实现    
def Component():
    left = Atom()
    if token.type == TokenType.POWER:
        token_tmp = token.type
        MatchToken(token_tmp)
        right = Component()
        left = MakeExprNode(token_tmp, left, right)
        return left
    else:
        return left


def Factor(): 
    if token.type == TokenType.PLUS or token.type == TokenType.MINUS:
        token_tmp = token.type
        MatchToken(token_tmp)
        if token_tmp == TokenType.MINUS:
            right = Factor()
            left = ExprNode(TokenType.CONST_ID,0)  # 一元负，左补0
            left = MakeExprNode(token_tmp, left, right)
            return left
        else:
            right = Factor()  # 一元正，消去正
            return right
    else:
        left = Component()
        return left


def Term():
    left = Factor()
    while token.type == TokenType.MUL or token.type == TokenType.DIV:
        token_tmp = token.type
        MatchToken(token_tmp)
        right = Factor()
        left = MakeExprNode(token_tmp, left, right)
    return left


father_type = None


def Expression():
    left = Term()
    while token.type == TokenType.PLUS or token.type == TokenType.MINUS:
        token_tmp = token.type
        MatchToken(token_tmp)
        right = Term()
        left = MakeExprNode(token_tmp, left, right)
    if father_type != TokenType.FUNC and father_type != TokenType.L_BRACKET:  # 防止FUNC和()内部expression由于递归从而打印两遍
        PrintSyntaxTree(left, 0)
    return left


def Hint(statment_type, op):
    if 0 == op:
        print("enter in %s" % statment_type)
    else:
        print("exit from %s" % statment_type)


def OriginStatment():
    global origin_x, origin_y
    Hint("OriginStatment", 0)
    MatchToken(TokenType.ORIGIN)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    x = Expression()
    origin_x = CacuSyntaxTree(x)
    MatchToken(TokenType.COMMA)
    y = Expression()
    origin_y = CacuSyntaxTree(y)
    MatchToken(TokenType.R_BRACKET)
    Hint("OriginStatment", 1)
    # 语义嵌入


def RotStatment():
    global rot_rad
    Hint("RotStatment", 0)
    MatchToken(TokenType.ROT)
    MatchToken(TokenType.IS)
    angle = Expression()
    rot_rad = CacuSyntaxTree(angle)
    Hint("RotStatment", 1)
    # 语义嵌入


def ScaleStatment():
    global scale_x, scale_y
    Hint("ScaleStatment", 0)
    MatchToken(TokenType.SCALE)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    x = Expression()
    scale_x = CacuSyntaxTree(x)
    MatchToken(TokenType.COMMA)
    y = Expression()
    scale_y = CacuSyntaxTree(y)
    MatchToken(TokenType.R_BRACKET)
    Hint("ScaleStatment", 1)
    # 语义嵌入


# 新增
def TitleStatment():
    global title_t
    Hint("TitleStatment", 0)
    MatchToken(TokenType.TITLE)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.QUOTE)
    title = Expression()
    title_t = title.Content
    MatchToken(TokenType.QUOTE)
    Hint("TitleStatment", 1)
    # 语义嵌入


def BgcolourStatment():
    Hint("BgcolourStatment", 0)
    MatchToken(TokenType.BGCOLOUR)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    r = Expression()
    MatchToken(TokenType.COMMA)
    g = Expression()
    MatchToken(TokenType.COMMA)
    b = Expression()
    MatchToken(TokenType.R_BRACKET)
    Hint("BgcolourStatment", 1)

    bg_color = (CacuSyntaxTree(r), CacuSyntaxTree(g), CacuSyntaxTree(b))
    bg_color = CacuColor(bg_color)
    fig.set_facecolor(bg_color)


def FgcolourStatment():
    global dot_color
    Hint("FgcolourStatment", 0)
    MatchToken(TokenType.FGCOLOUR)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    r = Expression()
    MatchToken(TokenType.COMMA)
    g = Expression()
    MatchToken(TokenType.COMMA)
    b = Expression()
    MatchToken(TokenType.R_BRACKET)
    Hint("FgcolourStatment", 1)
    # 语义嵌入
    dot_color = (CacuSyntaxTree(r), CacuSyntaxTree(g), CacuSyntaxTree(b))
    dot_color = CacuColor(dot_color)


def ClearStatment():
    global delete
    Hint("ClearStatment", 0)
    MatchToken(TokenType.CLEAR)
    f = token.lexeme  # 3.0，修改f=token为f=token.lexeme，得到True/False
    if f == 'TRUE':
        print(f)
        delete = True
    elif f == 'FALSE':
        delete = False
    MatchToken(TokenType.CONST_ID)
    Hint("ClearStatment", 1)
    # 语义嵌入


def ForStatment():
    global temp, title_t, ax
    print(origin_x, origin_y, scale_x, scale_y, rot_rad, dot_color, delete)
    Hint("ForStatment", 0)
    MatchToken(TokenType.FOR)
    MatchToken(TokenType.T)
    MatchToken(TokenType.FROM)
    start = Expression()
    MatchToken(TokenType.TO)
    end = Expression()
    MatchToken(TokenType.STEP)
    step = Expression()

    # get temp
    temp = GenerateT(CacuSyntaxTree(start), CacuSyntaxTree(end), CacuSyntaxTree(step))

    MatchToken(TokenType.DRAW)
    MatchToken(TokenType.L_BRACKET)
    x = Expression()
    x_data = CacuSyntaxTree(x, temp)
    if not isinstance(x_data, tuple):
        x_data = (x_data,) * len(temp)
    MatchToken(TokenType.COMMA)
    y = Expression()
    y_data = CacuSyntaxTree(y, temp)
    if not isinstance(y_data, tuple):
        y_data = (y_data,) * len(temp)

    MatchToken(TokenType.R_BRACKET)

    if title_t is not None:
        plt.title(title_t)
    if token.type == TokenType.SEMICO:
        print('single loop')
        print(x_data)
        print(y_data)
        x_data, y_data = Modify(x_data, y_data, origin_x, origin_y, scale_x, scale_y, rot_rad)
        print(x_data)
        print(y_data)
        if delete:
            print('delete')
            ax.cla()
            plt.title(title_t)
            singleLoopDelete(ax, list(x_data), list(y_data), dot_color, title_t)
        else:
            singleLoopNoDelete(ax, list(x_data), list(y_data), dot_color)
    elif token.type == TokenType.COLON:  # 4.0，新增Doublefor处理
        print('double loop')
        MatchToken(TokenType.COLON)
        MatchToken(TokenType.FOR)
        MatchToken(TokenType.T)
        MatchToken(TokenType.FROM)
        start = Expression()
        MatchToken(TokenType.TO)
        end = Expression()
        MatchToken(TokenType.STEP)
        step = Expression()

        temp = GenerateT(CacuSyntaxTree(start), CacuSyntaxTree(end), CacuSyntaxTree(step))

        MatchToken(TokenType.DRAW)
        MatchToken(TokenType.L_BRACKET)
        x = Expression()
        x_data2 = CacuSyntaxTree(x, temp)
        if not isinstance(x_data2, tuple):
            x_data2 = (x_data2,) * len(temp)
        MatchToken(TokenType.COMMA)
        y = Expression()
        y_data2 = CacuSyntaxTree(y, temp)
        if not isinstance(y_data2, tuple):
            y_data2 = (y_data2,) * len(temp)
        MatchToken(TokenType.R_BRACKET)

        x_data2, y_data2 = Modify(x_data2, y_data2, origin_x, origin_y, scale_x, scale_y, rot_rad)
        if delete:
            print('delete')
            ax.cla()
            plt.title(title_t)
            doubleLoopDelete(ax, list(x_data), list(y_data), list(x_data2), list(y_data2), dot_color, title_t)
        else:
            doubleLoopNoDelete(ax, list(x_data), list(y_data), list(x_data2), list(y_data2), dot_color)

    Hint("ForStatment", 1)
    # 语义嵌入


# def DoubleforStatment():
#     Hint("DoubleforStatment", 0)
#     ForStatment()
#     MatchToken(TokenType.COLON) 
#     ForStatment()
#     Hint("DoubleforStatment", 1)

# def process_tokens(tokens):#列表方法
#     tokens_list = list(tokens)
#     for i, token in enumerate(tokens_list):
#         if token.type == TokenType.COLON:
#             # 在当前 token 后查找第一个匹配到 TokenType.SEMICO 的位置
#             semico_index = next((index for index, t in enumerate(tokens_list[i+1:]) if t.type == TokenType.SEMICO), None)          
#             if semico_index is not None:               
#                 # 将迭代器中剩余元素加入列表
#                 tokens_list.extend(tokens)
#                 return True
#         return False

# 主程序              
def Statment():
    if token.type == TokenType.ORIGIN:
        OriginStatment()
    elif token.type == TokenType.SCALE:
        ScaleStatment()
    elif token.type == TokenType.ROT:
        RotStatment()
    elif token.type == TokenType.TITLE:
        TitleStatment()
    elif token.type == TokenType.BGCOLOUR:
        BgcolourStatment()
    elif token.type == TokenType.FGCOLOUR:
        FgcolourStatment()
    elif token.type == TokenType.CLEAR:
        ClearStatment()
        # 列表方法，elif process_tokens(tokens):或
    # 迭代器方法，elif token.type == TokenType.FOR and TokenType.COLON in cpy_tokens:
    #     DoubleforStatment()
    elif token.type == TokenType.FOR:
        ForStatment()
    elif token.type == TokenType.SEMICO:  # 词法分析的一个小bug，以;分隔句子，如果注释末尾无; 则会把下一句也吞掉。所以给注释末尾加; 分号不会被吞掉，用来标识注释语句
        SyntaxError("注释语句")
    else:
        SyntaxError("错误语句")


def Program():
    i = 0

    while TokenType.NONTOKEN != token.type:
        Statment()
        if MatchToken(TokenType.SEMICO):
            # if MatchToken(TokenType.SEMICO) or MatchToken(TokenType.COLON):#不符合Doublefor文法（如画图嵌套画图也不会报错），但可按句解析
            i += 1
            print("第%d句翻译完毕\n" % i)
        else:
            exit()

    plt.show()


def Parser(file_path):
    global tokens, cpy_tokens
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # 读文件
        lexer = Lexer()
        tokenList = lexer.lex(content)
        tokens = iter(tokenList)  # 从词法分析器得到记号流，实际迭代
        # cpy_tokens = iter(tokenList)#迭代器方法，用于Doublefor条件检查，不可行，MatchToken迭代完退出
        FetchToken()
        return Program()
    except FileNotFoundError:
        print("打开源文件有误\n")
    finally:
        file.close()  # 关闭文件


if __name__ == "__main__":
    Parser("2.txt")
