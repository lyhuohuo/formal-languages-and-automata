import os
import re
import string
import sys
from itertools import product

class CNF2GNF(object):
    def __init__(self,grammar_file):
        self.grammar_file = grammar_file
        self.load_grammar(grammar_file)
    def load_grammar(self,grammar_file):#识别输入文法并进行预处理

        # Accepted Variables - Non Terminal Symbols - RegExp
        _V_set = '[A-Z](_[0-9]*)?(,[A-Z](_[0-9]*)?)*'
        
        _SIGMA_set = '.*(,.*)*'
        
        _S_set = '[A-Z](_[0-9]*)?'
        
        _P_set = '([A-Z](_[0-9]*)?->.*(|.*)*(,[A-Z](_[0-9]*)?->.*(|.*)*)*)'
        with open(grammar_file,'r') as f:
            lines = f.readlines()
        g = ''.join([re.sub(" |\n|\t", "", x) for x in lines])
        if not re.search('V:' + _V_set + 'SIGMA:' + _SIGMA_set + 'S:' + _S_set + 'P:' + _P_set, g):
            raise ImportError('please input right grammar!')
        v = re.search('V:(.*)SIGMA:', g).group(1)
        sigma = re.search('SIGMA:(.*)S:', g).group(1)
        s = re.search('S:(.*)P:', g).group(1)
        p = re.search('P:(.*)', g).group(1)

        
        self._V = [re.escape(x) for x in re.split(',', v.replace(" ", ""))]
        self._SIGMA = [re.escape(x) for x in re.split(',', sigma.replace(" ", ""))]
        # print(self._V)
        # print(self._SIGMA)
        if [x for x in self._V if x in self._SIGMA]:
            sys.exit('Error : V intersection SIGMA is not empty')
        s = re.escape(s.replace(" ", ""))
        
        if s in self._V:
            self._S = s
        else:
            sys.exit('Error : start symbol is not in V')
        p = p.replace(" ", "")
        self.vob = self._V + self._SIGMA
        p_lines = re.split(',', p)
        
        self._P = {}
        # print(p_lines)
        for line in p_lines:#处理产生式
            split = re.split('->', line)
            left = re.escape(split[0])
            if (left in self._V):
                    # v.append(left)
                    self._P[left] = []
                    rules = re.split('\|', split[1])
                    # print(rules)
                    for rule in rules:
                        # P[left].append(self._computeRule(rule))
                        self._P[left].append(self.split_sigma(rule))
                        # print('o')
            else:
                raise ImportError('Rigth simbol in production ' + line + ' is not in V')

        for v in self._V:
            if v not in self._P.keys():
                raise ImportError('simbol ' + v + ' has no right production')

        
        # print(self._P)
        
    def split_sigma(self,rule):
        split = {}
        tmp = rule
        i = 0
        # print(tmp)
        while len(tmp) > 0:
            r = re.search('|'.join(self.vob), tmp)
            # print('ok')
            if r.start() == 0:
                split[i] = re.escape(tmp[0:r.end()])
                tmp = tmp[r.end():]
                i += 1
            else:
                raise ImportError('Error : undefined symbol find in production : ' + tmp)
        #print(rules)
        return split
    def CNF(self):
        self.load_grammar(self.grammar_file)
        self.delete_empty()
        self.delete_unit()
        self.delete_useless()
        self.replace_teminal()
        self.precess_length()
        self.delete_useless()
    def GNF(self):
        self.rename_NotTerminal()
        self._orderProductions()
        
        self._terminateFirstSymbol()
        self.delete_useless()
        
        if self.accept_empty:
            self._P[self._S].append({0:re.escape('#')})
    

    def delete_empty(self):#消除空产生式
        # self.istoempty = False
        if re.escape('#') not in self._SIGMA:
            self.accept_empty = False
            return 

        self._SIGMA = [x for x  in self._SIGMA if x != re.escape('#')]
        self.is_empty = {}
        self.empty_set = self.find_empty()
        
        _P = {}

        for v in self._P:
            # if v not in _P.keys():
            #     _P[v] = []
            for p in self._P[v]:
                empty_num = 0
                for t in p.values():
                    if t in self.empty_set:
                        empty_num += 1
                if empty_num > 0:
                    cases = [[x for x in l] for l in list(product([True, False], repeat=empty_num))]
                    # if empty_num == len(p)
                    if empty_num == len(p):
                        cases = [x for x in cases if x != [False] * empty_num]
                    for case in cases:
                        k = 0  # production length
                        _i = 0  # number of s appeared
                        c = {}
                        for key, val in p.items():
                            if val not in self.empty_set:
                                c[k] = val
                                k += 1
                            elif case[_i]:
                                c[k] = val
                                k += 1
                                _i += 1
                            else:
                                _i += 1
                        if v not in _P.keys():
                            _P[v] = []
                        _P[v] = [x for x in [c] if x not in _P[v] and x != {}] + _P[v]

                else:
                    if v not in _P.keys():
                            _P[v] = []
                    if len(p) == 1 and p[0] == re.escape('#'):
                        continue
                    _P[v].append(p)
        # print(_P)
        if self._S in self.empty_set:
            self.accept_empty = True
        else:
            self.accept_empty = False
            # self._SIGMA.append(re.escape('#'))
            # _P[self._S].append({0:re.escape('#')})

        # print(_P)
        self._P = _P
        
    def find_empty(self):
        empty = []
        empty_new = self.update_empty(empty)
        while empty_new != empty:
            empty = empty_new
            empty_new = self.update_empty(empty) 
        return empty_new


    def update_empty(self,SET):
        W = [x for x in SET]
        for v in self._P:
            flag = False
            for p in self._P[v]:
                p_flag = True
                for ix,s in p.items():
                    if s not in SET and s != re.escape('#'):
                        p_flag = False
                        break
                if p_flag:
                    flag = True
                    break
            if flag:
                if v not in W:
                    W.append(v)

        return W

        
    
    def delete_unit(self):#消除单一产生式
        unit = {}

        for v in self._V:
            ans = []
            ans.append(v)
            ans_new = self.find_unit(ans)
            while ans_new != ans:
                ans = ans_new
                ans_new = self.find_unit(ans_new)
            unit[v] = ans_new

        for v in self._V:
            for _v in unit[v]:
                if _v != v:
                    for p in self._P[_v]:
                        if len(p )== 1 and p[0] in self._V:
                            continue
                        else:
                            if p not in self._P[v]:
                                self._P[v].append(p)

        for v in self._P:
            for p in self._P[v]:
                if len(p )== 1 and p[0] in self._V:
                    self._P[v].remove(p)


    def find_unit(self,T):
        ans = T[:]
        for v in T:
            for p in self._P[v]:
                if len(p) == 1 and p[0] in self._V:
                    if p[0] not in ans:
                        ans.append(p[0])
        return ans
    def delete_useless(self):#消除无用符号
        # 计算有用符号
        W = []
        W_new = self._updateW(W)
        while W_new != W:
            W = W_new
            W_new = self._updateW(W) 
        V = W_new
        _P = {}
        for v in V:
            _P[v] = []
            for _p in self._P[v]:
                if [True for x in range(len(_p))] == [x in V + self._SIGMA for n, x in _p.items()]:
                    _P[v].append(_p)
        #计算可达符号
        Y = {}
        Y[0] = [self._S]
        j = 1
        Y[1] = self._propagateProduction(Y[0])
        while (Y[j] != Y[j - 1]):
            j += 1
            Y[j] = self._propagateProduction(Y[j - 1], Y[j - 2])
        self._V = [x for x in V if x in Y[j]]
        self._SIGMA = [x for x in self._SIGMA if x in Y[j]]
        P_last = {}
        for v in self._V:
            P_last[v] = []
            for _p in _P[v]:
                if [True for x in range(len(_p))] == [x in self._V + self._SIGMA for n, x in _p.items()]:
                    P_last[v].append(_p)
        self._P = P_last
    def _propagateProduction(self, Y, _prev=None):
        _y = [x for x in Y]
        y = [x for x in Y if x not in self._SIGMA]
        if _prev is not None:
            y = [x for x in y if x not in _prev]
        for v in y:
            for p in self._P[v]:
                for n, s in p.items():
                    if s not in Y:
                        _y.append(s)
        return _y

    def _updateW(self, SET):
        W = [x for x in SET]
        for v in self._P:
            flag = False
            for p in self._P[v]:
                flag_ = True
                for n, _v in p.items():
                    if _v not in SET and _v not in self._SIGMA:
                        flag_ = False
                        break
                if flag_:
                    flag = True
                    break
            if flag and v not in W:
                W.append(v)

        return W



    def replace_teminal(self):
        _P = {}
        _wrongPs = {}
        for v, Ps in self._P.items():
            _P[v] = []
            for p in Ps:
                if len(p) > 1 and len([x for x in p.values() if x in self._SIGMA]) > 0:
                    if v not in _wrongPs.keys():
                        _wrongPs[v] = []
                    _wrongPs[v].append(p)
                else:
                    _P[v].append(p)
        conv = {}
        for v, Ps in _wrongPs.items():
            for p in Ps:
                for s in list(set([y for y in [x for x in p.values() if x in self._SIGMA] if y not in conv.keys()])):
                    # print(v)
                    _v = self._createVariable(v[0])
                    self._V.append(_v)
                    conv[s] = _v
                    _P[_v] = [{0: s}]
                _p = {}
                for j, s in p.items():
                    if s in self._SIGMA:
                        _p[j] = conv[s]
                    else:
                        _p[j] = s
                _P[v].append(_p)
        self._P = _P
    
    def _createVariable(self, S):
        i = 0
        while (S + '\\_' + str(i) in self._V):
            i += 1
        return S + '\\_' + str(i)

    def _createConvVariable(self):
        i = 0
        while ('A\\_' + str(i) in self._conv.values()):
            i += 1
        return 'A\\_' + str(i)
    def precess_length(self):#代换长产生式
        _P = {}
        _wrongPs = {}
        for v, Ps in self._P.items():
            _P[v] = []
            for p in Ps:
                if len(p) > 2 and len([x for x in p.values() if x in self._V]) > 0:
                    if v not in _wrongPs.keys():
                        _wrongPs[v] = []
                    _wrongPs[v].append(p)
                else:
                    _P[v].append(p)
        for v, Ps in _wrongPs.items():
            #if v not in _P.keys():
               # _P[_v[j]] = []
            for p in Ps:
                n = len(p)
                _v = {0: v}
                for j in range(1, n):
                    if j != n - 1:
                        _v[j] = self._createVariable('X')
                        self._V.append(_v[j])
                    else:
                        _v[j] = p[j]
                    if _v[j] not in _P.keys():
                        _P[_v[j]] = []
                    _P[_v[j - 1]].append({0: p[j - 1], 1: _v[j]})
        self._P = _P

    def rename_NotTerminal(self):#代换非终结符
        self._conv = {}
        self._conv[self._S] = 'A\\_0'
        _P = {'A\\_0': []}
        _S = 'A\\_0'
        _P[_S] = self._renameCFGProductions(self._S)
        for v in [x for x in self._V if x != self._S]:
            if v not in self._conv.keys():
                self._conv[v] = self._createConvVariable()
            _P[self._conv[v]] = self._renameCFGProductions(v)
        self._V = list(_P.keys())
        # print(self._V[0][2:])
        self._S = _S
        self._P = _P

    def _renameCFGProductions(self, v):#为非终结符排序
        _Ps = []
        for el in self._P[v]:
            _p = {}
            for i, s in el.items():
                if s in self._SIGMA:
                    _p[i] = s
                elif s in self._conv.keys():
                    _p[i] = self._conv[s]
                else:
                    _v = self._createConvVariable()
                    self._conv[s] = _v
                    _p[i] = _v
            _Ps.append(_p)
        return _Ps

                        
                                
    def replace_notdirect_recurse(self):#消除间接左递归
        # print(self.__str__())
        _P = {}
        V = sorted(self._V, key=lambda n: int(n[3:]))
        for i in range(len(V)):
            vi = V[i]
            # print(vi)
            if vi not in _P.keys():
                _P[vi] = []
            for pi in self._P[vi]:
                        _P[vi].append(pi)

            
            for j in range(i):
                vj = V[j]
                # cun = []
                for pi in _P[vi]:
                    if pi[0] == vj:
                        
                        # print(vj)
                        for pj in _P[vj] :
                            c = {}
                            for ix,s in pj.items():
                                # if s == re.escape('#'):
                                #     continue
                                c[ix] = s

                            length = len(c)
                            for t in range(len(pi)-1):
                                c[length+t] = pi[t+1]
                            if c not in _P[vi]:
                                _P[vi].append(c)
                        _P[vi].remove(pi)
 

            
            if self.check(vi,_P[vi]):
                # print('True')
                _newPs = self._removeLeftRecursion(vi,_P)
                # print(_newPs)
                for _v, s in _newPs.items():
                    if _v not in _P.keys():
                        _P[_v] = []
                        self._V = [x for x in [_v] if x not in self._V] + self._V
                        _P[_v] = [x for x in s if x not in _P[_v]] + _P[_v]
                    if _v == vi:
                    # _P[_v] = [x for x in s if x not in _P[_v]] + _P[_v]
                        _P[vi] =s
        self._P = _P     
                                     
    def check(self,v,P):
        for p in P:
            if  p[0] == v:
                return True

        return False     
    
        
    def _orderProductions(self):
        self.replace_notdirect_recurse()
        # print('replace')
        # print(self.__str__())
       
        
        _P = {}
        for v in sorted(self._V, key=lambda n: int(n[3:])):
            if v not in _P.keys():
                _P[v] = []
            for p in self._P[v]:
                if p[0] in self._V:
                    if int(p[0][3:]) < int(v[3:]):
                        _newPs = self._replaceProduction(v, p, self._P)
                        _P[v] = [x for x in _newPs if x not in _P[v]] + _P[v]
                    else:
                        _P[v] = [x for x in [p] if x not in _P[v]] + _P[v]
                else:
                    _P[v] = [x for x in [p] if x not in _P[v]] + _P[v]
        self._P = _P
      
    def _replaceProduction(self, v, p, Ps):
        _Ps = []
        for _ps in Ps[p[0]]:
            _p = {}
            for k, el in _ps.items():
                _p[k] = el
            i = len(_p) - 1
            for j in range(1, len(p)):
                _p[i + j] = p[j]
            if _p[0] in self._V:
                if int(_p[0][3:]) < int(v[3:]):
                    _newPs = self._replaceProduction(v, _p, Ps)
                    _Ps = [x for x in _newPs if x not in _Ps] + _Ps
                else:
                    _Ps = [x for x in [_p] if x not in _Ps] + _Ps
            else:
                _Ps = [x for x in [_p] if x not in _Ps] + _Ps
        return _Ps

    

    def _removeLeftRecursion(self, v,  _P):#消除直接左递归
        _T = []
        _M = []
        _v = self._createVariable('A')
        for s in _P[v]:
            if s[0] != v:
                _T.append(s)
            else:
                _M.append(s)
        _Ps = {v: [], _v: []}
        for t in _T:
            _Ps[v].append(t)
            p0 = {}
            for i, el in t.items():
                p0[i] = el
            p0[len(p0)] = _v
            _Ps[v] = [x for x in [p0] if x not in _Ps[v]] + _Ps[v]
        for m in _M:
            p1 = {}
            p2 = {}
            for i, s in m.items():
                if i != 0:
                    p1[i - 1] = s
                    p2[i - 1] = s
            p2[len(p2)] = _v
            _Ps[_v] = [x for x in [p1, p2] if x not in _Ps[_v]] + _Ps[_v]
        return _Ps
    def _terminateFirstSymbol(self):#转化为终结符打头
        _P = {}
        for v in sorted(self._V, key=lambda n: int(n[3:]), reverse=True):
            _P[v] = []
            for p in self._P[v]:
                if p[0] in self._V:
                    newPs = self._terminateProduction(p)
                    _P[v] = [x for x in newPs if x not in _P[v]] + _P[v]
                else:
                    _P[v].append(p)
        self._P = _P

    def _terminateProduction(self, p):
        _Ps = []
        for _p in self._P[p[0]]:
            if _p[0] in self._V:
                T = self._terminateProduction(_p)
            else:
                T = [_p]
            for t in T:
                new = {}
                for i in range(len(t)):
                    new[i] = t[i]
                i = len(new) - 1
                for j in range(1, len(p)):
                    new[i + j] = p[j]
                _Ps.append(new)
        return _Ps

    def _renameBackCFG(self):
        _cB = {}
        for old, new in self._conv.items():
            _cB[new] = old
        self._S = _cB[self._S]
        self._V = list(_cB.values()) + [x for x in self._V if x not in list(_cB.keys())]
        _P = {}
        for v, Ps in self._P.items():
            if v in _cB.keys():
                _v = _cB[v]
            else:
                _v = v
            _P[_v] = []
            for p in Ps:
                _p = {}
                for i, s in p.items():
                    if s in _cB.keys():
                        _p[i] = _cB[s]
                    else:
                        _p[i] = s
                _P[_v].append(_p)
        self._P = _P

    def __str__(self, order=False):
        _str = 'V: ' + ', '.join(self._V) + '\n'
        _str += 'SIGMA: ' + ', '.join(self._SIGMA) + '\n'
        _str += 'S: ' + self._S + '\n'
        _str += 'P:'
        if order:
            V = [x for x in order if x in self._V] + [x for x in self._V if x not in order]
        else:
            V = self._V

        # print(self._V)
        for v in self._P:
            _str += '\n\t' + v + ' ->'
            _PS = []
            for p in self._P[v]:
                _p = ''
                for i, s in p.items():
                    _p += ' ' + s
                _PS.append(_p)
            _str += ' |'.join(_PS)
        return _str.replace('\\', '')

    def PDA(self, candidate):#下推自动机
        stack = []
        self.bottom = 'dos'
        stack.append(self.bottom)
        stack.append(self._S)
        stri = candidate
        # print(candidate)
        self.flag = False
        self.analysis(stri,stack)
        if not self.flag:
            print('Not accept')
            sys.exit()

    

    def analysis(self,stri,stack):#识别函数
        if stack[-1] == self.bottom :
            if stri == '':
                self.flag = True
                print('accept!')
                sys.exit() 
            else:
                return
        if stack[-1] != self.bottom and stri == '':
            return
        v = stack[-1]
        for ps in self._P[v]:
            
            # p_stack = stack[:]
            if ps[0] == re.escape(stri[0]):
                stack.pop()
                # print('success')
                for i in range(0,len(ps)-1):
                    
                    stack.append(ps[len(ps)-1-i])
                self.analysis(stri[1:],stack)
                for i in range(0,len(ps)-1):
                    stack.pop()
                stack.append(v)
                




    
if __name__ == '__main__':
    file = 'grammar.txt'
    cf2gf = CNF2GNF(file)
    print('input grammar')
    print(cf2gf)
    print('-------------')
    # print(cf2gf._P[cf2gf._S])
    print('cnf')
    cf2gf.CNF()
    print(cf2gf)
    print('-------------')
    print('gnf')
    cf2gf.GNF()
    print(cf2gf)
    print('-------------')
    

    candidate = input('input candidate string to recognize:')
    cf2gf.PDA(candidate)

