from flask import Flask,flash
from flask import render_template
from flask import request,session
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect
import decimal
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123456'

dbconn = None
connection = None

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


@app.route("/addjobs",methods = ["GET","POST"])    
def addjobs():
    connection = getCursor()
    global job_detail_list,service_list,part_list,serviceall,partall
    total_cost = ""
    job_id = request.args.get('job_id') 
    if request.method == 'GET':     
        # show job detail
        connection.execute("""SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date from job 
            inner join customer on job.customer= customer.customer_id 
            where job.job_id= %s
            group by job.job_id;""", (job_id,) )        
        job_detail_list = connection.fetchall()    

        # job detail of service
        connection.execute("""select s.service_name,s.cost,js.qty from job_service js
            inner join service s on js.service_id = s.service_id
            where js.job_id = %s
            order by s.service_name;""", (job_id,) )
        service_list = connection.fetchall() 

        # job detail of part
        connection.execute("""select p.part_name,p.cost,jp.qty from job_part jp
            inner join part p on jp.part_id = p.part_id
            where jp.job_id = %s
            order by p.part_name;""", (job_id,))
        part_list = connection.fetchall() 

        # all service/part name
        connection.execute("select service_name from service order by service_name")
        serviceall = connection.fetchall() 
        connection.execute("select part_name from part order by part_name")
        partall = connection.fetchall() 

        session['job_id'] = request.args.get('job_id')
             
    elif request.method == 'POST':     
        job_id = session.get('job_id')

        # get input imformation
        service = request.form.get('service_name') 
        service_qty = request.form.get('service_qty') 
        part = request.form.get('part_name') 
        part_qty = request.form.get('part_qty') 
        qty = r'^[1-9]\d*$'
        match_service = re.match(qty,service_qty)
        match_part = re.match(qty,part_qty)

        # complete the job
        if request.values.get("complete") == "complete":           
            connection.execute("update job set completed=1 where job_id=%s",(job_id,))
            # total service cost
            connection.execute("""select sum(js.qty*s.cost) from job_service js
                inner join service s on js.service_id = s.service_id 
                where js.job_id = %s;""",(job_id,))
            service_cost = connection.fetchone()
            # total part cost
            connection.execute("""select sum(jp.qty*p.cost) from job_part jp
                inner join part p on jp.part_id = p.part_id 
                where jp.job_id = %s;""",(job_id,))
            part_cost = connection.fetchone()
            if  service_cost!= None and part_cost == None:
                total_cost = service_cost[0]
            elif service_cost== None and part_cost != None:
                total_cost = part_cost[0]
            elif service_cost != None and part_cost != None:
                total_cost = part_cost[0] + service_cost[0]
            print("=========================",service_cost,type(service_cost),part_cost,type(part_cost),total_cost)
            flash("The job is marked as completed.","success")
        
        # add job
        if request.values.get("add") == "add":
            # add service to the job
            if service!="Open this select menu" and match_service:
                # through service_name get service_id
                connection.execute("select service_id from service where %s = service_name",(service,))
                service_id= connection.fetchone()[0]

                # check if the service_id is existed in the job
                connection.execute("select qty from job_service where %s = service_id and %s = job_id",(service_id,job_id,))
                check_service= connection.fetchone()
                if check_service == None: 
                    connection.execute("insert into job_service value (%s,%s,%s)",(job_detail_list[0][0],service_id,service_qty,))
                else:
                    service_qty = int(service_qty)
                    service_qty = service_qty + check_service[0]
                    connection.execute("update job_service set qty=%s where service_id=%s",(service_qty,service_id,))
                flash("Add service to the job successfully","success")

                # selct service again after add jobs
                connection.execute("""select s.service_name,s.cost,js.qty from job_service js
                    inner join service s on js.service_id = s.service_id
                    where js.job_id = %s
                    order by s.service_name;""", (job_id,) )
                service_list = connection.fetchall() 
            
            # add part to the job
            elif part!="Open this select menu" and match_part:             
                # through part_name get part_id
                connection.execute("select part_id from part where %s = part_name",(part,))
                part_id= connection.fetchone()[0]
                # check if the part id is existed in the job
                connection.execute("select qty from job_part where %s = part_id and %s = job_id",(part_id,job_id))
                check_part= connection.fetchone()
                if check_part == None:
                    connection.execute("insert into job_part value (%s,%s,%s)",(job_detail_list[0][0],part_id,part_qty,))
                else:
                    part_qty = int(part_qty)
                    part_qty = part_qty + check_part[0]
                    connection.execute("update job_part set qty=%s where part_id=%s",(part_qty,part_id,))
                flash("Add part to the job successfully","success")

                # selct part again after add jobs
                connection.execute("""select p.part_name,p.cost,jp.qty from job_part jp
                    inner join part p on jp.part_id = p.part_id
                    where jp.job_id = %s
                    order by p.part_name;""", (job_id,) )
                part_list= connection.fetchall() 

            else:
                flash("Please choose at least one part/service and input the right qty.","danger")

    return render_template("addjobs.html",job_detail_list=job_detail_list,service_list=service_list,part_list=part_list,serviceall=serviceall,partall=partall,total_cost=total_cost) 


@app.route("/admin",methods = ["GET","POST"]) 
def admin():
    return render_template("admin.html")  


@app.route("/customerlist") 
def customerlist():
    connection = getCursor()
    connection.execute("select * from customer order by family_name,first_name")
    customer_list = connection.fetchall() 
    return render_template("customer_list.html",customer_list=customer_list)    


@app.route("/customersearch",methods = ["GET","POST"]) 
def customersearch():
        connection = getCursor()
        if request.method == "GET":   
            connection.execute("select * from customer order by family_name,first_name")
            customer_list = connection.fetchall() 
            return render_template("customer_search.html",customer_list=customer_list)  
        else:
            search = request.form.get("search")
            connection.execute("""select * from customer 
                where family_name like '%%%%%s%%%%' or first_name like '%%%%%s%%%%' 
                order by family_name,first_name"""% (search,search) )
            search_customer = connection.fetchall() 
            return render_template("customer_search.html",customer_list=search_customer )  


@app.route("/addcustomer",methods = ["GET","POST"]) 
def addcustomer():
    connection = getCursor()
    if request.method == "GET":   
        return render_template("add_customer.html")  
    else:
        # get input information
        familyname= request.form.get("familyname").strip()
        firstname= request.form.get("firstname")
        email= request.form.get("email").strip()
        phone= request.form.get("phone").strip()
        # check input information
        if familyname == "" or not re.match("^.{1,25}$",familyname):
            flash("Please input the family name (Not exceeding 25 letters).","danger")
        elif firstname!= None and not re.match("^.{0,25}$",firstname):
            flash("The family name should not exceed 25 letters. Please input again","danger")
        elif not re.match(".*@.*",email):
            flash("Please input the right email.","danger")
        elif not re.match("^\d{1,11}$",phone):
            flash("Please input the right phone.","danger")
        # insert into database
        else:
            connection.execute("insert into customer value(0,%s,%s,%s,%s)",(firstname,familyname,email,phone,))
            flash("Add successfully !","success")
        return redirect(url_for('addcustomer'))     
    

@app.route("/addservice",methods = ["GET","POST"]) 
def addservice():  
    connection = getCursor()
    if request.method == "GET":   
        return render_template("add_service.html")  
    else:
        # get service name
        servicename= request.form.get("servicename").strip()
        # check part cost format
        servicecost= str(request.form.get("servicecost")).strip()
        cost = r'^[1-9]\d{0,2}(\.\d{1,2})?$'
        match_cost = re.match(cost,servicecost)
        connection.execute("select service_name from service where service_name= %s",(servicename,))
        service= connection.fetchone()
        # service name should not be empty,service name should not be repeat,service cost shoule be in correct format
        if servicename == "":
            flash("Please input the service name.","danger")
        elif service != None:
            flash("The service name is already existed. Please input again.","danger")
        elif not match_cost:
            flash("The cost should be in 0.01~999.99! Please input again.","danger")
        # insert into database
        else:
            servicecost = decimal.Decimal(servicecost)
            connection.execute("insert into service value(0,%s,%s)",(servicename,servicecost,))
            flash("Add successfully !","success")
        return redirect(url_for('addservice'))        

@app.route("/addpart",methods = ["GET","POST"]) 
def addpart():
    connection = getCursor()
    if request.method == "GET":   
        return render_template("add_part.html")   
    else:
        # get part name
        partname= request.form.get("partname").strip()
        # check part cost format
        partcost= str(request.form.get("partcost")).strip()
        cost = r'^[1-9]\d{0,2}(\.\d{1,2})?$'
        match_cost = re.match(cost,partcost)
        connection.execute("select part_name from part where part_name= %s",(partname,))
        part= connection.fetchone()
        # part name should not be empty,part name should not be repeat,part cost shoule be in correct format
        if partname == "":
            flash("Please input the part name.","danger")
        elif part != None:
            flash("The part name is already existed. Please input again.","danger")
        elif not match_cost:
            flash("The cost should be in 0.01~999.99! Please input again.","danger")
        # insert into database
        else:
            partcost = decimal.Decimal(partcost)
            connection.execute("insert into part value(0,%s,%s)",(partname,partcost,))
            flash("Add successfully !","success")
        return redirect(url_for('addpart'))        
      

@app.route("/schedule",methods = ["GET","POST"]) 
def schedule():
    connection = getCursor()
    # get all customer id/name for choosing 
    connection.execute("""select concat(customer_id,"-",ifnull(first_name,'-'),'-',family_name) from customer""")
    idname_list = connection.fetchall()

    if request.method == "GET":   
        return render_template("schedule_job.html",idname_list=idname_list)   
    else:
        # get the input data and fomat
        customer_get = request.form.get("customerid").strip()   
        date_get = request.form.get("date").strip()     
        print(customer_get,date_get)
        # check input data
        flag = str
        if date_get == "" or customer_get == "":
            flash("Please select a customer and a date.","danger")
        else:
            for idname in idname_list:
                if idname[0] == customer_get:
                    flag = 1
                    format = "%Y-%m-%d"
                    date = datetime.strptime(date_get, format).date()
                    customer = request.form.get("customerid").split("-")
                    customerid = int(customer[0])
                    connection.execute("insert into job(job_id,job_date,customer) value(0,%s,%s)",(date,customerid,))
                    flash("Schedule successfully !","success")
            if flag != 1:                
                flash("Please select a customer from the options.","danger")
        return redirect(url_for('schedule'))    
        

@app.route("/unpaidbills",methods = ["GET","POST"]) 
def unpaidbills():
    connection = getCursor()
    if request.method == "GET":   
        connection.execute("""SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date from job 
            inner join customer on job.customer= customer.customer_id 
            where job.paid=0 and job.completed=1
            order by job.job_date,job.customer;""")
        unpaidbills = connection.fetchall() 
        return render_template("unpaid_bills.html",unpaidbills = unpaidbills)   
    else:
        # filter by customer name/id
        search = request.form.get("search")
        connection.execute("""SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date from job 
            inner join customer on job.customer= customer.customer_id 
            where job.paid=0 and job.completed=1 and 
                    (customer.family_name like '%%%%%s%%%%' or customer.first_name like '%%%%%s%%%%' or job.customer="%s") 
            order by job.job_date,job.customer;"""% (search,search,search) )
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
