from flask import Flask, request, redirect, render_template, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:iyswtric17@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abcdefghij'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#Before any request, check if the user is logged in:

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'allposts', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#route to log in

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        
        if user and user.password==password:
            session['username']=username
            flash('You are logged in', "logged")
            return render_template('newpost.html')
        else:
            flash("User password incorrect, or user doesn't exist", 'error')
            

    return render_template('login.html')

#route to signup

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        verify=request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if not username: 
                flash('Please provide a username', 'error')
            if not password: 
                flash('Please provide a password', 'error')
            if verify !=password: 
                flash('Please use the same passwords to verify', 'error')
           
            else:
                new_user=User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username']=username
                return redirect('/newpost')
            

    return render_template('signup.html')

#Route to logout:

@app.route('/logout')
def logout():
    del session['username']
    flash("You are logged out")
    return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    
    users = User.query.all()
    return render_template('index.html', users=users, title='Blogz')

#New post

@app.route('/newpost', methods=['POST', 'GET'])
def add_new_blog():
    
    

    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog-entry']
        error = ''
        owner = User.query.filter_by(username=session['username']).first()
        
        if not title or not body:
            error = "Please provide a blog title and a blog entry."
            return render_template('newpost.html', error=error)
        else:
            new_blog = Blog(owner=owner, title=title, body=body)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/allposts')
    if request.method =='GET':

        return render_template('newpost.html')

#Blog

@app.route('/allposts')
def all_posts():
    if not request.args:
        blogs = Blog.query.order_by(Blog.id.desc()).all()
        return render_template("allposts.html", blogs=blogs)
    elif request.args.get('id'):
        user_id=request.args.get('id')
        blog=Blog.query.filter_by(id=user_id).first()
        return render_template('post.html', blog=blog)
    
    elif request.args.get('user'):
        user_id=request.args.get('user')
        user=User.query.filter_by(id=user_id).first()
        blogs=Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', blogs=blogs, user=user)


if __name__ == '__main__':
    app.run()