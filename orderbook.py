import decimal
ob = """28800538 A b S 44.26 100
28800562 A c B 44.10 100
28800744 R b 100
28800758 A d B 44.18 157
28800773 A e S 44.38 100
28800796 R d 157
28800812 A f B 44.18 157
28800974 A g S 44.27 100
28800975 A e S 44 100
"""
obsplit = ob.splitlines()
obsplitret = obsplit[:2]+obsplit[3:5]+obsplit[6:]
updated_order= """28800538 A b S 44.26 100
28800562 A c B 44.10 100
28800744 R b 100
28800758 A d B 44.18 157
28800773 A e S 44.38 200
28800796 R d 157
28800812 A f B 44.18 157
28800974 A g S 44.27 100
"""

#[[string]],int,string,int,float,int
def calculateprice(orderbook,target,BS,i,netPrice,netShares):
    """
    calculates money value of target shares to be bought or sold.
    returns 0 if not enough shares
    """
    if BS == 'S' and i == len(orderbook): return 0
    if BS == 'B' and i == -1: return 0
    else:
        order = orderbook[i]
        if order[3] == BS:
            shares,price = order[5],order[4]
            if shares < netShares:
                netPrice += shares*price
                netShares -= shares
                if BS == 'B': return calculateprice(orderbook,target,'B',i-1,netPrice,netShares)
                if BS == 'S': return calculateprice(orderbook,target,'S',i+1,netPrice,netShares)
            netPrice += netShares*price
            return netPrice
        if BS == 'B': return calculateprice(orderbook,target,'B',i-1,netPrice,netShares)
        if BS == 'S': return calculateprice(orderbook,target,'S',i+1,netPrice,netShares)

hl = [[1111,'A','b','B',44.26,100],[222,'A','c','S',44.10,100],[333,'A','i','S',44.50,100]]
assert(calculateprice(hl,150,'S',0,0,150) == 6635)
assert(calculateprice(hl,50,'B',len(hl)-1,0,50) == 2213)
assert(calculateprice(hl,210,'S',0,0,210) == 0)

def reduceorder(redline,orderbook,i):
    order = redline.split(' ')
    ID,redshares= order[2],int(order[3])
    while ID not in orderbook[i]:
        i += 1
    orderbook[i][5] -= redshares
    if orderbook[i][5] > 0:
        return [orderbook,orderbook[i][3]]
    else:
        return [orderbook[:i]+orderbook[i+1:],orderbook[i][3]]
#hl = [[1111,'A','b','B',44.26,100],[222,'A','c','S',44.10,100],[333,'A','i','S',44.50,100]]
#assert(reduceorder('5555 R i 20',hl) == [[[1111,'A','b','B',44.26,100],[222,'A','c','S',44.10,100],[333,'A','i','S',44.50,80]],'S'])
#assert(reduceorder('5555 R i 100',hl) == [[[1111,'A','b','B',44.26,100],[222,'A','c','S',44.10,100]],'S'])

# takes the orderbook and a string either 'B' or 'S', returns number of shares being bought or sold
# [string],string -> int
def countshares(orderbook,BS):
    count = 0
    for i in range(len(orderbook)):
        order = orderbook[i]
        if order[3] == BS:
            shares = int(order[5])
            count += shares
    return count

new = []
for e in obsplit:
    o = e.split(' ')
    if o[1] == 'A':
        ts,add,ID,bs,p,sh = int(o[0]),o[1],o[2],o[3],float(o[4]),int(o[5])
        new.append([ts,add,ID,bs,p,sh])
assert(countshares(new,'S') == 400)

#([string],[[string]],int -> [[string]]
def addorder(lines,orderbook,i):
    """
    returns orderbook sorted by price,low to high
    """
    order = lines[i].split(' ')
    if order[1] == 'A':
        TS,A,ID,BS,price,shares = int(order[0]),order[1],order[2],order[3],float(order[4]),int(order[5])
        orderbook.append([TS,A,ID,BS,price,shares])
    if order[1] == 'R':
        TS,R,ID,shares = int(order[0]),order[1],order[2],int(order[3])
        orderbook.append([TS,R,ID,shares])
    return sorted(orderbook, key=lambda x: x[4])

assert(addorder(obsplit,[[222,'A','b','B',50,200]],0) == [[28800538,'A', 'b', 'S', 44.26, 100],[222, 'A', 'b' ,'B', 50, 200]])

def isaddorder(lines,i):
    order = lines[i].split(' ')
    if order[1] == 'A':
        return True
    return False
assert(isaddorder(['222 A b B 50 200'],0) == True)
assert(isaddorder(['222 R b B 50 200'],0) == False)

def printmessage(lines,i,orderbook,netp,target,BS):
    order = lines[i].split(' ')
    if isaddorder(lines,i):
        if BS == 'S': l = 0
        if BS == 'B': l = len(orderbook)-1
        netpriceshs = calculateprice(orderbook,target,order[3],l,0,target)
        netpriceses = decimal.Decimal(netpriceshs).normalize()
        netpriceshares = netpriceses.__trunc__() if not netpriceses % 1 else float(netpriceses)
        if netpriceshares != netp:
            if order[3] == 'S':
                return '%i %s %.2f' % (int(order[0]),'B',float(netpriceshares))
            if order[3] == 'B':
                return '%i %s %.2f' % (int(order[0]),'S',float(netpriceshares))
        return False
    if BS == 'S':
        reducepriceshares = calculateprice(orderbook,target,BS,0,0,target)
        if reducepriceshares != netp: return '%s %s %s' % (str(order[0]),'B','NA')
    if BS == 'B':
        reducepriceshares = calculateprice(orderbook,target,BS,len(orderbook)-1,0,target)
        if reducepriceshares != netp: return '%s %s %s' % (str(order[0]),'S','NA')
    return False

orderss = ['111 A c B 44.10 100','222 A d B 35 40','333 A i S 30 100','444 A w S 50 50']
new = []
for i in range(len(orderss)):
    o = orderss[i].split(' ')
    if o[1] == 'A':
        ts,add,ID,bs,p,sh = int(o[0]),o[1],o[2],o[3],float(o[4]),int(o[5])
        new.append([ts,add,ID,bs,p,sh])
sh = 100
assert(printmessage(orderss,3,new,sh,150,'S') == '444 B 5500.00')

def pricer(lines,i,orderbook,target,netpA,netpB):
    if i == len(lines): return
    if isaddorder(lines,i):
        neworderbook = addorder(lines,orderbook,i)
        order = lines[i].split(' ')
        BS = order[3]
        if BS == 'S':
            if printmessage(lines,i,neworderbook,netpA,target,BS) != False: print printmessage(lines,i,neworderbook,netpA,target,BS)
            netpA0 = calculateprice(neworderbook,target,BS,0,0,target)
            return pricer(lines,i+1,neworderbook,target,netpA0,netpB)
        if BS == 'B':
            if printmessage(lines,i,neworderbook,netpB,target,BS) != False: print printmessage(lines,i,neworderbook,netpB,target,BS)
            netpB0 = calculateprice(neworderbook,target,BS,len(neworderbook)-1,0,target)
            return pricer(lines,i+1,neworderbook,target,netpA,netpB0)
    out = reduceorder(lines[i],orderbook,0)
    reducedorderbook,BS = out[0],out[1]
    if BS == 'S':
        if printmessage(lines,i,reducedorderbook,netpA,target,BS) != False: print printmessage(lines,i,reducedorderbook,netpA,target,BS)
        netpA0 = calculateprice(reducedorderbook,target,BS,0,0,target)
        return pricer(lines,i+1,reducedorderbook,target,netpA0,netpB)
    if BS == 'B':
        if printmessage(lines,i,reducedorderbook,netpB,target,BS) != False: print printmessage(lines,i,reducedorderbook,netpB,target,BS)
        netpB0 = calculateprice(reducedorderbook,target,BS,len(reducedorderbook)-1,0,target)
        return pricer(lines,i+1,reducedorderbook,target,netpA,netpB0)

log ="""28800538 A b S 44.26 100
28800562 A c B 44.10 100
28800744 R b 100
28800758 A d B 44.18 157
28800773 A e S 44.38 100
28800796 R d 157
28800812 A f B 44.18 157
28800974 A g S 44.27 100
28800975 R e 100
28812071 R f 100
28813129 A h B 43.68 50
28813300 R f 57
28813830 A i S 44.18 100
28814087 A j S 44.18 1000
28814834 R c 100
28814864 A k B 44.09 100
28815774 R k 100
28815804 A l B 44.07 175
28815937 R j 1000
28816245 A m S 44.22 100"""
target = 200
lines = log.splitlines()
orderbook = []
i = 0
netpA = 0
netpB = 0
pricer(lines,i,orderbook,target,netpA,netpB)

def testAddOrder():
    happyLine = "28800538 A b S 44.26 100"
    sadLine = "28800975 R e 100"
    assert(isAddOrder(happyLine))
    assert(not isAddOrder(sadLine))
    assert(orderinbook(orderbook,orderbook[8]) == True)
    assert(updatorder(orderbook,orderbook[8]) == updated_orderbook)
    assert(sortorderbook(['1 A b S 8 100','2 A d S 5 50','3 A h B 2 75']) == ['3 A h B 2 75','2 A d S 5 50','1 A b S 8 100'])
