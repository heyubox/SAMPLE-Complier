'''
Description: 
Author: He Yuhang
Github: https://github.com/hyhhhhhhhh
Date: 2020-12-07 23:06:23
LastEditors: Box
LastEditTime: 2020-12-15 01:03:51
'''
import re
from typing import NewType

from compiler import *
from compiler import (non_ter_ref, non_terminal_sign_type, productions,
                      ter_ref, terminal_sign_type)

jump_num = -2
tempvar_num = -1
jump_res = -3
program_reached = -4


# from queue import Queue
class Stack:
    def __init__(self):

        self.__container = list()

    def push(self, elem):

        self.__container.append(elem)

    def pop(self):

        top = self.top()
        self.__container.pop()
        return top

    def top(self):

        return self.__container[-1]

    def empty(self):

        return len(self.__container) == 0

    def debugT(self):
        print(self.top().type)
        for i in self.__container:
            print(i.type)

    #读栈直到读取到一对（），然后判断）是否后跟rop
    def if_rop_follows(self):
        """expecially for todo Stack"""
        # true select 'bool-quantity',['cal-exp','relation','cal-exp']
        if self.top().type != '(':
            return False
        ropStack = list()
        check_pos = False
        breakout = False
        for i in self.__container[::-1]:
            if check_pos and i.type not in [
                    'and', 'or', 'do', 'else', 'until', 'end', ';', ')', ';',
                    'then'
            ]:
                return True
            if breakout:
                break
            if i.type == '(':
                ropStack.append(i.type)
            elif i.type == ')':
                if len(ropStack) == 1:
                    # 匹配到最后一个')'
                    check_pos = True
                    breakout = True
                else:
                    ropStack.pop()
        return False
        # assert()

    def if_rop_after_ID(self):
        """expecially for todo Stack"""
        # true select 'bool-quantity',['cal-exp','relation','cal-exp']
        return self.__container[-1].num == 36 and self.__container[
            -2].type not in [
                'and', 'or', 'do', 'else', 'until', 'end', ';', ')', ';',
                'then'
            ]

    def get_program_ID(self):
        """expecially for todo Stack"""
        return self.__container[-2]


Signs_test = [Sign('program-start', 23)]


class readin_tokens:
    def __init__(self, filename):
        self.f = filename

        self.Signs = list()

        file = open(filename, 'r')

        while True:
            line = file.readline()
            if not line:
                break
            line = line.replace(' ', '', 1).replace('(', '', 1).replace(
                ',', '', 1).replace('-', '', 1).replace(')', '',
                                                        1).replace('\n', '')
            line = re.split('\s+', line)
            self.Signs.append(
                Sign(line[-1],
                     int(line[0]),
                     ifvar=True if line[0] == '36' else False))
        self.Signs.append(Sign('#'))


class code:
    def __init__(self, op, arg1=Sign('#'), arg2=Sign('#'), result=Sign('#')):
        '''
        description: 
        param {操作符op 变量arg1 变量arg2 结果result}
        return {*}
        '''
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.res = result
        # 调试用
        self.str_code = '(' + self.op.type + ',' + self.arg1.type + ',' + self.arg2.type + ',' + self.res.type + ')'

    def updateStr(self):
        self.str_code = '(' + self.op.type + ',' + self.arg1.type + ',' + self.arg2.type + ',' + self.res.type + ')'


class EmitTumple:
    def __init__(self, t, f, p):
        '''
        description: 
        param {真出口四元式t 假出口四元式f 真出口四元式地址p}
        return {*}
        '''
        self.t = t
        self.f = f
        self.pointer = p
        # 调试用
        self.block_str = self.t.str_code + '\n' + self.f.str_code

    def updateStr(self):
        self.t.updateStr()
        self.f.updateStr()
        self.block_str = self.t.str_code + '\n' + self.f.str_code


class generator:
    def __init__(self, table, Signs=Signs_test, sec_table=None):
        self.error = None
        Signs.reverse()

        self.todo = Stack()
        for i in Signs:
            self.todo.push(i)

        self.state = Stack()
        self.state.push(Sign('#'))
        self.state.push(grammar_start)

        self.table = table
        self.sec_tbale = sec_table

        self.newtemp = 0

        self.var_list = list()
        # 标识符表

        self.emit_list = list()
        # 四元式表

        self.expS = list()
        # exp栈

        self.bexpS = list()
        # boolexp栈

        self.temp_var = 1
        # 临时变量标记

    '''
    description: 
    param {*} self
    return {*}
    '''

    def matchTer(self):
        '''
        description: 
        param { }
        return {匹配的终结符ter_list 是否匹配了空串 }
        '''
        # 产生式栈顶empty pop(empty) 回退
        if self.state.top().type == 'empty':
            self.state.pop()
            return [], True
        ter_list = list()
        while True:
            peek = self.state.top()
            top = self.todo.top()
            # 栈顶终结符而且与队顶匹配
            if top.num and top.num == peek.num:
                if top.num == 36:
                    if_var_defined = False
                    for i in self.var_list:
                        if i.type == top.type:
                            if_var_defined = True
                    #标识符是否被定义：
                    if not if_var_defined:
                        self.error = "error:" + top.type + "未定义"
                        print(self.error)
                        exit()
                self.state.pop()
                self.todo.pop()
                ter_list.append(top)
            # 逆栈是终结符，但是与栈不匹配
            elif peek.num:
                self.error = 'error:不符合文法定义'
                print(self.error)
                exit()
            else:
                break

        return ter_list, False

    def getStack(self):
        '''
        description: 
        param { }
        return {分析栈栈顶 剩余输入串栈顶}
        '''
        return self.state.top(), self.todo.top()

    def match1(self, x, y):
        # 试图在table表中寻找产生式，匹配则返回产生式，否则返回False
        if self.table[x][y]:
            self.error = None
            return self.table[x][y]
        else:
            return False

    def match2(self, x, y):
        # 试图在sec_table表(即resolve_table)中寻找产生式，匹配则返回产生式，否则返回False
        if self.sec_tbale[x][y]:
            self.error = None
            return self.sec_tbale[x][y]
        else:
            return False

    def match(self, x, y):
        '''
        description: 
        param {分析栈栈顶符号x 剩余输入串栈顶y}
        return {匹配到的产生式p 分析栈栈顶符号x}
        '''
        xid = non_ter_ref[x.type] - 1
        yid = y.num - 1
        # 匹配到产生式p1
        p1 = self.match1(xid, yid)
        # 匹配到产生式p2
        p2 = self.match2(xid, yid)
        # 如果p1 p2非False，则匹配到冲突，进行冲突解决
        if p1 and p2:
            #'bool-quantity',['cal-exp','relation','cal-exp'] IN p2
            # # 1 3 （冲突 判断下一个）之后是不是bool-quantity的follow集合
            if self.todo.if_rop_follows():
                return p2, x.type
            #2 3 ID冲突  判断ID后面是不是bool-quantity的follow集合
            elif self.todo.if_rop_after_ID():
                return p2, x.type
            else:
                # if-sent-t冲突，默认不处理
                # if-sent-t -> empty IN p2
                return p1, x.type
        # 产生式无匹配，判断是否能选择空产生式
        elif not (p1 or p2):
            # 能否使用empty产生式
            for i in productions:
                if i.left.type == x.type and i.right[0].type == 'empty':
                    return i, x.type
            # 不能使用空产生式，报错
            self.error = "无法匹配" + y.type
            print(self.error)
            exit()
        #产生式唯一匹配，直接返回
        else:
            return p1, x.type

    def productionInS(self):
        '''
        description: 
        param { }
        return { 是否找到正确的产生式}
        '''
        arg1, arg2 = self.getStack()
        # 根据分析栈和剩余输入串栈顶确定产生式
        production, arg1 = self.match(arg1, arg2)
        if arg1 == production.left.type:
            self.state.pop()
            for i in reversed(production.right):
                self.state.push(i)
            # 匹配到的产生式逆序入栈完成

            return True

        return False

    def dealExp(self):
        '''
        description: 
        param {*}
        return {算数表达式的四元式 最后的临时变量或运算量}
        '''
        res = None
        to_emit = []
        stack = Stack()
        # 如果只有栈中只有一个元素，则单独一个标识符构成算数表达式
        # 不处理，直接返回
        if len(self.expS) == 1:
            return False, self.expS.pop()
        # 后缀式的计算处理原理
        else:
            while len(self.expS):
                i = self.expS[0]
                # 如果扫描到运算量
                if i.num in [36, 37, 38]:
                    stack.push(i)
                    self.expS.pop(0)
                # 如果扫描到运算符号
                elif i.type in ['+', '-', '*', '/']:
                    # 出栈栈顶两个运算量
                    op = self.expS.pop(0)
                    arg1 = stack.pop()
                    arg2 = stack.pop()
                    res = Sign('T' + str(self.temp_var), -1, True)
                    stack.push(res)
                    # 生成对应四元式
                    to_emit.append(code(op, arg2, arg1, res))
                    self.temp_var += 1
        self.expS = list()
        return to_emit, res

    def dealAssigExp(self, ID, assig):
        res = None
        to_emit = []
        if len(self.expS) == 1:
            # 如果只有栈中只有一个元素，则单独一个标识符构成算数表达式
            self.emit_arg(assig, self.expS.pop(), Sign('-', None), ID)
        else:
            # 调用dealExp，得到临时变量和一串四元式
            to_emit, res = self.dealExp()
            for i in to_emit:
                self.emit_code(i)
            self.emit_arg(assig, res, Sign('-', None), ID)
        pass

    def dealExpINBool(self):
        '''
        description: 
        param {*}
        return {参与布尔表达式的运算量}
        '''
        # 调用dealExp，得到临时变量和一串四元式
        to_emit, res = self.dealExp()  # to_emit: False list() res: Sign
        if to_emit == False:  # to_emit 空
            # 栈中只有一个元素，则单独一个标识符构成算数表达式，返回算数表达式
            return res
        else:
            # 将生式的四元式提交，返回最后生成的算数量，即变量
            for i in to_emit:
                self.emit_code(i)
            return res
            exit()  #未知

    def fillBack(self, code_begin, Etrue, fillin):
        for i in range(code_begin, Etrue):
            fillback = self.emit_list[i].res
            if fillback.num == -3 and fillback.type == 'None':
                self.emit_list[i].res.type = str(fillin)
                self.emit_list[i].updateStr()

    def dealBool(self, keepTrue=True):
        '''
        description: 
        param {keepTrue是否留下真出口}
        return {生成的四元式to_emit 最终的真/假出口位置p}
        '''
        # 获取p，为了正确地确定每个四元式的绝对地址
        p = self.newtemp
        stack = Stack()
        # 一个block就是一个确定了block内部真假出口跳转的代码块
        # 未确定的出口待回填
        # block 是EmitTumple列表
        # 每个EmitTumple列表里存放了，一组四元式，对应真出口和假出口
        block = None
        # 根据and or优先级，存放处理好的子block
        block_stack = Stack()
        # 循环处理栈中元素
        while len(self.bexpS):
            i = self.bexpS[0]
            if i.ifboolvar:
                # 标识符单独构成表达式 生成Block
                # Block 入栈
                block = [
                    EmitTumple(
                        code(Sign('jz', jump_num), i, Sign('-', None),
                             Sign('None', jump_res)),
                        code(Sign('j', jump_num), Sign('-', None),
                             Sign('-', None), Sign('None', jump_res)), p)
                ]
                p += 2
                block_stack.push(block)
                # self.bexpS.pop(0)
            elif i.type == 'not':
                # not 则调转真假出口位置
                reverse = block_stack.pop()
                for r in reverse:
                    temp = r.t
                    r.t = r.f
                    r.f = temp
                    r.updateStr()
                block_stack.push(reverse)
                pass
            elif i.type in ['true', 'false']:
                # 布尔常量单独构成表达式 生成Block
                # Block 入栈
                block = [
                    EmitTumple(
                        code(
                            Sign('jz', jump_num), i, Sign('-', None),
                            Sign('None' if i.type == 'true' else '0',
                                 jump_res)),
                        code(
                            Sign('j', jump_num), Sign('-', None),
                            Sign('-', None),
                            Sign('None' if i.type == 'false' else '0',
                                 jump_res)), p)
                ]
                p += 2
                block_stack.push(block)
            elif i.num in [36, 37, tempvar_num]:
                # 扫描到标识符 尝试 临时变量，压栈
                stack.push(i)
                # self.bexpS.pop(0)
            elif i.type in ['<', '<=', '<>', '=', '>', '>=']:
                # 扫描到rop
                # 出栈栈顶的两个布尔量
                op = i  # self.bexpS.pop(0)
                arg1 = stack.pop()
                arg2 = stack.pop()
                # 生成代码block
                block = [
                    EmitTumple(
                        code(op.turn_jump_type(), arg2, arg1,
                             Sign('None', jump_res)),
                        code(Sign('j', jump_num), Sign('-', None),
                             Sign('-', None), Sign('None', jump_res)), p)
                ]
                p += 2
                block_stack.push(block)
            elif i.type == 'and':
                # 将and左右两个子block用merge生成新的子block
                # 处理Block栈
                b2 = block_stack.pop()
                b1 = block_stack.pop()
                block = self.mergeAnd(b1, b2)
                block_stack.push(block)
                # self.bexpS.pop(0)
            elif i.type == 'or':
                # 将or左右两个子block用merge生成新的子block
                b2 = block_stack.pop()
                b1 = block_stack.pop()
                block = self.mergeOr(b1, b2)
                block_stack.push(block)
                # self.bexpS.pop(0)
            self.bexpS.pop(0)
        # 栈清空 回填所有真出口 留下假出口
        emit_tumple_list = block_stack.pop()
        if keepTrue:
            for i in emit_tumple_list:
                if i.t.res.type == 'None':
                    i.t.res = Sign(str(p), jump_res)
        else:
            # 栈清空 回填所有假出口 留下真出口
            for i in emit_tumple_list:
                if i.f.res.type == 'None':
                    i.f.res = Sign(str(p), jump_res)
        to_emit = list()
        # 从一组一组的真假出口四元式中，提取一个一个四元式
        for i in emit_tumple_list:
            # 处理not的一组四元式，调转出口
            if i.t.op.type == 'j':
                temp = i.t
                i.t = i.f
                i.f = temp
            i.updateStr()
            to_emit.append(i.t)
            to_emit.append(i.f)
        return to_emit, p

    def mergeAnd(self, b1, b2):
        # block = None
        backfill = b1[0].pointer + len(b1) * 2
        for i in b1:
            if i.t.res.type == 'None':
                i.t.res.type = str(backfill)
            i.updateStr()
            # pbegin+=2
        # for i in b2:
        # pbegin+=2

        return self.mergeBlock(b1, b2)

    def mergeBlock(self, b1, b2):
        for i in b2:
            b1.append(i)
        return b1

    def mergeOr(self, b1, b2):
        backfill = b1[0].pointer + len(b1) * 2
        for i in b1:
            if i.f.res.type == 'None':
                i.f.res.type = str(backfill)
            i.updateStr()
        #     pbegin+=2
        # for i in b2:
        #     pbegin+=2
        return self.mergeBlock(b1, b2)

    def jumpOpt(self):
        flag = True
        while flag:
            flag = False
            for i in self.emit_list:
                if i.op.type == 'j':
                    sent_jump_to = int(i.res.type)
                    jump_res = self.emit_list[sent_jump_to]
                    if jump_res.op.type == 'j':
                        #优化跳转 拉链
                        i.res.type = jump_res.res.type
                        i.updateStr()
                        flag = True

    # ter_list实际上是一个状态，它可能是：
    # []：match到empty
    # list():这个句子match到的Ter
    def generate(self):
        if self.productionInS():
            # 产生式匹配入队完成
            self.program_start()
            # var-declear
            self.var_declear()
            # compound-statement
            self.compound_statement()
            todo_end = self.todo.pop()
            state_end = self.state.pop()
            if todo_end.type == state_end.type and todo_end.type == '#':
                self.emit_arg(Sign('sys', program_reached), Sign('-', None),
                              Sign('-', None), Sign('-', None))
                # 优化跳转
                self.jumpOpt()
                print('编译成功')
                for i in range(len(self.emit_list)):
                    print(str(i) + ': ' + self.emit_list[i].str_code)
            return

    def compound_statement(self, zipper=None):
        if self.productionInS():
            ter_list, isempty = self.matchTer()
            self.statement_list(zipper=zipper)
            ter_list, isempty = self.matchTer()
            return

    def statement_list(self, zipper=None):
        if self.productionInS():
            ter_list, isempty = self.matchTer()
            self.statement(zipper=zipper)
            ter_list, isempty = self.matchTer()
            self.statement_list_t(zipper=zipper)
            ter_list, isempty = self.matchTer()
            return

    def statement(self, zipper=None):
        if self.productionInS():
            ter_list, _ = self.matchTer()
            current_state = self.state.top().type
            if current_state == 'assig-sent':
                self.assig_sent()
            elif current_state == 'if-sent':
                self.if_sent(zipper=zipper)
            elif current_state == 'while-sent':
                self.while_sent(zipper=None)
            elif current_state == 'repeat-sent':
                self.repeat_sent(zipper=None)
            elif current_state == 'compound-statement':
                self.compound_statement(zipper=zipper)
            return

    def if_sent(self, zipper=None):
        to_emit = list()
        code_begin = self.newtemp
        zipper = code_begin if not zipper else zipper
        if self.productionInS():
            ter_list, _ = self.matchTer()  # match if
            self.bool_exp()
            to_emit, Etrue = self.dealBool()
            for i in to_emit:
                self.emit_code(i)
            ter_list, _ = self.matchTer()  # match then
            self.statement(zipper if zipper else code_begin)
            # 假出口回填

            ter_list, _ = self.matchTer()
            self.if_sent_t(zipper if zipper else code_begin, code_begin, Etrue)
            Etrue = self.newtemp
            self.fillBack(code_begin, Etrue, self.newtemp)

        pass

    def if_sent_t(self, zipper=None, backfill_b=None, backfill_e=None):
        if self.productionInS():
            current_state = self.todo.top().type

            if current_state == 'else':
                ter_list, _ = self.matchTer()  # match else
                # jump out of ELSE
                self.emit_arg(Sign('j', jump_num), Sign('-', None),
                              Sign('-', None), Sign('None', jump_res))
                self.fillBack(backfill_b, backfill_e, self.newtemp)
                self.statement(zipper)
                return
            else:  # match empty
                ter_list, _ = self.matchTer()
                self.fillBack(backfill_b, backfill_e, self.newtemp)
                return
            pass

    def repeat_sent(self, zipper=None):
        to_emit = list()
        code_begin = self.newtemp
        zipper = code_begin if not zipper else zipper
        if self.productionInS():
            ter_list, _ = self.matchTer()  # match repeat
            self.statement(zipper if zipper else code_begin)
            ter_list, _ = self.matchTer()  # match until
            backfill_begin = self.newtemp
            self.bool_exp()
            to_emit, Etrue = self.dealBool()
            for i in to_emit:
                self.emit_code(i)
            # 真则跳出 假则回跳
            # 假出口回填
            # Etrue = self.newtemp
            self.fillBack(zipper if zipper else code_begin, Etrue, code_begin)

        pass

    def while_sent(self, zipper=None):
        to_emit = list()
        code_begin = self.newtemp
        zipper = code_begin if not zipper else zipper
        if self.productionInS():
            ter_list, _ = self.matchTer()  # return Sign: while
            self.bool_exp()
            to_emit, _ = self.dealBool()
            for i in to_emit:
                self.emit_code(i)
            ter_list, _ = self.matchTer()  # return Sign : do
            self.statement(zipper if zipper else code_begin)
            Etrue = self.newtemp
            # 循环跳转
            self.emit_arg(Sign('j', jump_num), Sign('-', None),
                          Sign('-', None), Sign(str(code_begin), jump_res))
            # 假链回填
            self.fillBack(zipper if zipper else code_begin, Etrue,
                          self.newtemp)

        return

    def bool_exp(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer()
            self.bool_item()
            ter_list, isempty = self.matchTer()
            self.bool_exp_t()

            pass

    def bool_exp_t(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer()  # match 'or' empty
            if isempty:
                return
            else:
                or_op = ter_list[0]
                self.bool_item()
                ter_list, isempty = self.matchTer()
                self.bool_exp_t()
                self.bexpS.append(or_op)
                return

    def bool_item(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer()
            self.bool_factor()
            ter_list, isempty = self.matchTer()
            self.bool_item_t()

    def bool_item_t(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer()  # match 'and' empty
            if isempty:
                return None
            else:
                and_op = ter_list[0]
                self.bool_factor()
                ter_list, isempty = self.matchTer()
                self.bool_item_t()
                self.bexpS.append(and_op)
                return

    def bool_factor(self):
        if self.productionInS():
            current_state = self.state.top().type
            if current_state == 'not':
                not_op = self.state.top()
                ter_list, isempty = self.matchTer()
                self.bool_quantity()
                self.bexpS.append(not_op)
            elif current_state == 'bool-quantity':
                ter_list, isempty = self.matchTer()
                self.bool_quantity()

    def bool_quantity(self):
        if self.productionInS():
            current_state = self.state.top().type
            if current_state == '(':
                ter_list, isempty = self.matchTer()
                self.bool_exp()
                ter_list, isempty = self.matchTer()
            elif current_state == 'ID':
                ter_list, isempty = self.matchTer()
                ter_list[0].turn_bool_type()
                self.bexpS.append(ter_list[0])
            elif current_state == 'cal-exp':
                ter_list, isempty = self.matchTer()
                self.cal_exp()
                res1 = self.dealExpINBool()
                ter_list, isempty = self.matchTer()
                ter_op = self.relation()
                ter_list, isempty = self.matchTer()
                self.cal_exp()
                res2 = self.dealExpINBool()
                #结果入栈
                self.bexpS.append(res1)
                self.bexpS.append(res2)
                self.bexpS.append(ter_op)
            elif current_state == 'bool-const':
                ter_list, isempty = self.matchTer()
                self.bool_const()
            pass

    def bool_const(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer()
            self.bexpS.append(ter_list[0])

    def relation(self):
        if self.productionInS():
            ter_op, isempty = self.matchTer()
            return ter_op[0]
            # rop 入栈
            pass

    def assig_sent(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer()
            assig_res = self.cal_exp()
            self.dealAssigExp(ter_list[0], ter_list[1])
            return

    def cal_exp(self):
        if self.productionInS():
            ter_list, _ = self.matchTer()
            cal_exp_res = self.cal_item()
            ter_list, _ = self.matchTer()
            cal_exp_t_res = self.cal_exp_t()

            # return combine

            return

    def cal_exp_t(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer(
            )  #ter_list '+' or '-' or isempty true
            if isempty:
                return None
            else:
                plus_op = ter_list[0]
                self.cal_item()
                ter_list, _ = self.matchTer()
                self.cal_exp_t()
                self.expS.append(plus_op)
                return

    def cal_item_t(self):
        if self.productionInS():
            ter_list, isempty = self.matchTer(
            )  #ter_list '*' or '/' or isempty true
            if isempty:
                return None
            else:
                cal_factor_res = self.cal_factor()
                cal_item_t_res = self.cal_item_t()
                self.expS.append(ter_list[0])
                return

    def cal_item(self):
        if self.productionInS():
            ter_list, _ = self.matchTer()
            cal_factor_res = self.cal_factor()  # (?,arg1,?,?)
            ter_list, _ = self.matchTer()
            cal_item_t_res = self.cal_item_t()  # ()
            # return combine tow
            return

    def cal_factor(self):
        if self.productionInS():
            current_state = self.state.top().type
            if current_state == '-':
                # to do : generate negtive
                ter_list, _ = self.matchTer()
                cal_factor_res = self.cal_factor()
                # todo 负号运算
                print("todo 负号运算")
                exit()
            elif current_state == 'cal-quantity':
                cal_quantity_res = self.cal_quantity(
                )  #return a unfinished code
                # up res
                return

    def cal_quantity(self):
        if self.productionInS():
            ter_list, _ = self.matchTer()
            if self.state.top().type == 'cal-exp':
                self.cal_exp()
                ter_list, _ = self.matchTer()
                return
            else:
                #向上提交arg
                self.expS.append(ter_list[0])
                return

    def statement_list_t(self, zipper=None):
        if self.productionInS():
            _, isempty = self.matchTer()
            if isempty:  # match empty
                return
            else:
                self.statement_list(zipper)
                return

    def var_declear(self):
        if self.productionInS():
            _, isempty = self.matchTer()
            if isempty:  # match empty
                return
            else:
                self.var_define()
                return
        pass

    def var_define(self):
        if self.productionInS():
            _, isempty = self.matchTer()
            self.id_list()
            _, isempty = self.matchTer()
            self.typefunc()
            _, isempty = self.matchTer()
            self.var_define_t()

    def var_define_t(self):
        if self.productionInS():
            _, isempty = self.matchTer()
            if isempty:  # match empty
                return
            else:
                _, isempty = self.var_define()

    def typefunc(self):
        if self.productionInS():
            self.matchTer()

    def id_list(self):
        if self.productionInS():
            #此处定义变量
            self.var_list.append(self.todo.top())
            self.matchTer()
            self.id_list_t()

    def id_list_t(self):
        if self.productionInS():
            _, isempty = self.matchTer()
            if isempty:  # match empty
                return
            else:
                self.id_list()

    def program_start(self):
        """
        emit(program,sample,-,-)
        generate()

        """
        self.var_list.append(self.todo.get_program_ID())
        ter_list, _ = self.matchTer()
        self.emit_arg(ter_list[0], ter_list[1])

        return True

    def emit_code(self, code):
        self.newtemp += 1
        self.emit_list.append(code)

    def emit_arg(self,
                 op,
                 arg1=Sign('-', None),
                 arg2=Sign('-', None),
                 res=Sign('-', None)):
        self.newtemp += 1
        self.emit_list.append(code(op, arg1, arg2, res))

    def debugTest(self):
        # self.todo.debugT()
        self.todo.if_rop_follows()


if __name__ == "__main__":
    print("Description: \nAuthor: He Yuhang\nGithub: https://github.com/hyhhhhhhhh\nDate: 2020-11-24 12:02:12\nLastEditors: Box\nLastEditTime: 2020-12-13 18:54:01")
    print("class: 2018 jk_2")
    print("StudentID: 201830170110")
    name = input('请输入文件名：')

    fo2 = open(name, "r")
    # fo2 = open("TEST4.txt", 'r')
    string2 = ''
    for line in fo2.readlines():
        string2 += line

    test2 = getTokens(string2)
    if test2.scanner():
        test2.generate()
        # test2.printres()
    else:
        print('error')
        print(test2.error)

    print()
    readin = readin_tokens("tokens.txt")
    test = PredictingAnalysisTable()
    test.compile()
    g = generator(test.table, readin.Signs, sec_table=test.resolve_table)
    # g.debugTest()
    g.generate()
