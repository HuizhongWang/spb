# spb
spb ID: 1159528
### 1. Web Application Structure

1. The route "/" serves as the homepage, but it actually displays the "/currentjobs" page.
2. For technicians, their homepage is also the "/currentjobs" route (linked to currentjoblist.html), where they can view current jobs and navigate to the "/addjobs" route (linked to addjob.html) to add new jobs.
- The administrator's homepage is "/admin", from which they can access several functional pages: 
  - "/customerlist" (linked to customer_list.html) to view customer lists
  - "/customersearch" (linked to customer_search.html) to search for customers
  - "/addcustomer" (linked to add_customer.html) to add customers
  - "/addservice" (linked to add_service.html) to add services
  - "/addpart" (linked to add_part.html) to add parts
  - "/schedule" (linked to schedule_job) to schedule jobs
  - "/unpaidbills" (linked to unpaid_bills.html) to confirm unpaid bills
  - "/historybills" (linked to billing_history.html) to display all billing history
3. Additionally, there is a base.html serving as a parent template, containing common elements for all pages. The app.py file also includes two functions, getCursor() and closeCursor(), to facilitate database management within routes.

### 2. Design Decisions

1. Due to the numerous functionalities available to the administrator, a functional list is provided on each of their pages. This allows for easy navigation to other functionalities within the current page, eliminating the need to return to the administrator's homepage for further access.
2. The "History Bills" page displays all jobs, where the "completed" and "paid" fields in the database are marked using the numbers 1 and 0. In the HTML page for user display, these are translated to "yes" and "no" respectively using conditional statements.
3. During the addition of services/parts, data validation is required. This includes checking if the part/service already exists. Additionally, since the price for services/part is limited to a maximum of three digits in the database, and the total cost is limited to a maximum of four digits in the database frontend validation is necessary to enforce this constraint on prices.
4. After clicking the "Complete" button on the "Add Jobs" page, modifications cannot be made. Therefore, clicking the button will directly redirect to the "Current Jobs" page.

### 3. Database Questions

1. What SQL statement creates the job table and defines its fields/columns? (Copy and paste the relevant lines of SQL.)
   ```sql
   CREATE TABLE IF NOT EXISTS job (
       job_id INT auto_increment PRIMARY KEY NOT NULL,
       job_date date NOT NULL,
       customer int NOT NULL,
       total_cost decimal(6,2) default null,
       completed tinyint default 0,
       paid tinyint default 0
   );
2. Which line of SQL code sets up the relationship between the customer and job tables?
    ```sql
    Copy code
    FOREIGN KEY (customer) REFERENCES customer(customer_id) ON UPDATE CASCADE
3. Which lines of SQL code insert details into the parts table?
    ```sql
    INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Wiper blade', '12.43');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Left fender', '260.76');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Right fender', '260.76');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Tail light', '120.54');
    INSERT INTO part (`part_name`, `cost`) VALUES ('Hub Cap', '22.89');
4. Suppose that as part of an audit trail, the time and date a service or part was added to a job needed to be recorded, what fields/columns would you need to add to which tables? Provide the table name, new column name and the data type. (Do not implement this change in your app.)
    Table Name: job_service, job_part
    New Column Name: add_datetime
    Data Type: datetime
5. Suppose logins were implemented. Why is it important for technicians and the office administrator to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
    The differentiation in access routes for technicians and the office administrator is intended to provide them with different content and distinguish their usage permissions.
    a. If certain confidential information is visible to all employees, it would increase the risk of data leakage.
    b. If everyone can see all information, it will reduce efficiency in daily work as individuals primarily focus on their own business-related content. Having access to all data during routine information searches may overwhelm and hinder productivity.