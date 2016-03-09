import queue
import unittest

class QueueTestCase(unittest.TestCase):

    def setUp(self):
        pass
 
    def tearDown(self):
        pass

    def test001_empty(self):
        q = queue.Queue()
        self.assertTrue(q.empty())
        q.put(3)
        self.assertFalse(q.empty())
        q.get()
        self.assertTrue(q.empty())

    def test002_size(self):
        q = queue.Queue()
        self.assertEqual(q.size(), 0)
        q.put(3)
        self.assertEqual(q.size(), 1)
        q.put(5)
        self.assertEqual(q.size(), 2)
        q.get()
        self.assertEqual(q.size(), 1) 
        q.get()
        self.assertEqual(q.size(), 0)   
  
    def test003_putAndget(self):
        q = queue.Queue()
        q.put(3)
        q.put(5)
        self.assertEqual(q.size(), 2)
        item = q.get()
        self.assertEqual(item, 3)
        item = q.get()
        self.assertEqual(item, 5)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(QueueTestCase)
    unittest.TextTestRunner(verbosity = 2).run(suite) 
