'''
Description: 
Author: He Yuhang
Github: https://github.com/hyhhhhhhhh
Date: 2020-11-24 12:02:12
LastEditors: Box
LastEditTime: 2020-12-13 21:54:21
'''

from error import SemanticRuleError, SyntaxError, SyntaxRuleError

KeyWord = [
    'and', 'array', 'begin', 'bool', 'call', 'case', 'char', 'constant', 'dim',
    'do', 'else', 'end', 'false', 'for', 'if', 'input', 'integer', 'not', 'of',
    'or', 'output', 'procedure', 'program', 'read', 'real', 'repeat', 'set',
    'stop', 'then', 'to', 'true', 'until', 'var', 'while', 'write'
]
Special = ['ID', 'int', 'string']
Op = [
    '(', ')', '*', '*/', '+', ',', '-', '.', '..', '/', '/*', ':', ':=', ';',
    '<', '<=', '<>', '=', '>', '>=', '[', ']'
]
# Oplr = ['(',')']
# Op2 = ['*','*/','+',',','-','.','..','/','/*',':',':=',';','<' ,'<=','<>' ,'=','>' ,'>=','[',']']
EncodeList = dict(zip(KeyWord + Special + Op, range(1, 61)))
DecodeList = dict(zip(EncodeList.values(), EncodeList.keys()))


class getTokens():
    def __init__(self, string):
        self.string = string.strip() + ' '
        self.p = 0
        self.l = len(self.string) - 1
        self.var = 0
        self.token = []
        self.var_index = []
        self.var_list = []

        self.error = None

    def addPrase(self, string):
        self.string += string

    def RecodrdVar(self, buffer):
        if buffer not in self.var_list:
            self.var += 1
            self.var_list.append(buffer)
        return self.var_list.index(buffer) + 1

    def NotReach(self):
        return not self.p == self.l

    def backstep(self):
        self.p -= 1

    def update(self):
        if self.p < self.l:
            self.p += 1
        # self.string =self.string[self.p:]

    def pos(self):
        return self.string[self.p]

    def IsSpace(self):
        return self.pos() == ' ' or self.pos() == '\n' or self.pos() == '\t'

    def ClearSpace(self):
        while self.IsSpace():
            self.update()

    def scanner(self):
        #get legal words in a line
        # 一直读到文件最后跳出while
        while self.NotReach():
            #每当遇到空字符完成一个iteration,处理空字符
            self.ClearSpace()
            buffer = ''
            # 如果开头读到第一个是数字
            if self.pos().isdigit():
                # 那么接下来所有都要是数字，以满足 整数 的要求
                while self.pos().isdigit() and self.NotReach():
                    buffer += self.pos()
                    self.update()
                # 读到非数字停止，判断停止的时候是不是非法的 字母。字母非法，符号合法
                if not self.pos().isalpha():
                    self.token.append(EncodeList['int'])
                    self.var_index.append(self.RecodrdVar(buffer))
                else:
                    self.error = 'error at :\n' + self.string[:self.p]+'^'
                    return False  #error
            # 当前Token不是整数，判断当前Token是不是标识符或者特殊字符串
            # 开头为字母，开始判断
            elif self.pos().isalpha():
                # 读取Token所有的字母与数字
                while (self.pos().isalpha()
                       or self.pos().isdigit()) and self.NotReach():
                    buffer += self.pos()
                    self.update()
                # 读取完毕判断是特殊字符串还是标识符
                if buffer in KeyWord:
                    # 返回关键字
                    self.token.append(EncodeList[buffer])
                    self.var_index.append('-')
                else:
                    # 返回ID
                    self.token.append(EncodeList['ID'])
                    self.var_index.append(self.RecodrdVar(buffer))
            # 处理Token开头是符号的情况：注释，普通符号，字符常量
            # 如果引号开头，提取整个引号内容，知道匹配下一个引号为止
            elif self.pos() == '\'':
                self.update()
                # 未匹配到最后，未匹配到下一个引号，未匹配到换行都继续
                while self.pos() != '\'' and self.NotReach() and self.string[self.p]!='\n':
                    buffer += self.pos()
                    self.update()
                if self.pos() == '\'':
                    # 正常抵达字符串的结尾
                    self.update()
                    self.var += 1
                    self.token.append(EncodeList['string'])
                    self.var_index.append(self.RecodrdVar(buffer))
                else:
                    # 字符串不匹配
                    self.error = 'error at :\n' + self.string[:self.p]+'^'
                    return False
            # 最后一种情况，匹配普通操作符
            elif self.pos() in Op:
                # 向后取两个字
                for i in range(2):
                    buffer += self.pos()
                    self.update()
                    # 取不到两个字，break只取一个
                    if self.pos() not in Op:
                        break
                # 如果只取到一个字，且字是操作符
                if len(buffer) == 1:
                    self.token.append(EncodeList[buffer])
                    self.var_index.append('-')
                # 取到两个字 buffer == 2
                elif buffer in Op:
                    # 跳过注释
                    if buffer in ['/*', '*/']:
                        search_end = buffer[-2:]
                        while search_end != '*/':
                            if not self.NotReach() or self.string[self.p]=='\n':
                                self.error = 'error at : \n' + self.string[:self.p]+'^'
                                return False
                            buffer += self.pos()
                            self.update()
                            search_end = buffer[-2:]
                        continue
                    # 返回符号
                    self.token.append(EncodeList[buffer])
                    self.var_index.append('-')
                # 如果取到两个字，但是能够分别独立构成操作符，比如 6+(3-2)
                elif buffer[0] in Op and buffer[1] in Op:
                    buffer = buffer[0]
                    self.backstep()
                    self.token.append(EncodeList[buffer])
                    self.var_index.append('-')

                else:  #buffer 不是有效运算符
                    
                    self.error = 'error at :\n' + self.string[:self.p]+'^'
                    return False
            else:
                self.error = 'error at :\n' + self.string[:self.p]+'^'
                return False
            # print(buffer)
        return True

    def get_tokens(self, token, varnum):
        if varnum == '-':
            return DecodeList[token]
        else:
            return self.var_list[varnum - 1]

    def printres(self):
        for token, varnum, adjust in zip(self.token, self.var_index,
                                         range(1,
                                               len(self.token) + 1)):
            line = '( ' + str(token) + ' , ' + str(varnum) + ' )' + ' ' + str(
                self.get_tokens(token, varnum))
            print(line, end= '    \t')
            if adjust and adjust % 5 == 0:
                print()

    def generate(self):
        file = open("tokens.txt", 'w')  #append mode

        for token, varnum, adjust in zip(self.token, self.var_index,
                                         range(1,
                                               len(self.token) + 1)):
            line = '( ' + str(token) + ' , ' + str(varnum) + ' )' + ' ' + str(
                self.get_tokens(token, varnum))
            #   print(line)
            file.write(line + "\n")


#所有终结符类型
terminal_sign_type = KeyWord + Special + Op + ['pound']

empty = ['empty']
#所有非终结符类型
non_terminal_sign_type = [
    'program-start',  #程序
    'var-declear',  #变量说明
    'compound-statement',  #复合语句
    'var-define',  #变量定义
    'var-define-t',  #变量定义-t
    'id-list',  #标识符表
    'id-list-t',  #标识符表-t
    'type',  #类型
    'statement-list',  #语句表
    'statement-list-t',  #语句表-t
    'statement',  #语句
    'bool-exp',  #布尔表达式
    'bool-exp-t',  #布尔表达式-t
    'repeat-sent',  #repeat句
    'while-sent',  #while句
    'if-sent',  #if句
    # 'if-else-t',#if else句子-t
    'if-sent-t',  #if句-t
    'assig-sent',  #赋值句
    'cal-exp',  #算术表达式
    'cal-exp-t',  #算术表达式-t
    'cal-item',  #项
    'cal-item-t',  #项-t
    'cal-factor',  #因子
    'cal-quantity',  #算术量
    'bool-item',  #布尔项
    'bool-item-t',  #布尔项-t
    'bool-factor',  #布尔因子
    'bool-quantity',  #布尔量
    # 'bool-quantity-t',#布尔量-t
    'bool-const',  #布尔常数
    'relation',  #关系符
    'str-exp',  #字符表达式
    # 'const',#常数
]  #+empty


class Sign:
    """
    符号
    """
    def __init__(self, sign_type, sign_num='', ifvar=False, ifbool=False):

        self.type = sign_type
        self.num = sign_num
        self.ifvar = ifvar
        self.ifboolvar = ifbool

    def turn_jump_type(self):
        assert (self.type in ['<', '<=', '<>', '=', '>', '>='])
        type = 'j' + self.type
        num = -2
        return Sign(type, num, self.ifvar, self.ifboolvar)

    def turn_bool_type(self):
        self.ifboolvar = True

    def is_terminal_sign(self):
        """
        是不是终结符
        :return: True/False
        """
        if self.type == 'empty':
            return True
        else:
            for i in terminal_sign_type:
                if i == self.type:
                    return True
            return False

    def is_non_terminal_sign(self):
        """
        是不是非终结符
        :return: True/False
        """
        for i in non_terminal_sign_type:
            if i == self.type:
                return True
        return False

    def is_empty_sign(self):
        """
        是不是空字
        :return: True/False
        """
        return self.type == 'empty'


non_ter_ref = dict(
    zip(non_terminal_sign_type, range(1,
                                      len(non_terminal_sign_type) + 1)))
ter_ref = dict(zip(terminal_sign_type, range(1, len(terminal_sign_type) + 1)))


def ref_Sign_num(type):
    if type in ter_ref.keys():
        return ter_ref[type]
    else:
        return 0


class Production:
    """
    产生式
    """
    def __init__(self,
                 left_type,
                 right_types,):

        self.left = Sign(left_type, ref_Sign_num(left_type))
        self.right = list()

        for i in right_types:
            self.right.append(Sign(i, ref_Sign_num(i)))

        # 调试用的
        self.str = self.left.type + ' ->'
        for i in self.right:
            self.str += ' ' + i.type

     


# 1. <常数> → <整数>│<布尔常数>│<字符常数>
# 2. <布尔常数> → true│false
# 3. <类型> → integer│bool│char

# 4. <算术表达式> → <算术表达式> + <项>│<算术表达式> - <项>│<项>
# 4.1. <算术表达式> → <项><算术表达式-t>
# 4.2. <算术表达式-t> → + <项> <算数表达式-t>| - <项> <算数表达式-t>| empty

# 5. <项> → <项> * <因子>│<项> / <因子>│<因子>
# 5.1. <项> → <因子> <项-t>
# 5.2. <项-t> →  * <因子> <项-t> |  / <因子> <项-t> | empty

# 6. <因子> → <算术量>│- <因子>
# 7. <算术量> → <整数>│<标识符>│（ <算术表达式> ）

# 8. <布尔表达式> → <布尔表达式> or <布尔项>│<布尔项>
# 8.1. <布尔表达式> → <布尔项> <布尔表达式-t>
# 8.2. <布尔表达式-t> → or <布尔项> <布尔表达式-t> | empty

# 9. <布尔项> → <布尔项> and <布因子>│<布因子>
# 9.1. <布尔项> → <布因子> <布尔项-t>
# 9.2. <布尔项-t> → and <布因子> <布尔项-t> | empty

# 10. <布因子> → <布尔量>│not <布因子>
# 11. <布尔量> → <布尔常数>│<标识符>│（ <布尔表达式> ）│
#  <标识符> <关系符> <标识符>│<算术表达式> <关系符> <算术表达式>
# 拆分公共左因子： <布尔量> → <标识符> <关系符> <标识符> | <标识符>
# 13. <关系符> → <│<>│<=│>=│>│=
# 14.（已删除） <字符表达式> → <字符常数>│<标识符>
# 15. <语句> → <赋值句>│<if句>│<while句>│<repeat句>│<复合句>
# 16. <赋值句> → <标识符> := <算术表达式>

# 17. <if句>→ if <布尔表达式> then <语句>│if <布尔表达式> then <语句> else <语句>
# 17.1. <if句> → if <布尔表达式> then <语句> <if句-t>
# 17.2. <if句-t> →  else <语句> | empty

# 18. <while句> → while <布尔表达式> do <语句>
# 19. <repeat句> → repeat <语句> until <布尔表达式>

# 20. <复合句> → begin <语句表> end

# 21. <语句表> → <语句> ；<语句表>│<语句>
# 21.1. <语句表>  → <语句> <语句表-t>
# 21.2. <语句表-t> → ； <语句表> | empty

# 22. <程序> → program <标识符> ；<变量说明> <复合语句> .
# 23. <变量说明> → var <变量定义>│empty

# 24. <变量定义> → <标识符表> ：<类型> ；<变量定义>│<标识符表> ：<类型> ；
# 24.1. <变量定义> → <标识符表> ：<类型> ；<变量定义-t>
# 24.2. <变量定义-t>  → <变量定义> | empty

# 25. <标识符表> → <标识符> ，<标识符表>│<标识符>
# 25.1. <标识符表> → <标识符> <标识符表-t>
# 25.2. <标识符表-t> → ,<标识符表> | empty

productions = [
    #1
    #    Production('const',['int']),
    #    Production('const',['bool-const']),
    #    Production('const',['string']),
    #2
    Production('bool-const', ['true']),
    Production('bool-const', ['false']),
    #3
    Production('type', ['integer']),
    Production('type', ['bool']),
    Production('type', ['char']),
    #4
    #    Production('cal-exp',['cal-exp','+','cal-item']),
    #    Production('cal-exp',['cal-exp','-','cal-item']),
    #    Production('cal-exp',['cal-item']),
    Production('cal-exp', ['cal-item', 'cal-exp-t']),
    Production('cal-exp-t', ['+', 'cal-item', 'cal-exp-t']),
    Production('cal-exp-t', ['-', 'cal-item', 'cal-exp-t']),
    Production('cal-exp-t', ['empty']),
    #5
    #    Production('cal-item',['cal-item','*','cal-factor']),
    #    Production('cal-item',['cal-item','/','cal-factor']),
    #    Production('cal-item',['cal-factor']),
    Production('cal-item', ['cal-factor', 'cal-item-t']),
    Production('cal-item-t', ['*', 'cal-factor', 'cal-item-t']),
    Production('cal-item-t', ['/', 'cal-factor', 'cal-item-t']),
    Production('cal-item-t', ['empty']),
    #6
    Production('cal-factor', ['cal-quantity']),
    Production('cal-factor', ['-', 'cal-factor']),
    # 7. <算术量> → <整数>│<标识符>│（ <算术表达式> ）
    Production('cal-quantity', ['int']),
    Production('cal-quantity', ['ID']),
    Production('cal-quantity', ['(', 'cal-exp', ')']),
    # 8. <布尔表达式> → <布尔表达式> or <布尔项>│<布尔项>
    #    Production('bool-exp',['bool-exp','or','bool-item']),
    #    Production('bool-exp',['bool-item']),
    Production('bool-exp', ['bool-item', 'bool-exp-t']),
    Production('bool-exp-t', ['or', 'bool-item', 'bool-exp-t']),
    Production('bool-exp-t', ['empty']),
    # 9. <布尔项> → <布尔项> and <布因子>│<布因子>
    #    Production('bool-item',['bool-item','and','bool-factor']),
    #    Production('bool-item',['bool-factor']),
    Production('bool-item', ['bool-factor', 'bool-item-t']),
    Production('bool-item-t', ['and', 'bool-factor', 'bool-item-t']),
    Production('bool-item-t', ['empty']),
    # 10. <布因子> → <布尔量>│not <布因子>
    Production('bool-factor', ['bool-quantity']),
    Production('bool-factor', ['not', 'bool-quantity']),
    # 11. <布尔量> → <布尔常数>│<标识符>│（ <布尔表达式> ）│
    #  <标识符> <关系符> <标识符>│<算术表达式> <关系符> <算术表达式>
    Production('bool-quantity', ['bool-const']),
    #需要对bool-quantity再处理，因为有公因式
    Production('bool-quantity',
               ['(', 'bool-exp', ')']),  # 1 3 （冲突 如果下一个）之后有rop则可以选这个
    Production('bool-quantity', ['ID']),  #2 3 ID冲突  如果ID后面没有紧跟rop就选这个
    Production('bool-quantity',
               ['cal-exp', 'relation', 'cal-exp']),  #不满足LL1的罪魁祸首

    #    Production('bool-quantity',['ID','relation','ID']),
    #    Production('bool-quantity',['ID','bool-quantity-t']),
    #    Production('bool-quantity-t',['relation','ID']),
    #    Production('bool-quantity-t',['empty']),

    # 12. <关系符> → <│<>│<=│>=│>│=
    Production('relation', ['<']),
    Production('relation', ['<>']),
    Production('relation', ['<=']),
    Production('relation', ['>=']),
    Production('relation', ['>']),
    Production('relation', ['=']),
    # 13. <语句> → <赋值句>│<if句>│<while句>│<repeat句>│<复合句>
    Production('statement', ['assig-sent']),
    Production('statement', ['if-sent']),
    Production('statement', ['while-sent']),
    Production('statement', ['repeat-sent']),
    Production('statement', ['compound-statement']),
    # 14. <赋值句> → <标识符> := <算术表达式>
    Production('assig-sent', ['ID', ':=', 'cal-exp']),
    # 15. <if句>→ if <布尔表达式> then <语句>│if <布尔表达式> then <语句> else <语句>
    #    Production('if-sent',['if','bool-exp','then','statement']),
    #    Production('if-sent',['if','bool-exp','then','statement','else','statement']),
    Production('if-sent',
               ['if', 'bool-exp', 'then', 'statement', 'if-sent-t']),
    Production('if-sent-t', ['else', 'statement']),
    Production('if-sent-t', ['empty']), 
    #    Production('if-else-t',['assig-sent']),
    #    Production('if-else-t',['while-sent']),
    #    Production('if-else-t',['repeat-sent']),
    #    Production('if-else-t',['compound-statement']),

    #    Production('if-sent-t',['empty']),#不满足LL1的罪魁祸首
    # 16. <while句> → while <布尔表达式> do <语句>
    Production('while-sent', ['while', 'bool-exp', 'do', 'statement']),
    # 17. <repeat句> → repeat <语句> until <布尔表达式>
    Production('repeat-sent', ['repeat', 'statement', 'until', 'bool-exp']),
    # 18. <复合句> → begin <语句表> end
    Production('compound-statement', ['begin', 'statement-list', 'end']),
    # 19. <语句表> → <语句> ；<语句表>│<语句>
    #    Production('statement-list',['statement',';','statement-list']),
    #    Production('statement-list',['statement']),
    Production('statement-list', ['statement', 'statement-list-t']),
    Production('statement-list-t', [';', 'statement-list']),
    Production('statement-list-t', ['empty']),
    # 20. <程序> → program <标识符> ；<变量说明> <复合语句> .
    Production(
        'program-start',
        ['program', 'ID', ';', 'var-declear', 'compound-statement', '.']),
    # 21. <变量说明> → var <变量定义>│ε
    Production('var-declear', ['var', 'var-define']),
    Production('var-declear', ['empty']),
    # 22. <变量定义> → <标识符表> ：<类型> ；<变量定义>│<标识符表> ：<类型> ；
    #    Production('var-define',['id-list',':','type',';','var-define']),
    #    Production('var-define',['id-list',':','type',';']),
    Production('var-define', ['id-list', ':', 'type', ';', 'var-define-t']),
    Production('var-define-t', ['var-define']),
    Production('var-define-t', ['empty']),
    # 23. <标识符表> → <标识符> ，<标识符表>│<标识符>
    Production('id-list', ['ID', 'id-list-t']),
    Production('id-list-t', [',', 'id-list']),
    Production('id-list-t', ['empty']),
]

pro_ref = dict(zip(range(len(productions)), productions))

grammar_start = Sign('program-start')


class PredictingAnalysisTable:
    """
    预测分析表
    """
    def __init__(self):
        # 错误
        self.error = None

        # 预测分析表
        self.table = list()

        self.resolve_table = list()

        # 所有的非终结符
        self.non_terminal_signs = list()
        # 所有的终结符
        self.terminal_signs = list()

        # 载入所有的符号
        for i in non_terminal_sign_type:
            self.non_terminal_signs.append(Sign(i))
        for i in terminal_sign_type:
            self.terminal_signs.append(Sign(i))

        # 根据非终结符和终结符的数量为预测分析表分配空间，并且为每一个格子预先填上 None
        for i in non_terminal_sign_type:
            self.table.append(list())
            self.resolve_table.append(list())
        for i in range(0, len(non_terminal_sign_type)):
            for j in terminal_sign_type:
                self.table[i].append(None)
                self.resolve_table[i].append(None)

        # 为每一个非终结符建立 first 集和 follow 集
        self.firsts = list()
        self.follows = list()

        # 为每一个非终结符的 first 集和 follow 集分配空间
        for i in non_terminal_sign_type:
            self.firsts.append(list())
            self.follows.append(list())

    def compile(self):
        """
        编译预测分析表
        """
        # 对每一个文法元素求其 first 集
        self.calculate_firsts()
        # 对每一个文法元素求其 follow 集
        self.calculate_follows()
        # 根据 first 集和 follow 集生成预测分析表
        success = self.generate_table()
        return success

    def get_production(self, non_terminal_sign, terminal_sign):

        x = self.get_non_terminal_sign_index(non_terminal_sign)
        y = self.get_terminal_sign_index(terminal_sign)
        return self.table[x][y]

    @classmethod
    def set_add(cls, container, sign):

        exist = False
        for elem in container:
            if elem.type == sign.type:
                exist = True
        if not exist:
            container.append(sign)
        return not exist

    def get_terminal_sign_index(self, terminal_sign):

        for i in range(0, len(self.terminal_signs)):
            if terminal_sign.type == self.terminal_signs[i].type:
                return i
        return -1

    def get_non_terminal_sign_index(self, non_terminal_sign):

        for i in range(0, len(self.non_terminal_signs)):
            if non_terminal_sign.type == self.non_terminal_signs[i].type:
                return i
        return -1

    def get_non_terminal_sign_first(self, non_terminal_sign):

        return self.firsts[self.get_non_terminal_sign_index(non_terminal_sign)]

    def get_non_terminal_sign_first_no_empty(self, non_terminal_sign):

        result = list()
        for i in self.get_non_terminal_sign_first(non_terminal_sign):
            if not i.is_empty_sign():
                result.append(i)
        return result

    def is_empty_in_non_terminal_sign_first(self, non_terminal_sign):

        for i in self.get_non_terminal_sign_first(non_terminal_sign):
            if i.is_empty_sign():
                return True
        return False

    def get_non_terminal_sign_follow(self, non_terminal_sign):

        return self.follows[self.get_non_terminal_sign_index(
            non_terminal_sign)]

    def calculate_firsts(self):
        """
        求所有的 first 集
        """
        # 立一个 flag，用来标志 firsts 集是否增大
        flag = True
        # 开始循环
        while flag:
            flag = False
            # 在每一次循环之中遍历所有产生式
            for production in productions:
                # 如果产生式右边为空
                if len(production.right) == 0:
                    # 将空字加入其 first 集
                    if self.set_add(
                            self.get_non_terminal_sign_first(production.left),
                            Sign('empty')):
                        flag = True
                # 如果产生式右边不为空
                else:
                    # 如果是以终结符开头，将终结符添加到其 first 集
                    if production.right[0].is_terminal_sign():
                        if self.set_add(
                                self.get_non_terminal_sign_first(
                                    production.left), production.right[0]):
                            flag = True
                    # 如果是以非终结符开头
                    elif production.right[0].is_non_terminal_sign():
                        # (1) 将开头非终结符的 first 集中的所有非空元素添加到产生式左边非终结符的 first 集中
                        bigger = False
                        for i in self.get_non_terminal_sign_first_no_empty(
                                production.right[0]):
                            if self.set_add(
                                    self.get_non_terminal_sign_first(
                                        production.left), i):
                                bigger = True
                        if bigger:
                            flag = True

                        # (2) 从第一个非终结符开始循环，如果其 first 集中包含空字，那么将它下一个符号的 first
                        # 集添加到产生式左边非终结符的 first 集中去
                        for i in range(0, len(production.right)):
                            if production.right[i].is_non_terminal_sign():
                                # 如果包含空字
                                if self.is_empty_in_non_terminal_sign_first(
                                        production.right[i]):
                                    # 如果它是最后一个，将空字填入
                                    if i == len(production.right) - 1:
                                        if self.set_add(
                                                self.
                                                get_non_terminal_sign_first(
                                                    production.left),
                                                Sign('empty')):
                                            flag = True
                                    # 如果不是最后一个
                                    else:
                                        # 如果它之后是终结符
                                        if production.right[
                                                i + 1].is_terminal_sign():
                                            if self.set_add(
                                                    self.
                                                    get_non_terminal_sign_first(
                                                        production.left),
                                                    production.right[i + 1]):
                                                flag = True
                                        # 如果它之后是非终结符
                                        elif production.right[
                                                i + 1].is_non_terminal_sign():
                                            bigger = False
                                            for j in self.get_non_terminal_sign_first_no_empty(
                                                    production.right[i + 1]):
                                                if self.set_add(
                                                        self.
                                                        get_non_terminal_sign_first(
                                                            production.left),
                                                        j):
                                                    bigger = True
                                            if bigger:
                                                flag = True
                                        else:
                                            self.error = SyntaxRuleError(
                                                '终结符或非终结符类型错误')
                                            return False
                                # 如果不包含空字
                                else:
                                    break
                            else:
                                break
                    # 否则报错
                    else:
                        self.error = SyntaxRuleError('终结符或非终结符类型错误')
                        return False

    def calculate_follows(self):
        """
        求所有的 follow 集
        """
        first = list()
        flag = True
        while flag:
            flag = False
            # 遍历所有产生式
            for production in productions:
                # 如果产生式左边是开始符号
                if production.left.type == grammar_start.type:
                    if self.set_add(
                            self.get_non_terminal_sign_follow(production.left),
                            Sign('pound')):
                        flag = True

                # 遍历产生式右边
                for i in range(0, len(production.right)):
                    # 如果是非终结符
                    if production.right[i].is_non_terminal_sign():
                        # 如果它是产生式最后一个符号
                        if i == len(production.right) - 1:
                            # 将产生式左边非终结符的 follow 集添加到这个符号的 follow 集中
                            bigger = False
                            for j in self.get_non_terminal_sign_follow(
                                    production.left):
                                if self.set_add(
                                        self.get_non_terminal_sign_follow(
                                            production.right[i]), j):
                                    bigger = True
                            if bigger:
                                flag = True
                        # 否则观察其之后的元素
                        else:
                            # 求他之后所有符号集合的 first 集
                            first.clear()
                            first += self.calculate_set_first(
                                production.right[i + 1:])
                            # (1) 将 first 中所有非空元素填入 follow
                            empty_find = False
                            for f in first:
                                if not f.is_empty_sign():
                                    self.set_add(
                                        self.get_non_terminal_sign_follow(
                                            production.right[i]), f)
                                else:
                                    empty_find = True

                            # (2) 如果 first 中含有空
                            if empty_find:
                                # 将产生式左边非终结符的 follow 集添加到这个符号的 follow 集中
                                bigger = False
                                for j in self.get_non_terminal_sign_follow(
                                        production.left):
                                    if self.set_add(
                                            self.get_non_terminal_sign_follow(
                                                production.right[i]), j):
                                        bigger = True
                                if bigger:
                                    flag = True

                    elif production.right[i].is_terminal_sign():
                        continue
                    # 否则报错
                    else:
                        self.error = SyntaxRuleError('终结符或非终结符类型错误')
                        return False

    def calculate_set_first(self, container):
        """
        计算一系列符号的 first 集
        """
        first = list()

        # 开始求 first 集
        # 如果集合为空
        first = list()

        # 开始求 first 集
        # 如果产生式右边为空
        if len(container) == 0:
            # 将空字加入其 first 集
            self.set_add(first, Sign('empty'))
        # 如果产生式右边补位空
        else:
            # 如果是以终结符开头，将终结符添加到 first 集
            if container[0].is_terminal_sign():
                self.set_add(first, container[0])
            # 如果是以非终结符开头
            elif container[0].is_non_terminal_sign():
                # (1) 将开头非终结符的 first 集中的所有非空元素添加到 first 中
                for i in self.get_non_terminal_sign_first_no_empty(
                        container[0]):
                    self.set_add(first, i)

                # (2) 从第一个非终结符开始循环，如果其 first 集中包含空字，那么将它的下一个符号的 first
                # 集添加到 first 中
                for i in range(0, len(container)):
                    if container[i].is_non_terminal_sign():
                        # 如果包含空字
                        if self.is_empty_in_non_terminal_sign_first(
                                container[i]):
                            # 如果它是最后一个，将空字填入
                            if i == len(container) - 1:
                                self.set_add(first, Sign('empty'))
                            # 如果不是最后一个
                            else:
                                # 如果它之后是终结符
                                if container[i + 1].is_terminal_sign():
                                    self.set_add(first, container[i + 1])
                                # 如果它之后是非终结符
                                elif container[i + 1].is_non_terminal_sign():
                                    for j in self.get_non_terminal_sign_first_no_empty(
                                            container[i + 1]):
                                        self.set_add(first, j)
                                # 否则报错
                                else:
                                    self.error = SyntaxRuleError(
                                        '终结符或非终结符类型错误')
                                    return False
                        # 如果不含空字
                        else:
                            break
                    else:
                        break
            # 否则报错
            else:
                self.error = SyntaxRuleError('终结符或非终结符类型错误')
                return False

        return first

    def insert_to_table(self, production, terminal):
        """
        将产生式插入预测分析表对应位置
        """
        # 先判断应该插入到的位置
        x = self.get_non_terminal_sign_index(production.left)
        y = self.get_terminal_sign_index(terminal)

        # 如果那个位置已经有产生式了
        if self.table[x][y]:
            # 判断这个产生式是不是与要插入的产生式一样
            same_left = production.left.type == self.table[x][y].left.type
            if same_left:
                same_right = True
                if len(production.right) != len(self.table[x][y].right):
                    self.error = SyntaxRuleError("文法非LL(1)" + production.str)
                    if not self.resolve_table[x][y]:
                        self.resolve_table[x].insert(y, production)
                        return True
                    # return False
                else:
                    for i in range(0, len(production.right)):
                        if production.right[i].type != self.table[x][y].right[
                                i].type:
                            same_right = False
                    if same_right:
                        # 执行插入
                        del self.table[x][y]
                        self.table[x].insert(y, production)
                        return True
                    else:
                        self.error = SyntaxRuleError("文法非LL(1)" +
                                                     production.str)
                        if not self.resolve_table[x][y]:
                            self.resolve_table[x].insert(y, production)
                            return True
                        # return False
            else:
                self.error = SyntaxRuleError("文法非LL(1)出大错，将无法正确编译" + production.str)
                return False
        # 如果那个位置为空，说明可以填入
        else:
            # 执行插入
            del self.table[x][y]
            self.table[x].insert(y, production)
            return True

    @classmethod
    def set_have_repeat(cls, set1, set2):
        """
        判断两个集合是否有交集
        """
        for i in set1:
            for j in set2:
                if i.type == j.type:
                    return True
        return False

    

    def generate_table(self):
        """
        根据 first 集和 follow 集生成预测分析表
        :return: 是否生成成功
        """
        # 调试
        # self.grammar_rule_debug()

        # 对每一条产生式应用规则
        for production in productions:
            # 先求出该产生式右边部分的 first 集
            first = self.calculate_set_first(production.right)

            # 对每一个 first 集中的每一个终结符执行操作
            empty_find = False
            for i in list(first):
                if i.type == 'empty':
                    empty_find = True
                else:
                    if not self.insert_to_table(production, i):
                        return False

            # 如果其 first 集中有空字，则对 follow 集中的每一个终结符执行操作
            if empty_find:
                for i in self.get_non_terminal_sign_follow(production.left):
                    if not self.insert_to_table(production, i):
                        return False

        return True


if __name__ == "__main__":

    # test = PredictingAnalysisTable()

    # print('LL1文法：', test.compile())
    # print(len(test.follows))
    # # confilct_y
    # count = 0
    # confilct_y = None
    # confilct_x = None
    # for i in test.resolve_table:
    #     count += 1
    #     for j in range(len(i)):
    #         if i[j] :
    #             confilct_y = j
    #             confilct_x = count
    #             print('select when :',terminal_sign_type[j])
    #             print(test.table[confilct_x][confilct_y])

    #             print(i[j].str)

    print("Description: \nAuthor: He Yuhang\nGithub: https://github.com/hyhhhhhhhh\nDate: 2020-11-24 12:02:12\nLastEditors: Box\nLastEditTime: 2020-12-13 18:54:01")
    print("class: 2018 jk_2")
    print("StudentID: 201830170110")
    name = input('请输入文件名：')

    fo2 = open(name, "r")
    # fo2 = open("sample2.txt", 'r')
    string2 = ''
    string3 = ''
    for line in fo2.readlines():
        string2 += line
    # for line in fo3.readlines():
    #     string3 += line

    test2 = getTokens(string2)
    if test2.scanner():
        test2.generate()
        test2.printres()
    else:
        print('error')
        print(test2.error)
