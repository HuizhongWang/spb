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
        connection.execute("""SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date from job 
            inner join customer on job.customer= customer.customer_id 
            where completed=0 order by customer.family_name,customer.first_name;""")
        jobList = connection.fetchall() 
        return render_template("currentjoblist.html", job_list = jobList)    
    else:
        job_item = request.form["name"]
        return redirect(url_for("addjobs"))

@app.route("/addjobs",methods = ["GET","POST"])    # technician add jobs
def addjobs():
    connection = getCursor()
    job_id = request.args.get('job_id') # get job_id
  
    connection.execute("""select j.job_id,j.customer,j.job_date from job j
        left join job_service js on j.job_id=js.job_id
        left join job_part jp on j.job_id=jp.job_id
        where j.job_id= %s;""", (job_id,) )        
  
    job_detail_list = connection.fetchall() 
    return render_template("addjobs.html",job_detail_list=job_detail_list)    

@app.route("/admin",methods = ["GET","POST"]) 
def admin():
    return render_template("admin.html")    


@app.route("/customerlist",methods = ["GET","POST"]) 
def customerlist():
        connection = getCursor()
        if request.method == "GET":   
            connection.execute("select * from customer order by family_name,first_name")
            customer_list = connection.fetchall() 
            return render_template("customer_list.html",customer_list=customer_list)  
        else:
            search = request.form.get("search")
            connection.execute("select * from customer where family_name =%s or firstname=%s order by family_name,first_name;",(search,search,) )
            search_customer = connection.fetchall() 
            # return redirect(url_for("customerlist"),search_customer=search_customer )     
            return render_template("customer_list.html",customer_list=search_customer )  

@app.route("/addcustomer",methods = ["GET","POST"]) 
def addcustomer():
    return render_template("add_customer.html")  

@app.route("/addservice",methods = ["GET","POST"]) 
def addservice():
    return render_template("add_service.html")    

@app.route("/addpart",methods = ["GET","POST"]) 
def addpart():
    return render_template("add_part.html")    

@app.route("/schedule",methods = ["GET","POST"]) 
def schedule():
    return render_template("schedule_job.html")    

@app.route("/unpaidbills",methods = ["GET","POST"]) 
def unpaidbills():
    connection = getCursor()
    connection.execute("""SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date from job 
            inner join customer on job.customer= customer.customer_id 
            where completed=0 order by job.job_date,job.customer;""")
    unpaidbills = connection.fetchall() 
    return render_template("unpaid_bills.html",unpaidbills = unpaidbills)    

@app.route("/historybills",methods = ["GET","POST"])
def historybills():
    connection = getCursor()
    connection.execute("""SELECT * from customer as a
            inner join job as b
            on b.customer = a.customer_id 
            order by b.job_date,b.customer;""")
    historybills = connection.fetchall() 
    return render_template("billing_history.html",historybills=historybills)    

if __name__ == '__main__':
    app.run(debug=True)
