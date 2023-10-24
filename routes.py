from flask import flash, redirect, render_template, request, url_for
from app import app, mongo, bcrypt, login_manager
from models import User, Task
from flask_login import login_user, logout_user, current_user, login_required
from bson.objectid import ObjectId

@app.route('/')
def home1():
    return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user already exists
        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash('Username already exists. Choose a different one.', 'danger')
            return redirect(url_for('register'))

        # If user doesn't exist, proceed with registration
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({"username": username, "password": hashed_pw})
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({"username": username})
        if user and bcrypt.check_password_hash(user["password"], password):
            user_obj = User(user["username"], user["password"], user["_id"])
            login_user(user_obj)
            flash('Logged in!', 'success')
            return redirect(url_for('home'))
        flash('Login unsuccessful. Check username and password.', 'danger')
    return render_template('login.html')


@app.route('/')
@app.route('/home')
@login_required
def home():
    if current_user.username == 'admin':
        tasks = mongo.db.tasks.find()
    else:
        tasks = mongo.db.tasks.find({"user_id": current_user.id})
    return render_template('home.html', tasks=tasks)



@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form['title']
    description = request.form['description']
    mongo.db.tasks.insert_one({"title": title, "description": description, "user_id": current_user.id})
    flash('Task added!', 'success')
    return redirect(url_for('home'))



@app.route('/edit_task/<task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    
    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('home'))
    
    if current_user.username != 'admin' and task["user_id"] != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('home'))

    title = request.form['title']
    description = request.form['description']
    
    mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"title": title, "description": description}})
    
    flash('Task updated successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/delete_task/<task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    
    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('home'))
    
    if current_user.username != 'admin' and task["user_id"] != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('home'))
    
    mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    logout_user()  # This logs out the user
    flash('You have been logged out.', 'success')  # Display a message to the user
    return redirect(url_for('login'))  # Redirect to the login page (or wherever you want)