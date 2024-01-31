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
import decimal

app = Flask(__name__)

dbconn = None
connection = None
def get_flashed_messages():
    pass

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
        return redirect(url_for("addjobs"))

@app.route("/addjobs",methods = ["GET","POST"])    # technician add jobs
def addjobs():
    global get_flashed_messages
    connection = getCursor()

    # get job_id
    job_id = request.args.get('job_id') 
    connection.execute("""select j.job_id,j.customer,j.job_date from job j
        left join job_service js on j.job_id=js.job_id
        where j.job_id= %s
        group by j.job_id;""", (job_id,) )        
    job_detail_list = connection.fetchall() 

    # get service info
    connection.execute("select * from service")
    service_list = connection.fetchall() 

    # get part info
    connection.execute("select * from part")
    part_list = connection.fetchall() 
    
    if request.method == 'POST':    
        # get input imformation
        service = request.form.get('service_name') 
        service_qty = request.form.get('service_qty') 
        part = request.form.get('part_name') 
        part_qty = request.form.get('part_qty') 
        qty = r'^[1-9]\d*$'
        match_service = re.match(qty,service_qty)
        match_part = re.match(qty,part_qty)

        if service!="Open this select menu" and match_service:
            print(service)
            connection.execute("select service_id from service where %s = service_name",(service,))
            service_id = connection.fetchone()[0]
            connection.execute("insert into job_service value (%s,%s,%s)",(job_id,service_id,service_qty,))
        elif part!="Open this select menu" and match_part:
            connection.execute("select part_id from part where %s = part_name",(part,))
            part_id = connection.fetchone()[0]
            connection.execute("insert into job_part value (%s,%s,%s)",(job_id,part_id,part_qty,))

    return render_template("addjobs.html",job_detail_list=job_detail_list,service_list=service_list,part_list=part_list)    

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
            connection.execute("""select * from customer 
                where family_name like '%%%%%s%%%%' or first_name like '%%%%%s%%%%' 
                order by family_name,first_name"""% (search,search) )
            search_customer = connection.fetchall() 
            return render_template("customer_list.html",customer_list=search_customer )  

@app.route("/addcustomer",methods = ["GET","POST"]) 
def addcustomer():
    return render_template("add_customer.html")  

@app.route("/addservice",methods = ["GET","POST"]) 
def addservice():
    return render_template("add_service.html")    

@app.route("/addpart",methods = ["GET","POST"]) 
def addpart():
    partname= request.form.get("partname")
    partcost= str(request.form.get("partcost"))
    cost = r'^\d{1,3}$'
    match_cost = re.match(cost,partcost)
    
    if request.method == "POST":   # 验证不为空，是小数，名字没有重复
        connection = getCursor()
        connection.execute("select part_name from part where part_name= %s",(partname,))
        part= connection.fetchone()[0] 

        if partname != None and part != None and match_cost:
            partcost = decimal.Decimal(partcost)
            print(partcost,partname)
            connection.execute("insert into part value(0,%s,%s)",(partname,partcost,))
        else:
            print("repeat")
     
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
