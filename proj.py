import psycopg2;
from datetime import datetime,timedelta;
import generator_b_id

conn = psycopg2.connect(database = "adep_metadata", 
                        user = "postgres", 
                        host= 'illin4313',
                        password = "postgres",
                        port = 5431)



#MENU CODE

class Cab:

    def __init__(self, available=True):
        self.available=available

 

    def book(self):
           if self.available:
            print("cab booked succesfully!")
            self.available=False
           else:
            print("Sorry, the cab driver is not available..")

 

    def release(self):
        self.available=True
        print("Cab released")

    def UpdateEmployee(self,usr_name):
        fname=input("First name:")
        lname=input("Last name:")
        pwd=input("pwd:")
        no=input("contact:")

        cur = conn.cursor()
        cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(usr_name,))
        e_id=cur.fetchone()[0]
        numeric_part=e_id[1:]
        numeric_id=int(numeric_part)

        sql1='''update employee_g2
                set f_name=%s,l_name=%s 
                where emp_id=%s'''
        cur.execute(sql1,(fname,lname,numeric_id))
        conn.commit()

        sql2='''update sensitive_info_g2
                set pwd=%s,contact_no=%s
                where username=%s'''
        cur.execute(sql2,(pwd,no,usr_name))
        conn.commit

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Employee credentials of {fname} {lname} were updated',date_now))
        conn.commit()

        cur.close()

    def unregisterDriver(self,username):
        cur=conn.cursor()
        cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(username,))
        e_id=cur.fetchone()[0]
        numeric_part=e_id[1:]
        numeric_id=int(numeric_part)
        cur.execute('''select f_name,l_name from drivers_g2 where driver_id=%s''',(numeric_id,))
        names=cur.fetchone()
        if names:
            fname=names[0]
            lname=names[1]

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Driver details of {fname} {lname} were deleted',date_now))
        conn.commit()


        
        cur.execute('''delete from drivers_g2 where driver_id=%s''',(numeric_id,))
        conn.commit()

        cur.execute('''delete from sensitive_info_g2 where username=%s''',(username,))
        conn.commit()
        
        print(f"Driver account {e_id} successfully deleted.")
        cur.close()
        

    def unregisterEmployee(self,usrname):
        cur=conn.cursor()
        cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(usrname,))
        e_id=cur.fetchone()[0]
        numeric_part=e_id[1:]
        numeric_id=int(numeric_part)
        cur.execute('''select f_name,l_name from employee_g2 where emp_id=%s''',(numeric_id,))
        names=cur.fetchone()
        if names:
            fname=names[0]
            lname=names[1]

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Employee details of {fname} {lname} were deleted',date_now))
        conn.commit()

        cur.execute('''delete from employee_g2 where emp_id=%s''',(numeric_id,))
        conn.commit()

        cur.execute('''delete from sensitive_info_g2 where username=%s''',(usrname,))
        conn.commit()
        
        print(f"Employee account {e_id} successfully deleted.")
        cur.close()
        
    def cabStatus(self,username):
      cur = conn.cursor()
      cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(username,))
      e_id=cur.fetchone()[0]
      numeric_part=e_id[1:]
      numeric_id=int(numeric_part)
        
      try:
        cur.execute('''select status,pickup_time from bookings_g2 where employee_id=%s''',(numeric_id,))
        rows=cur.fetchall()
        
        if not rows:
            raise Exception("No bookings have been made so far.")
        for row in rows:
            print('!!!Cab Status!!!')
            print('Status:',row[0])
            if(row[1]=='M'):
               print('Shift:Morning')
            else:
               print("Shift:Evening")
      except Exception as e:
        print(e)
      finally:
        conn.commit()
        cur.close()
    
            
        
    def Employee_Login(self,chance):
        if chance<2:
                usr_name=input("Enter your username:")
                entered_password=input("Enter your password:")

                if self.check_credentials(usr_name,entered_password):
                  while True:
                     print("1. Update Credentials")
                     print("2. Book Cab")
                     print("3. Cab Status")
                     print("4. Delete Account")
                     print("5. Log out")
                     choice=input("enter your choice:")
                     if choice=="1":
                       self.UpdateEmployee(usr_name)
                     elif choice=="2":
                       self.CabBook(usr_name)
                     elif choice=="3":
                       self.cabStatus(usr_name)
                     elif choice=="4":
                       self.unregisterEmployee(usr_name)
                       break
                     elif choice=="5":
                       break
                     else:
                       print("Invalid choice. Please try again.")

                else:
                    print("Password is incorrect!!! Try Again!!")
                    chance=chance+1
                    self.DriverLogin(chance)
        else:
            print("!!!!!!! Too many wrong attempts !!!!!!!!")

 
    def registerEmployee(self,fname,lname,usr,pwd,no):
        cur = conn.cursor()
        sql1='''insert into employee_g2(f_name,l_name) values (%s,%s)'''
        cur.execute(sql1,(fname,lname))
        conn.commit()

        query1 = '''select emp_id from public.employee_g2 where "f_name"=%s and "l_name"=%s;'''
        cur.execute(query1, (fname,lname))
        conn.commit()
        result=cur.fetchone()[0]

        if result<10:
          e_id='E00'+str(result)
        elif result<100:
          e_id='E0'+str(result)
        else:
          e_id='E'+str(result)
    
        sql2='''insert into sensitive_info_g2(e_id,username,pwd,contact_no) values (%s,%s,%s,%s)'''
        cur.execute(sql2,(e_id,usr,pwd,no))
        conn.commit

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Employee named {fname} {lname} was registered',date_now))
        cur.close()
        conn.commit()
      
       

    def NewEmployee(self):
        fname=input("First name:")
        lname=input("Last name:")
        usr=input("Username:")
        pwd=input("pwd:")
        no=input("contact:")
        self.registerEmployee(fname,lname,usr,pwd,no)

 

    def check_credentials(self,usr_name,entered_password):
                    cur=conn.cursor()
                    query1 = '''select pwd from public.sensitive_info_g2 where "username"=%s;'''
                    cur.execute(query1, (usr_name,))
                    conn.commit()
                    result=cur.fetchone()[0]
                    if result:
                         col1=result

                    cur.close()

                    if entered_password==col1:
                         return True
                    
                    return False
                    
                    

    def updateDriver(self,username):
        fname=input("First name:")
        lname=input("Last name:")
        pwd=input("pwd:")
        no=input("contact:")

        cur = conn.cursor()
        cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(username,))
        e_id=cur.fetchone()[0]
        numeric_part=e_id[1:]
        numeric_id=int(numeric_part)

        sql1='''update drivers_g2
                set f_name=%s,l_name=%s 
                where driver_id=%s'''
        cur.execute(sql1,(fname,lname,numeric_id))
        conn.commit()

        sql2='''update sensitive_info_g2
                set pwd=%s,contact_no=%s
                where username=%s'''
        cur.execute(sql2,(pwd,no,username))
        conn.commit

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Employee credentials of {fname} {lname} were updated',date_now))
        conn.commit()

        cur.close()
    
    #BOOKING
    def CabBook(self,usr_name):
      cur=conn.cursor()
      direc=int(input('1.To Office\n2.From Office'))
      if direc==1:
          dropoff_loc='amdocs'
          pickup_loc=input('Enter pickup location')
          cur.execute('''select cab_no from cab_details_g2 where location=%s''',(pickup_loc,))
          cab_no=cur.fetchone()[0]
          pickup_time='M'
      elif direc==2:
          pickup_loc='amdocs'
          dropoff_loc=input('Enter dropoff location')
          cur.execute('''select cab_no from cab_details_g2 where location=%s''',(dropoff_loc,))
          cab_no=cur.fetchone()[0]
          pickup_time='E'
      else:
          print('Wrong Choice!Try again...')
          return
      
      cur.execute('''select driver_id from drivers_g2 where cab_no=%s''',(cab_no,))
      d_id=int(cur.fetchone()[0])

      booking_date=datetime.now()+timedelta(1) 

      status='Booked'
      
      #getting emp_id
      cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(usr_name,))
      e_id=cur.fetchone()[0]
      numeric_part=e_id[1:]
      numeric_id=int(numeric_part)
      
      #getting d_id
      cur.execute('''select driver_id,f_name,l_name from drivers_g2 where cab_no=%s''',(cab_no,))
      result=cur.fetchone()
      if result:
          d_id,fname,lname=int(result[0]),result[1],result[2]
      
      generated_b_id=generator_b_id.get_booking_id(numeric_id,d_id)
      sql1='''insert into bookings_g2(employee_id,driver_id,booking_date,pickup_location,dropoff_location,status,pickup_time,b_id) values (%s,%s,%s,%s,%s,%s,%s,%s)'''
      cur.execute(sql1,(numeric_id,d_id,booking_date,pickup_loc,dropoff_loc,status,pickup_time,generated_b_id))

      sql1='''Update cab_details_g2 set seats_available=seats_available+1 where cab_no=%s'''
      cur.execute(sql1,(cab_no,))
  

      conn.commit()
      

      if pickup_time=='M':
        timing='7:00 AM'
      else:
        timing='6:15 PM'

      print(f'{fname} {lname} (Cab number: {cab_no}) will pick you at {timing} tomorrow')

      date_now=datetime.now().isoformat(sep=" ")
      sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
      cur.execute(sql3,(f'Employee {e_id} booked cab {cab_no}',date_now))
      conn.commit()
      cur.close()
      #return e_id

    def cabStatusUpdate(self,username):
        cur = conn.cursor()
        cur.execute('''select e_id from sensitive_info_g2 where username=%s''',(username,))
        e_id=cur.fetchone()[0]
        numeric_part=e_id[1:]
        numeric_id=int(numeric_part)
        print(numeric_id)

        cur.execute('''select cab_no from drivers_g2 where driver_id=%s''',(numeric_id,))
        cab_no=cur.fetchone()[0]

        sql1='''Update cab_details_g2 set seats_available=seats_available-1 where cab_no=%s'''
        cur.execute(sql1,(cab_no,))
        
      
        sql1="Update bookings_g2 set status='completed' where driver_id=%s and status='Booked'"
        cur.execute(sql1,(numeric_id,))
        

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Cab({cab_no}) has completed its route',date_now))
      
        conn.commit()
        cur.close()

    def DriverLogin(self,chance):
            if chance<2:
                usr_name=input("Enter your username:")
                entered_password=input("Enter your password:")

              
                if self.check_credentials(usr_name,entered_password):
                    print("You are logged in ....")

                    while True:
                     print("1. Update Credentials")
                     print("2. Ride Completion Confirmation")
                     print("3. Delete Account")
                     print("4. Log out")
                     choice=input("enter your choice:")
                     if choice=="1":
                       self.updateDriver(usr_name)
                     elif choice=="2":
                       self.cabStatusUpdate(usr_name)
                     elif choice=="3":
                       self.unregisterDriver(usr_name)
                       break
                     elif choice=="4":
                       break
                     else:
                       print("Invalid choice. Please try again.")                 
                else:
                    print("Password is incorrect!!! Try Again!!")
                    chance=chance+1
                    self.DriverLogin(chance)
            else:
                 print("!!!!!!! Too many wrong attempts !!!!!!!!")




    def registerDriver(self,fname,lname,usr,cab_no,password,contact_no):

        cur = conn.cursor()
        sql1='''insert into drivers_g2(f_name,l_name,cab_no) values (%s,%s,%s)'''
        cur.execute(sql1,(fname,lname,cab_no))
        conn.commit()
        
        #creating driver id of the form D00..
        cur.execute('''select driver_id from drivers_g2 where cab_no=%s''',(cab_no,))
        result=cur.fetchone()[0]
        if result<10:
          d_id='D00'+str(result)
        elif result<100:
          d_id='D0'+str(result)
        else:
          d_id='D'+str(result)
        
        
        sql2='''insert into sensitive_info_g2(e_id,username,pwd,contact_no) values (%s,%s,%s,%s)'''
        cur.execute(sql2,(d_id,usr,password,contact_no))
        conn.commit

        date_now=datetime.now().isoformat(sep=" ")
        sql3='''insert into public.log_g2(description, "timestamp") values (%s,%s)'''
        cur.execute(sql3,(f'Driver named {fname} {lname} was registered',date_now))
        cur.close()
        conn.commit()


    def fillCabDetails(self,cab_no,seats_available,total_seats,loc):
        cur=conn.cursor()
        sql1='''insert into cab_details_g2(cab_no,seats_available,total_seats,location) values (%s,%s,%s,%s)'''
        cur.execute(sql1,(cab_no,seats_available,total_seats,loc))
        conn.commit()
        cur.close()


    def NewDriver(self):
            fname = input("Enter your first name:")
            lname=input("Enter your last name:")
            contact_no= input("Enter your Contact_Info:")
            usr=input("Enter username:")
            password = input("Create your password:")
            cab_no = input("Enter your Cab Number:")
            loc=input('Enter route you will be covering:')
            

            #password=self.encrypt_password(password1)
            self.registerDriver(fname,lname,usr,cab_no,password,contact_no)
            self.fillCabDetails(cab_no,0,4,loc)


       

def func():

    cab=Cab()

    while True:
        print("1. Employee Login")
        print("2. Register Employee")
        print("3. Driver Login")
        print("4. Register Driver")
        print("5. Admin Login")
        print("6. Exit")
        choice=input("enter your choice:")
        #print(type(choice))

       

        if choice=="1":
           cab.Employee_Login(0)
        elif choice=="2":
           cab.NewEmployee()
        elif choice=="3":
           cab.DriverLogin(0)  
        elif choice=="4":
           cab.NewDriver()
        elif choice=='5':
            pass
        elif choice=="6":
            break
        else:
           print("Invalid choice. Please try again.")

           

 

if __name__ == "__main__":
    func()
    conn.close()

     
