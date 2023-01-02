from flask import render_template,redirect,url_for,session,request,flash
from Market.models import get_user_details
from Market import app,bcrypt

@app.route('/')
@app.route('/home')
def home():
    
    return render_template('base.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':

        username=request.form['username1']
        entered_password=request.form['password1']

        conn=get_user_details()
        db=conn.cursor()

        users=db.execute('''select * from user where username="'''+ username+'''" ''')
        data=[dict(id=user[0],username=[1],password=user[3]) for user in users.fetchall()]
        if data:
            data1=data[0]['password']
            id_user=data[0]['id']
            username_data=data[0]['username']
            if bcrypt.check_password_hash(data1,entered_password):
                
                session['user']=id_user
                # session['username']=username_data
                flash('You have sucessfully logged in')
                return redirect(url_for('dashboard'))
            else:
                flash('Password is wrong')
        else:
            flash('Entered username is wrong')
    return render_template('login.html')





@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':

        username=request.form['username']
        email=request.form['email_id']
        password=request.form['password']
        confirm_password=request.form['confirm_password']

        
        conn=get_user_details()
        db=conn.cursor()

        users=db.execute('''select * from user where username="'''+ username+'''" ''')
        data=[user[1] for user in users.fetchall()]
        if data:
            flash('Username or email is already exists!!!')

        else:

            if username and email:
                if password:
                    if password==confirm_password:

                        hashed_password=bcrypt.generate_password_hash(password)
                        data=[username,email,hashed_password]
                        user_commit=db.execute('''insert into user(username,email,password) values(?,?,?)''',data)
                        conn.commit()
                        conn.close()
                        flash('Sucessfully registerd')
                        
                    else:
                        flash('please match the password')
                    
                else:
                    flash('please enter your password')
            else:
                flash('please fill username and email')           

    return render_template('register.html')

@app.route('/dashboard')

def dashboard():
    if 'user'in session:
        user=session['user']
        conn=get_user_details()
        db=conn.cursor()
        
        users=db.execute(f'''select * from user where id={user}''')
        user_data=[row[1] for row in users.fetchall()]
        user_data=user_data[0]
        return render_template('dashboard.html',user=user,user_data=user_data)
    return "Please login"

@app.route('/logout')
def logout():
    if 'user' in session:

        session.pop('user',None)
        
        flash('You have logged out')
        return redirect(url_for('login'))
    
    return "Please login in"


@app.route('/market',methods=['GET','POST'])

def market():
    if 'user' in session:
        if request.method=='POST':
            user=session['user']
            id_item=request.form['purchased_item']
            conn=get_user_details()
            cur=conn.cursor()
            user_data=cur.execute(f'''select * from user where id={user}''')
            user_data=[dict(budget=row[4]) for row in user_data.fetchall()]
            item_data=cur.execute(f'''select * from item where id={id_item}''')
            item_data=[dict(item_name=row[1],price=row[2]) for row in item_data.fetchall()]
           
            if item_data:
                user_budget=user_data[0]['budget']
                item_price=item_data[0]['price']
                if user_budget>=item_price:
                    
                    item_data=cur.execute(f'''update item set item_user_id={user} where id={id_item} ''')
                    user_budget=user_budget-item_price
                    user_data=cur.execute(f'''update user set budget={user_budget} where id={user}''')
                    
                    conn.commit()
                    conn.close()
                    
                    flash('You have purchased this item')
                else:
                    flash('You dont have enough balance')
            else:
                flash('Item is not present')
            return redirect(url_for('market'))

        if request.method=='GET':
            conn=get_user_details()
            cur=conn.cursor()
            
            data=cur.execute('select * from item where item_user_id  is Null')
            whole_items=[dict(id=row[0],item_name=row[1],price=row[2],description=row[3]) for row in data.fetchall()]
            return render_template('market.html',whole_items=whole_items)

    return "please login "
    
    

@app.route('/owned_item',methods=['GET','POST'])
def owned_item():
    if 'user' in session:

        user=session['user']
        conn=get_user_details()
        cur=conn.cursor()
        data=cur.execute(f'''select * from item where item_user_id={user}''')
        item_data=[dict( id=row[0],item_name=row[1],user_id=row[4]) for row in data.fetchall()]

        if item_data:
            
            if request.method=='POST':
                selling_item=request.form['sell_item']
                user_data=cur.execute(f''' select * from user where id={user}''')
                user_budget=[dict(budget=row[4]) for row in user_data.fetchall()]
                user_budget=user_budget[0]['budget']
                item=cur.execute(f'''select * from item where id={selling_item}''')
                items=[dict(owner_id=row[4],price=row[2]) for row in item.fetchall()]
                item_price=items[0]['price']

                if user==items[0]['owner_id']:

                    item=cur.execute(f'''update item set item_user_id=Null where id={selling_item}''')
                    
                    user_budget=user_budget+item_price
                    
                    data=cur.execute(f'''update user set budget={user_budget} where id={user}''')
                    
                    conn.commit()
                    conn.close()
                    flash('You have sold sucessfully')
                    return redirect(url_for('market'))
        
        else:
            flash('You dont own any items')
        return render_template('owned.html',item_data=item_data)
    return "Not logged in"

@app.route('/search',methods=['GET','POST'])
def search():
    
    if request.method=='POST':
        search_data=request.form['searched']
        if search:
            conn=get_user_details()
            cur=conn.cursor()
            datas=cur.execute(f''' select * from item where item_name like"'''+'%'+search_data+'%'+'''" ''')

           
            datas=[dict(item_name=row[1]) for row in datas.fetchall()]
            conn.close()

            return render_template('search.html',datas=datas,search_data=search_data)

    return render_template('search.html')
