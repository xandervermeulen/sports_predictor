from configparser import ConfigParser
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession, HiveContext
import os

#ENVIRONMENT DIRECTORIES
#Change to the root path of you installation directories. (ex. c:\\tools\bigdatatools\spark-3.4.0-bin-hadoop3)
spark_home = "C:\\tools\\bigdatatools\spark-3.4.0-bin-hadoop3"
hadoop_home = "C:\\tools\\bigdatatools\hadoop-3.4.0-win10-x64"
java_home = "C:\\Program Files\\Java\\jdk-17.0.4.1"
#########################

# DO NOT CHANGE ANYTHING BELOW THIS LINE
#This function can be used to set systemvariables before running code. This eliminates the need to set the variables in the os.
def setupEnvironment():
    os.environ["PYSPARK_PYTHON"] = "python"
    os.environ["SPARK_HOME"] = spark_home
    os.environ["HADOOP_HOME"] = hadoop_home
    os.environ["PYSPARK_HADOOP_VERSION"] ="3"
    os.environ["JAVA_HOME"] = java_home + os.sep
    pathlist = [spark_home + os.sep + "bin", hadoop_home + os.sep +  "bin", java_home + os.sep + "bin"]
    os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)

#This function can be used to list all environment variables.
def listEnvironment():
    import os
    for key, value in os.environ.items():
        print(f'{key}: {value}')

#This function can be used to start the sparkcluster on the local machine and return the sparksession.
def startLocalCluster(appName, partitions=4):
    builder = SparkSession.builder \
        .appName(appName) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.sql.shuffle.partitions", partitions) \
        .master("local[*]")

    extra_packages = ["org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2","com.microsoft.sqlserver:mssql-jdbc:12.2.0.jre8"] # These are the packages that are needed for the sparksession to work with kafka and sqlserver
    builder = configure_spark_with_delta_pip(builder, extra_packages=extra_packages) # This function adds the delta-lake package to the sparksession and adds the extra packages to all the executors.
    spark = builder.getOrCreate()
    print(spark.getActiveSession())
    return spark

#Configparser is a helper class to read properties from a configuration file
config = ConfigParser()
config.read('config.ini') #Define connection properties is the config file
cn = "default" #This is the default connection-name. Create a "default" profile in config.ini

#Returns a jdbc connection string based on the connection properties. Works only for sqlServer connections.
def create_jdbc():
    return f"jdbc:sqlserver://{config.get(cn, 'host')}:{config.get(cn, 'port')};database={config.get(cn, 'database')};encrypt=true;trustServerCertificate=true"

# Set the connectionName that has to be used (if you don't want to use the default profile
def set_connection(connectionName):
    global cn
    cn = connectionName

#Returns a specific property from the connection profile in the config.ini
def get_Property(propertyName):
  return config.get(cn, propertyName)