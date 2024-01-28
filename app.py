from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None
job_item = None

# connect database
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True,auth_plugin='mysql_native_password')
    dbconn = connection.cursor()
    return dbconn

# close database
def colseCursor():
     dbconn.close()
     connection.close()

@app.route("/")
def home():
    return redirect("/currentjobs")

@app.route("/currentjobs", methods = ["GET","POST"])
def currentjobs():
    connection = getCursor()
    if request.method == "GET":
        connection.execute("SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date from job inner join customer on job.customer= customer.customer_id where completed=0 order by customer.family_name,customer.first_name;")
        jobList = connection.fetchall() 
        return render_template("currentjoblist.html", job_list = jobList)    
    else:
        job_item = request.form["name"]
        return redirect(url_for("addjobs"))

@app.route("/addjobs")  # technician add jobs
def addjobs():
    connection = getCursor()
    return render_template("addjobs.html")    


if __name__ == '__main__':
    app.run(debug=True)
