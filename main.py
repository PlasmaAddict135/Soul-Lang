import os, re, time
from TARRP import *
start = time.time()
print('SIO VERSION 0.9.8')
print("Type 'CLOG' or 'HELP' for more information.")

def IDE(inpt):
    current_index = 0
    do_print = False

    def submit_button():
        nonlocal current_index
        dictionary_of_functions = {
         'print': printFunc,
         'int':intFunc,
         'func':ufuncFunc,
         'if':ifFunc,
         'fib':FibonacciFunc,
         'input':inputFunc,
         'var[str]':varFunc,
         'open':filesFunc,
         'set': setFunc,
         'sys':filesFunc
        }
        for ind, s in enumerate(inpt):
            current_index = ind
            if s in dictionary_of_functions:
                dictionary_of_functions[s]()

        current_index = 0

    def printFunc():
        try:
            nonlocal current_index
            if inpt[current_index] == 'print':
                if 'func' != inpt[(current_index < 3)]:
                    inpt[current_index] = '<'
                    if inpt[current_index] == '<':
                        print(' '.join(inpt[current_index + 2:inpt.index('>', current_index)]))
                    current_index += 1
        except:
            print('ERROR 112: Invalid syntax; check spelling')
        
    def varprintFunc():
        if 'print/var' or 'print/set' == inpt[(current_index)]:
            print('e')
            print(inpt[(current_index + 1)])
            print(inpt[inpt.index('var')+1])
            if inpt[inpt.index('var')+1] == inpt[(current_index)]:
                print(inpt[inpt.index('var')+1])
    # var a = hello! print/var a ;
    def lformFunc():
        if inpt[current_index] == 'print^':
            index = inpt.index('->') + 1
            n = int(inpt[index])
            print(*inpt[index + 1:index + 1 + n])
        if inpt[(current_index + 1)] == 'print':
            print('^')
            print('ERROR 113: Syntax error; check spelling')

    def intFunc():
        if 'int' in inpt:
            if '+' in inpt:
                ints = inpt.index('int')
                inpt[ints + 1] = float(inpt[(ints + 1)])
                inpt[ints + 3] = float(inpt[(ints + 3)])
                print(inpt[(ints + 1)] + inpt[(ints + 3)])
            if '-' in inpt:
                ints = inpt.index('int')
                inpt[ints + 1] = float(inpt[(ints + 1)])
                inpt[ints + 3] = float(inpt[(ints + 3)])
                print(inpt[(ints + 1)] - inpt[(ints + 3)])
            if '/' in inpt:
                ints = inpt.index('int')
                inpt[ints + 1] = float(inpt[(ints + 1)])
                inpt[ints + 3] = float(inpt[(ints + 3)])
                print(inpt[(ints + 1)] / inpt[(ints + 3)])
            if '*' in inpt:
                ints = inpt.index('int')
                inpt[ints + 1] = float(inpt[(ints + 1)])
                inpt[ints + 3] = float(inpt[(ints + 3)])
                print(inpt[(ints + 1)] * inpt[(ints + 3)])

    def setFunc():
        if 'set:' == inpt[current_index]:
            inpt[current_index + 1] = int(inpt[current_index + 1])
            if 'goto' != inpt[current_index + 1]:
                if ':' == inpt[current_index + 2]:
                    inpt[inpt[current_index + 1]] = inpt[current_index + 3]
            if 'goto' == inpt[current_index + 1]:
                if ':' in inpt[current_index + 3]:
                    inpt[inpt.index(inpt[current_index + 2], current_index)] = inpt[current_index + 4]
#############################
#BROKEN
#############################
    if 'ssl(' == inpt[current_index]:
        print(inpt[current_index + 1])
        if inpt.count(inpt[(current_index + 1)]) > 1:
            inpt = inpt[inpt.count(inpt[(current_index + 1)]):]
            print(inpt)
            submit_button()
    if 'ssl(' == inpt[current_index + 4]:
        if '(' in inpt[current_index]:
            if '' == inpt[current_index + 1]:
                pass

#(  + 1 ssl( print < e > ))

###########################
#BROKEN
###########################

    def listFunc():
        if 'list:' == inpt[current_index]:
            global clist
            try:
                inpt[current_index + 1] = []
                clist = inpt[current_index + 1]
                clist.append(' '.join(inpt[inpt.index('[', current_index) + 1:inpt.index(']', current_index)]))
                print(clist)
            except:
                print('')
        
# ssl( e print < hello > ; )endssl e ;
    def ifFunc():
        if 'func' != inpt[(current_index < 3)]:
            end = inpt.index('}', current_index)
            if 'if' == inpt[current_index] and 'in' == inpt[(current_index + 2)] and '*' or 'all' == inpt[(current_index + 3)] and '{' == inpt[(current_index + 4)]:
                if inpt.count(inpt[(current_index + 1)]) > 1:
                    if inpt[(current_index + 5)] <= 'print':
                        inpt[current_index] = 'print'
                        if inpt[(current_index + 1)] == '<':
                            if end == end:
                                print(' '.join(inpt[inpt.index('<', current_index) + 1:inpt.index('>', current_index)]))
                    if 'ints' == inpt[(current_index + 3)] or inpt[(current_index + 5)] == '+':
                        print(int(inpt[(current_index + 4)]) + int(inpt[(crrent_index + 6)]))
                else:
                    inpt[current_index] = 'null'
                    inpt[current_index + 7] = 'null'
                    return False
            if inpt[current_index] == 'if':
                loc_targ = inpt[(current_index + 1)]
                end = inpt.index('>', current_index + 1)
                if inpt[(current_index + 2)] == 'goto' and inpt[(current_index + 3)] == '->':
                        inpt[current_index + 4] = int(inpt[(current_index + 4)])
                        loc_ = inpt[(current_index + 4)]
                        loc_res = inpt[(current_index + 6 + loc_)]
                        if '{' == inpt[(current_index + 5)] and loc_targ == loc_res:
                            final_peram = inpt[(current_index + 7)]
                            if inpt[(current_index + 6)] < 'print':
                                inpt[current_index] = 'print'
                                if inpt[(current_index + 1)] == '<' and end == end:
                                        print(' '.join(inpt[inpt.index('<', current_index) + 1:inpt.index('>', current_index)]))
                            if inpt[(current_index + 6)] == 'ints':
                                inpt[current_index + 7] = int(inpt[(current_index + 7)])
                                inpt[current_index + 8] = int(inpt[(current_index + 8)])
                                print(inpt[(current_index + 8)] + inpt[(current_index + 7)])
                        else:
                            inpt[current_index] = 'null'
                            inpt[current_index + 7] = 'null'
                if inpt[(current_index + 3)] == '<-':
                    inpt[current_index + 4] = int(inpt[(current_index + 4)])
                    loc_ = inpt[(current_index + 4)]
                    loc_res = inpt[(current_index + 6 - loc_)]
                    if '{' == inpt[(current_index + 5)] and loc_targ == loc_res:
                        final_peram = inpt[(current_index + 7)]
                        if inpt[(current_index + 7)] == 'print':
                            if inpt[(current_index + 8)] == '<' and end == end:
                                print(' '.join(inpt[current_index + 9:inpt.index('>', current_index)]))
                        if inpt[(current_index + 6)] == 'ints':
                            inpt[current_index + 7] = int(inpt[(current_index + 7)])
                            inpt[current_index + 8] = int(inpt[(current_index + 8)])
                            print(inpt[(current_index + 8)] + inpt[(current_index + 7)])
                    else:
                        inpt[current_index] = 'null'
                        inpt[current_index + 7] = 'null'
            if 'if' == inpt[current_index]:
                try:
                    if '@' == inpt[(current_index + 2)]:
                        i = inpt[(current_index + 2)]
                        inpt[i + 1] = int(inpt[(i + 1)])
                        if inpt[(inpt[(i + 1)] - 1)] == inpt[(current_index + 1)]:
                            print(inpt[(i + 2)])
                except:
                    print('no')

                if '[]' > inpt[inpt.index('if')]:
                    print('ERROR 232: Illegal character usage')
# if test goto -> 6 { hello print < e > } test ;
#################################################
#WORKS BUT HAS TO BE UPDATED TO RECENT INDEXING
#################################################
    def filesFunc():
        if 'sys[open]' in inpt:
            os.startfile(inpt[(inpt.index('sys[open]') + 1)] + '.txt')
        if 'sys[w]' in inpt:
            writef = open(inpt[(inpt.index('sys[w]') + 1)] + '.txt', 'w')
            writef.write(inpt[(inpt.index('sys[w]') + 2)])
            writef.close()
        if 'sys[r]' in inpt:
            readf = open(inpt[(inpt.index('sys[r]') + 1)] + '.txt', 'r')
            print(readf.read())
        else:
            print('ERROR 341: Invalid syntax or SYSTEM perameter; check spelling')

###############
#JUST WHY
###############
    def varFunc():
        if 'var[str]' in inpt:
            if inpt.count(inpt[(inpt.index('var[str]') + 1)]) > 1:
                print(inpt[(current_index + 2)])
        else:
            print('ERROR 251: Invalid syntax or VAR perameter; check spelling')

    #VARIABLE HANDLING
    if inpt[current_index] == 'var':
        if inpt[current_index + 2] == '=':
            inpt[inpt.index('var', current_index) + 1] = inpt[inpt.index('var', current_index) + 3]
############################################
#STILL TRYING TO GET RIGHT
############################################
    def inputFunc():
        nonlocal current_index
        if 'input=' == inpt[current_index]:
            inpt[current_index + 1] = input(inpt[(current_index + 2)])
            current_index += 1
        else:
            print('ERROR 461: Invalid syntax; check spelling')

#######################################
#NEEDS OPTIMIZATION
#######################################
    def ufuncFunc():
        nonlocal current_index

        def subIf_Func():
            end = inpt.index('}', current_index)
            if 'if' == inpt[current_index]:
                if 'in' == inpt[(current_index + 2)]:
                    if '*' or 'all' == inpt[(current_index + 3)]:
                        if '{' == inpt[(current_index + 4)]:
                            if inpt.count(inpt[(current_index + 1)]) > 1:
                                if inpt.count(inpt[(current_index + 1)]) > 1:
                                    if inpt[(current_index + 5)] <= 'print':
                                        inpt[current_index] = 'print'
                                        if inpt[(current_index + 1)] == '<':
                                            if end == end:
                                                print(' '.join(inpt[inpt.index('<', current_index) + 1:inpt.index('>', current_index)]))
                                    if not 'ints' == inpt[(current_index + 3)] or inpt[(current_index + 5)] == '+':
                                        print(int(inpt[(current_index + 4)]) + int(inpt[(crrent_index + 6)]))
                                else:
                                    inpt[current_index] = 'null'
                                    inpt[current_index + 7] = 'null'
                                    return False
            if inpt[current_index] == 'if':
                loc_targ = inpt[(current_index + 1)]
                end = inpt.index('>', current_index + 1)
                if inpt[(current_index + 2)] == 'goto':
                    if inpt[(current_index + 3)] == '->':
                        inpt[current_index + 4] = int(inpt[(current_index + 4)])
                        loc_ = inpt[(current_index + 4)]
                        loc_res = inpt[(current_index + 6 + loc_)]
                        if '{' == inpt[(current_index + 5)]:
                            if loc_targ == loc_res:
                                final_peram = inpt[(current_index + 7)]
                                if inpt[(current_index + 6)] < 'print':
                                    inpt[current_index] = 'print'
                                    if inpt[(current_index + 1)] == '<':
                                        if end == end:
                                            print(' '.join(inpt[inpt.index('<', current_index) + 1:inpt.index('>', current_index)]))
                                if inpt[(current_index + 6)] == 'ints':
                                    inpt[current_index + 7] = int(inpt[(current_index + 7)])
                                    inpt[current_index + 8] = int(inpt[(current_index + 8)])
                                    print(inpt[(current_index + 8)] + inpt[(current_index + 7)])
                            else:
                                inpt[current_index] = 'null'
                                inpt[current_index + 7] = 'null'
                    if inpt[(current_index + 3)] == '<-':
                        inpt[current_index + 4] = int(inpt[(current_index + 4)])
                        loc_ = inpt[(current_index + 4)]
                        loc_res = inpt[(current_index + 6 - loc_)]
                        if '{' == inpt[(current_index + 5)]:
                            if loc_targ == loc_res:
                                final_peram = inpt[(current_index + 7)]
                                if inpt[(current_index + 7)] == 'print':
                                    if inpt[(current_index + 8)] == '<':
                                        if end == end:
                                            print(' '.join(inpt[current_index + 9:inpt.index('>', current_index)]))
                                if inpt[(current_index + 6)] == 'ints':
                                    inpt[current_index + 7] = int(inpt[(current_index + 7)])
                                    inpt[current_index + 8] = int(inpt[(current_index + 8)])
                                    print(inpt[(current_index + 8)] + inpt[(current_index + 7)])
                            else:
                                inpt[current_index] = 'null'
                                inpt[current_index + 7] = 'null'

        if 'func' == inpt[current_index]:
            ending = inpt.index(')', current_index)
            if inpt[(current_index + 2)] == '(':
                if inpt.count(inpt[(current_index + 1)]) > 1:
                    if ')' > inpt[(current_index + 2)]:
                        if 'print' > inpt[(current_index + 2)]:
                            try:
                                if inpt[current_index] == 'print':
                                    if 'func' != inpt[(current_index < 3)]:
                                        inpt[current_index] = '<'
                                        if inpt[current_index] == '<':
                                            print(' '.join(inpt[current_index + 2:inpt.index('>', current_index)]))
                                        current_index += 1
                            except:
                                print('ERROR 112: Invalid syntax; check spelling')

                            if 'if' > inpt[(current_index + 2)]:
                                inpt[current_index] = 'if'
                                if ending == ending:
                                    subIf_Func()
        #func foo ( if test goto -> 6 { hello print < e > } test ) foo ;

    def FibonacciFunc():

        def fib(num):
            if num < 0:
                print('ERROR 581: Invalid number')
            else:
                if num == 1:
                    return 0
                if num == 2:
                    return 1
                return fib(num - 1) + fib(num - 2)

        if inpt[current_index] == 'fib':
            inpt[current_index + 1] = int(inpt[(current_index + 1)])
            num = inpt[(current_index + 1)]
            print(fib(num))

###########################################
#IMPORTS WORK BUT ONLY FOR A TEST
###########################################
    if inpt[current_index] == 'import':
        impf = open('C:\\Users\\admin\\AppData\\Local\\Programs\\SIO\\Scripts\\' + inpt[(current_index + 1)] + '.sio', 'r')
        imported = impf.read().split(' ')
        impf.close()
        inpt = inpt + imported
        inpt.remove(inpt[inpt.index('import', current_index)])
        submit_button()
    if ';' in inpt[(-1)]:
        submit_button()
    if ';' not in inpt[(-1)]:
        if 'load' not in inpt[(-1)]:
            print("ERROR 000: No ';' in ENDING PARAMETER \nLAST ITEM: '" + inpt[current_index] + "'")
    if 'p;' in inpt[(-1)]:
        printFunc()

#######################
#LOADING FILES
#######################
    if 'load' in inpt[(-1)]:
        try:
            load_ = input('LOAD: ')
            f2 = open(load_, 'r')
            back = f2.read()
            f2.close()
            TARRP_F(load_)
            f = open(load_, 'r')
            inpt = f.read().split(' ')
            f.close()
            if ';' in inpt[(-1)]:
                submit_button()
            if ';' not in inpt[(-1)]:
                print("ERROR 000: No ';' in ENDING PARAMETER \nLAST ITEM: '" + inpt[(-1)] + "'")
            fb = open(load_, 'w')
            fb.write(back)
            fb.close()
        except:
            print('          ^')
            print('ERROR 584: Invalid TARRP loading parameter')

        if 'l;' in inpt[(-1)]:
            print(len(inpt))
            submit_button()
        if 'rep;' in inpt[(-1)]:
            submit_button()
            submit_button()
        if 'save;' in inpt[(-1)]:
            print('Notice: This will overwrite any other file with this name')
            saveas = input('Save as: ')
            f = open(saveas + '.sio', 'a')
            f.write(' '.join(inpt))
            f.close()
            print('Save sucessful, check folder that SIO is installed in.')
            submit_button()
        if 'clock' in inpt:
            print(f"Runtime of the program is {endtime - start}")
        if 'SIO -R' in inpt:
            exit()
        if 'SIO -V' in inpt:
            print('SIO version: 0.9.8')

##############################
#CHANGE LOG
##############################
        if 'CLOG' in inpt:
            print('NOTICE: LATEST TO EARLIEST (EXCLUDING MINOR CHANGES SUCH AS LITTLE BUGS')
            print("> Changed 'locate' to 'goto' for clarity")
            print("> Finally impleminted functions; made them capable of handling 'if' statements and printing things")
            print("> Made it so that you could re-use 'print' function inside 'if'")
            print('> Added Fibonacci function to increase preformance')
            print("> Changed the ending parameter from '()' to ';' for ease")
            print("> Changed 'if' statement indentation syntax to start '{' and '}' to end")
            print("> Changed the way the 'print' function works")
            print("> Changed syntax, no more '.' seperator")
            print('> Implemented a parser!')
            print('> Fixed print function bug')
            print("> Changed 'p' to 'print', and 'a' to a broader 'int'")
            print("> Added 'if[in,*]' function along with 'locate', 'p' perameter, and 'a' perameter")
            print("> Fixed '@' in if function")
            print("> Fixed 'long form printing function' errors")
            print("> Made 'print' function more efficient")
            print("> Added 'int' function for handeling #'s")
            print("> Changed 'add' function to ints")
            print("> Opening 'SIO' files supported")
            print("> Imported 'TARRP'")
            print("> Made 'TARRP'")
            print("> Renamed 'u[input]' to 'input'")
            print('> Added string variables')
            print('> Changed function syntax')
            print("> Changed 'files' syntax")
            print("> Created 'file opening' function")
            print("> Created 'writing' and 'reading' functions")
            print('> Made it so the terminal is cutomizable via SIO COMMAND')
            print("> Made 'Version/Restart' functions")
            print('> Changed function storage to dictionary instead of function')
            print("> Added more 'Ending Parameters'")
            print("> Updated 'inpt' input")
            print('> Enclosed everything in function')
            print("> Made 'add' function")
            print("> Created 'print' function")
            print('> Made program')
        if 'IDE -C' in inpt:
            customize = input('Customize IDE >>> ')
            if 'fgc=lb' in customize:
                os.system('color 1')
            if 'fgc=blue' in customize:
                os.system('color 9')
            if 'theme=powershell' in customize:
                os.system('color 1f')
            if 'theme=deapsea' in customize:
                os.system('color 0a')
            if 'theme=deapsea2' in customize:
                os.system('color 02')
            if 'hcm' in customize:
                os.system('color f0')


endtime = time.time()
while True:
    str1 = ' '
    inpt = input('>>> ').split(' ')
    IDE(inpt)

IDE(inpt)
