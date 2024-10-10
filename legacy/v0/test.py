

tot = 0
s = 0
n = 100
r = 1+(.09/12)
i = 0
period = 12*25

while i < period:
    tot += n
    tot = tot*r
    s += n
    i += 1
    print(str(i) + "th month, $" + str(tot) + ", initial = $%s"%s + "return =%s"%(tot/s))