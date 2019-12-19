'''
CSC267A Final Project
Xufan Wang
11/23/2018
'''
import sys
from optparse import OptionParser
from database import Database
from PDBparser import Query
from lift import lift_rule
from grounding import Grounding
from Gibbs import Gibbs
import bruteforce

'''
	parse import using python library
'''
parser = OptionParser()
parser.add_option("-q", "--query",
                  action="store", dest="queryFile",
                  help="Specify query file.")
parser.add_option("-t", "--table", action="append", dest="tableFiles",
				  help="Specify table files.")
(options, args) = parser.parse_args()



'''
initialize database with table files

'''
print("Initializing MySQL Database...")

try:
	db = Database()
	for filename in options.tableFiles:
		print("Creating table from " + filename)
		db.createTable(filename.replace('\\','/'))
except:
	print("Error when initializing Database, please check DB requirements and try again.")
	raise
	
'''
parse the query file
'''
q = Query(options.queryFile)
pq=q.parse()


'''
try use lift rule to calculate the query
'''
l = lift_rule(db)

resultLift = l.lift(l.PL_interface(pq))

if resultLift != -1.0:
    print("The query is liftable.")
    print('result:',pq,":", '%.4f'%resultLift)
else:
    print("The query is unliftable.")
    
    
'''
other options
'''
userDecision = int(input("What do you what to do next?\n [0]Exit   [1]Gibbs Sampling   [2]Brute Force\n"))

'''
exiting
'''
if userDecision == 0:
    sys.exit()
    
'''
do Gibbs sampling
'''
if userDecision == 1:
    gibbs = Gibbs(pq, db)
    print('result:',pq,":",'%.4f'%gibbs.sample(1000))
    
'''
do brute force
'''
if userDecision == 2:
    grounding = bruteforce.getGrounding(pq, db)
    print('result:',pq,":", '%.4f'%bruteforce.sol_UCQ(grounding, db))
