import Queue
import sys

testQueue = Queue.Queue()

while True:
    str_input = raw_input("Enter put item (finish : no input) : ")
    
    if len(str_input) < 1:
        print "Finished input item"
        break

    testQueue.put(str_input)
    print str_input, "input"

print "=========================="
print "Queue size : ", testQueue.qsize()
print "=========================="

while True:
    if testQueue.empty():
        print "Queue is empty"
        break
 
    get_item = testQueue.get()
    print get_item + " get, Queue size :", testQueue.qsize()
