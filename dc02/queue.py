class Queue(object):

    def __init__(self):
        self.q = []

    def size(self):
        return len(self.q)

    def empty(self):
        if len(self.q) is 0:
            return True
        return False

    def put(self, data):
        self.q.append(data)
  
    def get(self):
        data = self.q.pop(0)
        return data

    def __str__(self):
        return self.q.__str__()

if __name__ == "__main__":
    q = Queue()
    
    while True:
        str_input = raw_input("Enter put item (finish: no input) : ")
       
        if len(str_input) < 1:
            print "Finished input item"
            break

        q.put(str_input)
        print str_input, "input"

        print "==============================="
        print "Queue size : ", q.size()
        print "==============================="

    while True:
        if q.empty():
            print "Queue is empty"
            break

        get_item = q.get()
        print get_item + " get, Queue size:", q.size()   
