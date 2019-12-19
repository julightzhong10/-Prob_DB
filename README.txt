How to use:
	1. Please run under Python3.7 and MySQL 8.0, since the code was tested under this environment.

	2. Before running, make sure to install python mysql-connector (pip install mysql-connector)

	3. Before running, please first open config.py and change the user name, password and host name for your local MySQL database system,and change dbname to a database for the program to put data.

	4. The program will change a database setting to enable file read/write, so please ensure that your account is authorized to do so.
	   Alternatively, you can change the database setting by yourself, and delete the line in database.py that change the setting:self.cursor.execute("SET GLOBAL local_infile = true")

	5. After configuration, please run the program using the following command:	
	   python ./run.py --query <query-file> --table <table-file-1> [--table <table-file-2> --table <table-file-3> ...]

	   Example:
	   		  $ python ./run.py --query ././sample_quries/test0.txt --table ./sample_tables/tP.txt --table ./sample_tables/tQ.txt --table ./sample_tables/tR.txt

				Initializing MySQL Database...
				Creating table from .\tP.txt
				Creating table from .\tQ.txt
				Creating table from .\tR.txt
				1
				The query is liftable.
				result: [[(’Q’, [’x’])]] : 0.8950
				What do you what to do next?
				[0]Exit [1]Gibbs Sampling
				[2]Brute Force
				1
				result: [[(’Q’, [’x’])]] : 0.8760
	6. Thanks.


