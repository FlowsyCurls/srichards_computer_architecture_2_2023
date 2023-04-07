# MOESI simple finite state machine

def moesifsm(blockstate, blockaddr, cpumsg, busaddr, busmsg):
    if cpumsg == 'CALC':
        return
    else:
        addrcond = blockaddr == busaddr
        # print(addrcond)
        if blockstate == 'I':
            if cpumsg == 'WRITE':
                return ['writemiss','M']
            elif cpumsg == 'READ':
                return ['readmiss','E']
            elif addrcond and (busmsg == 'writemiss' or busmsg == 'readmiss'):
                return ['neutral','I']
            else:
                return ['neutral','I']
        elif blockstate == 'S':
            if cpumsg == 'WRITE':
                return ['writemiss','M']
            elif cpumsg == 'READ':
                return ['readhit','S']
            elif addrcond and busmsg == 'writemiss':
                return ['neutral','I']
            elif addrcond and busmsg == 'readmiss':
                return ['neutral','S']
            else:
                return ['neutral','S']
        elif blockstate == 'O':
            if cpumsg == 'WRITE':
                return ['writehit','M']
            elif cpumsg == 'READ':
                return ['readhit','O']
            elif addrcond and busmsg == 'readmiss':
                return ['supply','O']
            elif addrcond and busmsg == 'writemiss':
                return ['writeback','I']
            else:
                return ['neutral','O']
        elif blockstate == 'M':
            if cpumsg == 'WRITE':
                return ['writehit','M']
            elif cpumsg == 'READ':
                return ['readhit','M']
            elif addrcond and busmsg == 'readmiss':
                return ['supply','O']
            elif addrcond and busmsg == 'writemiss':
                return ['writeback','I']
            else:
                return ['neutral','M']
        elif blockstate == 'E':
            if cpumsg == 'WRITE':
                return ['writehit','M']
            elif cpumsg == 'READ':
                return ['readhit','E']
            elif addrcond and busmsg == 'readmiss':
                return ['neutral','S']
            elif addrcond and busmsg == 'writemiss':
                return ['neutral','I']
            else:
                return ['neutral','E']
        else:
            return ['neutral', blockstate]

# print(moesifsm('M', '1111', '', '1111', 'writemiss'))