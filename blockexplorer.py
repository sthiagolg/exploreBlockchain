#https://github.com/blockchain/api-v1-client-python/blob/master/docs/blockexplorer.md
#https://www.blockchain.com/api/blockchain_api

from blockchain import blockexplorer
import argparse
import multiprocessing
from multiprocessing import Process, Lock


parser = argparse.ArgumentParser(description='Cole')
parser.add_argument("-t","--transaction", help="transaction hash",type=str)

parser.add_argument("-u","--utxo", help="UTXO",type=str)

args = parser.parse_args()

txHash = args.transaction
utxo = args.utxo

#block = blockexplorer.get_block('000000000000000016f9a2c3e0f4c1245ff24856a79c34806969f5084f410680')
#print(str(block.hash))
#tx = blockexplorer.get_tx('bb0f83721c87e9a55db296a4c67b09d7b001ed5d533dc556f23b5257a5f55200')




def listInOut(txHash):
     tx = blockexplorer.get_tx(txHash)
     print("TxHash: "+txHash)
     print("TIME: "+str(tx.time))


     print(str("INPUTS: "+str(len(tx.inputs))))

     totalIN=0
     for i in range(len(tx.inputs)):

         try:
             print(tx.inputs[i].address+": "+str(tx.inputs[i].value/100000000))
             totalIN+=tx.inputs[i].value
         except:
            print("Coinbase transaction ")
            #totalIN+=tx.inputs[i].value
     #print("total IN: "+str(totalIN/100000000))
     print()


     print(str("OUTPUTS: "+str(len(tx.outputs))))

     totalOUT=0
     for i in range(len(tx.outputs)):
         spent = tx.outputs[i].spent
         print(tx.outputs[i].address+": "+str(tx.outputs[i].value/100000000)+" | spent: "+str(spent))
         totalOUT+=tx.outputs[i].value
         #print(tx.outputs[i].n)
     print("total: "+str(totalOUT/100000000)+" BTC")


     print("-------------------------------")
     return (tx.inputs , tx.outputs)
     #print("Tx fees: "+str((totalIN-totalOUT)/100000000))

def listUTXO(utxoOfAddress):
    try:
        outs = blockexplorer.get_unspent_outputs(utxo)
        print("UTXOs for "+utxo)
        for i in outs:
            print(i.value/100000000)
    except:
        print("No UXTOs available")


def nextHoop(txHash):
    tx = blockexplorer.get_tx(txHash)

    global finalAddr

    nextAddr = []
    finalAddr = []

    for out in tx.outputs:
        if out.spent:
            nextAddr.append((out,tx.time))
            print("Next Hoop: "+out.address)
        else:
            finalAddr.append(out)


    return nextAddr,finalAddr

def nextTransaction(PrevOut,txDate):

    transactionList = transactions(PrevOut.address)

    addressIN = False

    for trans in transactionList:

        for inp in trans.inputs:
            if trans.time> txDate and PrevOut.address==inp.address:

                return trans


def startSearch(txHash):

    (next,final) = nextHoop(txHash)



    while next!=[]:
        #print("test")
        #print("NEXT/FINAL"+next,final)
        for out in next:

            trans = nextTransaction(out[0],out[1])
            (next,final) = nextHoop(trans.hash)
        #return
    #print(next,final)
    for out in final:
        print(out.address+": "+str(out.value/100000000)+ " BTC")





def transactions(addr):
    address = blockexplorer.get_address(addr)

    transactionsAll = []

    print("TRANSACTIONS of "+str(addr))

    for trans in address.transactions:


        #(input,output) = listInOut(trans.hash)
        transactionsAll.append(trans)

    return transactionsAll[::-1]


def searchFutureOfTransaction(txHash,percent):


    #print("TEEEEEESTEEEEEE")
    tx = blockexplorer.get_tx(txHash)

    OUTPUTLIST = tx.outputs

    print(len(OUTPUTLIST))

    valueOut = 0

    for OUTPUT in OUTPUTLIST:
        valueOut += OUTPUT.value


    #mutex = Lock()

    global finalTable

    for OUTPUT in OUTPUTLIST:

        print(OUTPUT.spent)

        if not OUTPUT.spent:

            #mutex.acquire()
            finalTable.append((OUTPUT.address,OUTPUT.value/100000000,percent*OUTPUT.value/valueOut*100))
            #mutex.release()
            print(finalTable)
            print("utxo added")


        else:

            transactionList=transactions(OUTPUT.address)

            for trans in transactionList:
                (inputlist,outputlist)=listInOut(trans.hash)



                valueIn=0
                for inp in inputlist:
                    valueIn+=inp.value

                ratio=1
                for inp in inputlist:

                    if trans.time > tx.time and inp.address==OUTPUT.address :

                        if valueIn > OUTPUT.value:
                            print("new inputs added!!!")
                        ratio=inp.value/valueIn

                        #print("PERCENT: "+str(percent*inp.value/valueIn*100)+"%")
                        searchFutureOfTransaction(trans.hash,ratio*percent*OUTPUT.value/valueOut)
                        break


                    #break
                valueIn=0

            #print(afterTx)

                #for out in transactionList[i].outputs:
                    #transactionList=transactions(out.address)
                #worker = multiprocessing.Process(target = searchFutureOfTransaction, args = (trans.hash,))
                    #searchFutureOfOutput(out)
                #worker.start()


                #worker.join()
class Node(object):
    def __init__(self):
        self.data = None # contains the data
        self.next = None # contains the reference to the next node


class LinkedList:
    def __init__(self):
        self.cur_node = None

    def add_node(self, data):
        new_node = Node() # create a new node
        new_node.data = data
        new_node.next = self.cur_node # link the new node to the 'previous' node.
        self.cur_node = new_node #  set the current node to the new one.

    def list_print(self):
        node = self.cur_node # cant point to ll!
        while node:
            print (node.data,end="->")
            node = node.next


if __name__ == "__main__":

    #transactions("1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a")

    """ll = LinkedList()
    ll.add_node(1)
    ll.add_node(2)
    ll.add_node(3)
    ll.add_node(2)

    ll.list_print()"""

    global finalTable

    global finalAddr

    finalTable = []

    finalAddr = []

    """for t in trans:
        for out in t:
            print(out.address)"""

    txHash = "0c60ce100b7d4a6a12b767896606d3e777243cac54d7cc539d277aae57e5cd76"


    tx = blockexplorer.get_tx(txHash)

    OUTPUTLIST = tx.outputs


    valueOut = 0

    for OUTPUT in OUTPUTLIST:
        valueOut += OUTPUT.value


    #print(finalTable)

    searchFutureOfTransaction(txHash,1)

    total=0
    percent = 0

    for i in finalTable:
        total+=i[1]
        percent+=i[2]

    print("Total First Tx: "+str(valueOut/100000000))
    print("Total after: "+str(total))
    print("Percent after: "+str(percent)+"%")





#listUTXO("3Kcw4gQ2xvaYYXvuvjRXk62BaTvXz59aJM")
    #listInOut("84dfbad566e2bfad28b09dbfbcc4598804668d516dfa217d173b578b1fbb9ba1")
