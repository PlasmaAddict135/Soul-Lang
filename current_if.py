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
