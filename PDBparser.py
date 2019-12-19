'''
CSC267A Final Project
Zixiang Liu
11/17/2018
This code is tested under version:
3.7.0 [MSC v.1912 64 bit (AMD64)]
'''

class Query:
    '''
    This class parser the input query txt into intermediate language.

    for input file with txt
    R(x1), S(x1, y1) || S(x2, y2), T(x2)
    the parse method should output
    [[(R, [x1]),(S, [x1, y1])],[(S, [x2, y2]),(T, [x2])]]

    To use it, initiate with the query filename
    parse() method will return the query in the above form
    result is also stored in Query.aq
    '''
    def __init__(self, filename):
        self.filename = filename

    def setFile(self, filename):
        '''
        reset the filename
        So the object can be reused
        '''
        self.filename = filename

    def readFile(self):
        '''
        Helper function not designed to be used independently
        Read the file and put lines in self.lines
        '''
        F = open(self.filename, 'r')
        self.lines = []
        for line in F:
            self.lines.append(line)
        F.close()

    def tokenize(self):
        '''
        Helper function not designed to be used independently
        load the file txt
        remove all new line and space
        break the strings into tokens

        args:
            None
        return:
            None
            but store the result in self.allquerylist
        '''
        self.readFile()
        self.allquerystr = ''.join(self.lines).replace('\n', '')
        self.allquerylist = []
        ctk = [] # current token
        for c in self.allquerystr.replace(' ', ''):
            if c in ['(', ')', ',', '|']:
                self.allquerylist.append(''.join(ctk))
                self.allquerylist.append(c)
                ctk = []
            else:
                ctk.append(c)

    def parse(self):
        '''
        Parse the query
        for
        R(x1), S(x1, y1) || S(x2, y2), T(x2)
        the method should output
        [[(R, [x1]),(S, [x1, y1])],[(S, [x2, y2]),(T, [x2])]]

        args:
            None
        return:
            not only return the query list
            But also store it in self.aq
        '''
        self.tokenize()

        aq = [] # all query
        cq = [] # conjunctive query
        cpc = None # current predicate tuple
        cp = None # current predicate
        cv = None # current variable
        pflag = True    # flag for predicate after a comma,
                        # false for variable after a comma

        for c in self.allquerylist:
            if c == '(':
                pflag = False
                cpc = (cp, [])
            elif c == ')':
                pflag = True
                cpc[1].append(''.join(cv))
                cq.append(cpc)
                cpc = None
                cv = None
                cp = None
            elif c == ',':
                if not pflag:
                    cpc[1].append(''.join(cv))
                    cv = None
            elif c == '|':
                if cq:
                    aq.append(cq)
                    cq = []
                    cpc = None
                    cp = None
                    cv = None
                    pflag = True
            else:
                if pflag:
                    cp = c
                else:
                    cv = c
        aq.append(cq)
        self.aq = aq
        return aq

# ------------------------------------------------------------------------------
# Below is a simple test case
# for input:
#  R(x1), S(x1, y1) || S(x2, y2), T(x2) ||
#
# Guy(a, b, c), Van(ddd, res, foo), Broek(bar, bar)
#
# || Boy(next, door), Deep(dark,   fantasy)
#
# the expected output is:
# [[('R', ['x1']), ('S', ['x1', 'y1'])],
# [('S', ['x2', 'y2']), ('T', ['x2'])],
# [('Guy', ['a', 'b', 'c']),
#  ('Van', ['ddd', 'res', 'foo']),
#  ('Broek', ['bar', 'bar'])],
# [('Boy', ['next', 'door']), ('Deep', ['dark', 'fantasy'])]]
# ------------------------------------------------------------------------------
# q = Query('test.txt')
# q.parse()
