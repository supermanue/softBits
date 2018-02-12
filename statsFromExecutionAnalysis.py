'''
Created on 20 Dic.2017

@author: supermanue

License: GPL
'''

'''
 Log format:
Timestamp,acme11,acme12,acme13
1513769435,0,1,2

meaning: 0: empty; 1: mixed; 2: full

'''
import  sys
if __name__ == '__main__':
    fileName = sys.argv[1]

    values = []
    usage=[0,0]
    totalLines = 0
    totalCPUs=128 #a mano, como dios manda
    with open(fileName, 'r') as log:
        line = log.readline()
        for name in line.split(',')[1:-2]: #first word is always "Timestamp"
            values += [[name, 0,0,0]]

        for line in log.readlines():
            cont=0
            totalLines +=1
            valuesAux = line.split(',')
            for value in valuesAux[1:-2]: #first word is always "Timestamp"
                values[cont][int(value)+1] += 1
                cont +=1
            usage[0]+=int(valuesAux[-2])
            usage[1] +=int(valuesAux[-1])

    valuesAveraged=[]
    totalValues=[0,0,0]
    for elem in values:
        valuesAveraged+=[[elem[0].strip(), round (float(elem[1])/totalLines * 100,2),
        round (float(elem[2])/totalLines * 100,2), round (float(elem[3])/totalLines * 100,2)]]
        totalValues[0] +=elem[1]
        totalValues[1] +=elem[2]
        totalValues[2] +=elem[3]

    valuesAveraged +=[["TOTAL",round (float(totalValues[0])/(totalLines*len(valuesAveraged)) * 100,2),
    round (float(totalValues[1])/(totalLines*len(valuesAveraged)) * 100,2),
    round (float(totalValues[2])/(totalLines*len(valuesAveraged)) * 100,2)]]

    usageAveraged = [round (float(usage[0])/(totalLines*totalCPUs) * 100,2),
                     round (float(usage[1])/(totalLines*totalCPUs) * 100,2)]

    print "Node, % empty, % mixed, % full"
    for elem in valuesAveraged:
        print(elem[0] + ", " + str(elem[1]) + ", " + str(elem[2]) + ", " + str(elem[3]))

    print "\n\nCPU used: " + str(usageAveraged[0]) + "%, " + "FreeCPUs: " + str(usageAveraged[1]) + "%"
