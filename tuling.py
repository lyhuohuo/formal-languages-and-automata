def cal(x,y):
    
    line = []
    
    for i in range(y):
       line.append('1')
    line.append('0')
    
    for i in range(x):
        line.append('1')

    line.append('0')
    line.append('1')
    line.append('0')

    now = 0
    
    state = 0
    while state !=21:#状态21为终态
        # print(state)
        if state == 0:
            if line[now] == '0':
                state = 17
                now -= 1
            elif line[now] == '1':
                
                state = 1
                line[now] = 'a'
                now = now + 1
            # else:
            #     state = 21
        elif state == 1:
            if line[now] == '0':
                state = 2
                now = now + 1
            elif line[now] == '1':
                now = now + 1
            # else:
            #     state = 17
        elif state == 2:
            if line[now] == '0':
                state = 18
                now = now + 1
            elif line[now] == '1':
                state = 3
                line[now] = 'b'
                now = now + 1
            # else:
            #     state = 17
        elif state == 3:
            if line[now] == '0':
                state = 4
                now = now + 1
            elif line[now] == '1':
                now = now + 1
            # else:
            #     state = 17
        elif state == 4:
            if line[now] == '0':
                state = 9
                now = now - 1
            elif line[now] == '1':
                state = 5
                line[now] = 'c'
                now = now + 1
            # else:
            #     state = 17
        elif state == 5:
            if line[now] == '0':
                state = 6
                now = now + 1
            elif line[now] == '1':
                now = now + 1
            # else:
            #     state = 17
        elif state == 6:
            if now >= len(line) or now < 0:
                line.append('1')
                state = 7
                now = now + 1
            elif line[now] == '0':
                state = 7
                line[now] = '1'
                now = now + 1
            elif line[now] == '1':
                now = now + 1
            # else:
            #     state = 17
        elif state == 7:
            if now >= len(line) or now < 0:
                line.append('0')
                state = 8
                now = now -1
            else:
                state = 17
        elif state == 8:
            if line[now] == '0' or line[now] == '1':
              
                now = now - 1
            elif line[now] == 'c':
                state = 4
                now = now + 1
            # else:
            #     state = 17
        elif state == 9:
            if line[now] == '0' or line[now] == '1':
              
                now = now - 1
            elif line[now] == 'c':
                line[now] = '1'
                now = now - 1
            elif line[now] == 'b':
                state = 20
                now = now + 1
            # else:
            #     state = 17
        elif state == 10:
            if line[now] == '0':
                state = 11
                now = now + 1
            elif line[now] == 'b':
                line[now] = '1'
                now = now - 1
            # else:
            #     state = 17
        elif state == 11:
            if line[now] == '0':
                state = 12
                now = now + 1
            elif line[now] == '1':
                now = now + 1
            # else:
            #     state = 17
        elif state == 12:
            if line[now] == '0':
                state = 13
                line[now] = '1'
                now = now + 1
            elif line[now] == '1':
                line[now] = 'd'
                now = now + 1
            # else:
            #     state = 17
        elif state == 13:
            if line[now] == '0':
                state = 14
                now = now - 1
                line.pop()
            elif line[now] == '1':
                now = now + 1
            # else:
            #     state = 17
        elif state == 14:
            if line[now] == '1':
                state = 15
                line[now] = '0'
                now = now - 1
            # else:
            #     state = 17
        elif state == 15:
            if line[now] == '0':
                state = 16
                now = now - 1
            elif line[now] == '1':
                now = now - 1
            elif line[now] == 'd':
                state = 13
                line[now] = '1'
                now = now + 1
            # else:
            #     state = 17
        elif state == 16:
            if line[now] == '0' or line[now] == '1':
          
                now = now - 1
            elif line[now] == 'a':
                state = 0
                now = now + 1
            # else:
            #     state = 17
        elif state == 17:
            
            if line[now] == 'a':
                line[now] = '1'
                now = now -1
            elif now < 0:
                state = 21
                now = now + 1
        elif state == 18:
            if now >= len(line):
                
                state = 19
                now = now - 1
            else:
                now = now + 1
        elif state == 19:
            # print('now = ' ,now)
            if line[now] == '1':
                
                # print(line)
                line[now] = '0'
                state = 22
                # print(line)
                now = now - 1
                # state = 17

        elif state == 20:
            if line[now] == '0':
                state = 10
                now = now - 1
            elif line[now] == '1':
                line[now] = 'b'
                state = 3
                now = now +1
        elif state == 22:
            if now < 0:
                state = 21
                now = now + 1
            elif line[now] == 'a':
                line[now] = '1'
                now = now - 1
            else:
                now = now - 1
        # print('now = '+ now)
        # print(line)
    # print(line)
    # print('now = ',now)
    res = 0
    pos = len(line)-2
    # print(line)
    while line[pos] != '0':
        res += 1
        pos = pos-1

    print('res = ',res)
        


if __name__ == '__main__':
    x,y = map(int,input('请输入x和y 计算x的y次幂').split())
    # print(x,y)
    cal(x,y)