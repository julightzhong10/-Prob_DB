'''
CSC267A Final Project
Xufan Wang
11/23/2018
'''
import mysql.connector
import config

class Database:
    '''
    Database
    Initialize a database connection for database operation
    Default database is ***ProbDB***
    '''
    def __init__(self):
    
        self.connection = mysql.connector.connect(
            host=config.DATABASE_CONFIG["host"],
            user=config.DATABASE_CONFIG["user"],
            passwd=config.DATABASE_CONFIG["passwd"]
        )
        
        self.tables = {} # record of table name and length        
        self.cursor = self.connection.cursor() # connection cursor will be used to execute SQL
        
        dbname = config.DATABASE_CONFIG["dbname"]
        
        self.cursor.execute("SET GLOBAL local_infile = true")
        # please delete/comment out the above line if you already set the parameter yourself
        
        self.cursor.execute("DROP DATABASE IF EXISTS " + dbname)
        self.cursor.execute("CREATE DATABASE " + dbname)
        self.cursor.execute("USE " + dbname)
        
    def createTable(self, filename):
        tbname = '' # name of table
        nVars = 0 # number of variables in the table
        with open(filename, 'r') as F:
            for i in range(2):
                line = F.readline().strip() # read one line
                line = line.replace(' ', '') # remove space
                if i == 0: # read file name
                    tbname = line
                elif i == 1: # peek first line
                    ll = line.split(',') # list of all items
                    nVars = len(ll) - 1
                    if nVars == 1:
                        self.cursor.execute("CREATE TABLE " + tbname + " (c1 INT NOT NULL, prob DECIMAL(6 , 5) NOT NULL, UNIQUE KEY (c1)) ENGINE=InnoDB")
                    elif nVars == 2:
                        self.cursor.execute("CREATE TABLE " + tbname + " (c1 VARCHAR(20) NOT NULL, c2 INT NOT NULL, prob DECIMAL(6 , 5) NOT NULL, UNIQUE KEY (c1, c2)) ENGINE=InnoDB")
                    else:
                        return False
        
        self.cursor.execute("LOAD DATA LOCAL INFILE '" + filename + "' INTO TABLE " + tbname + " FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 ROWS")
        self.tables[tbname] = nVars
    
    '''
    select all rows that contains the arguments
    if selecting one argument from a table with two arguments, then need to specify the column
        - column is either 1 or 2
        - set column to 3 to indicate both
    if selecting one argument from a table with one argument or
    selecting two arguments from a table with two arguments,
    then do not need to specify column
    
    Example:
    selectByArgs(['a'], 'S') # return the row S(a) of the form [[a, Pr(S(a))]]
    '''
    def selectByArgs(self, tbname, args, column = 0):
        whereClause = ""
        if column == 0:
            if self.tables[tbname] == 1:
                whereClause = "c1=" + str(args[0])
            else:
                whereClause = "c1=" + str(args[0]) + " AND c2=" + str(args[1])
        elif column == 1 or column == 2:
            whereClause = "c" + str(column) + "=" + str(args[0])
        elif column == 3:
            whereClause = "c1=" + str(args[0]) + " OR c2=" + str(args[0])
            
        self.cursor.execute("SELECT * FROM " + tbname + " WHERE " + whereClause)
        
        '''
        if selecting only one row, return probability directly
        else, return the whole table
        '''
        if column == 0:
            return self.getProb(self.convertFormat(self.cursor.fetchall()))
        else:
            return self.convertFormat(self.cursor.fetchall())
        
    '''
    fetch entire table by name
    '''
    def getTable(self, tbname):
        self.cursor.execute("SELECT * FROM " + tbname)
        return self.convertFormat(self.cursor.fetchall())
    
    '''
    for the result with only a single row, return the probability in the result
    '''
    def getProb(self, result):
        if len(result) != 1:
            return 0.0
        else:
            return result[0][-1]
    
    '''
    convert the probabilities in the result from MySQL to float format
    also convert variable name type to string
    '''
    def convertFormat(self, result):
        output = []
        for row in result:
            row = list(row)
            row[0] = str(row[0])
            if len(row) == 3:
                row[1] = str(row[1])
            row[-1] = float(row[-1])
            output.append(row)
        return output
        
    '''
    find all possible values at specified column(s) from specified table(s)
    Input:
        positions: a list of tuples of the form (table, column)
    '''
    def getAllPossibleValues(self, positions):
        selectClause = ""
        if positions == []:
            return
            
        for pos in positions:
            selectClause += "SELECT c" + str(pos[1]) + " FROM " + pos[0] + " UNION "
        selectClause = selectClause[:-(len(" UNION "))]
        
        self.cursor.execute(selectClause)
        result = self.cursor.fetchall()
        output = []
        for tuple in result:
            output.append(tuple[0])
        output = list(set(output)) # delete duplicates
        output = [str(x) for x in output]
        return output
            
# db = Database()

# db.createTable("tP.txt")
# db.createTable("tQ.txt")
# db.createTable("tR.txt")

# print(db.selectByArgs('P', ['1']))
# print(db.getTable("Q"))

# print(db.getAllPossibleValues([('P', 1), ('R', 1), ('R', 2)]))
