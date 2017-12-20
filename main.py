from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://practiceblog:sudha@localhost:8889/practiceblog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'sudha'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)

    def __init__(self, title, body, owner, date = None):
        self.title = title
        self.body = body
        self.owner = owner
        if date is None:
            date = datetime.utcnow()
        self.date = date
        


    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    def __repr__(self):
        return str(self.username)
    

@app.before_request
def require_login():
    allowed_routes = ['newpost', 'login', 'blog', 'index', 'register', 'individualpost', 'allpost']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')



@app.route("/")
def index():
    #TODO The /blog route displays all the blog posts.
    return redirect("/blog")
   
@app.route("/blog")
def home():
    blogs=Blog.query.all()
    welcome = "Not logged in"

    if 'user' in session:
        welcome = "Logged in as:" + session['user']
        
    return render_template('home.html', title="ManiCity", blogs=blogs, welcome=welcome)

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    welcome = ""

    if 'user' in session:
        welcome = "Logged in as:" + session['user']
        existing_user = User.query.filter_by(username=session['user']).first()
    else:
        return redirect("/")

    if request.method =='POST':
        newpost_title = request.form['title']
        newpost_body = request.form['body']
        
        newpost= Blog(newpost_title, newpost_body, existing_user)
        
        if newpost.is_valid():
            db.session.add(newpost)
            db.session.commit()
            author = User.query.filter_by(id=newpost.owner_id).first()
            return redirect("/individualpost?blog_title=" +newpost_title)
        elif newpost_title =='':
            flash("Title is required to post in the blog")
            return render_template('newpost.html',title="New Post")
        elif (newpost_body == ''):
            flash("Body is required to post in the blog")
            return render_template('newpost.html',title="New Post")
    else:
        return render_template('newpost.html',title="New Post", welcome=welcome)


@app.route("/individualpost")
def blog():
    welcome = "Not logged in"
    if 'user' in session:
        welcome = "Logged in as: " + session['user']

    title = request.args.get('blog_title')
    if title:
        existing_blog = Blog.query.filter_by(title= title).first()
        author = User.query.filter_by(id= existing_blog.owner_id).first()
        return render_template("individualpost.html", 
            title= existing_blog.title, body= existing_blog.body,
            author= author.username, welcome= welcome)

    # TODO refactor to use routes with variables instead of GET parameters
    
    #if request.args:
     #   blogpost_id = request.args.get('id')
      #  blog = Blog.query.get(blogpost_id)
       # return render_template('individualpost.html', title="Blog Entry", blog=blog)

    # if we're here, we need to display all the entries
    # TODO store sort direction in session[] so we remember user's preference
    #sort = request.args.get('sort')
    #if (sort=="newest"):
        #blogs = Blog.query.order_by(Blog.date.DESC()).all()
    #else:
        #blogs = Blog.query.all()   
    #return render_template('allpost.html', title="All Entries", blogs=blogs)



@app.route("/UserPage")
def UserPosts():
    welcome = "Not logged in"
    if 'user' in session:
        welcome = "Logged in as: " + session['user']

    user = request.args.get('user_link')
    if user:
        existing_user = User.query.filter_by(username= user).first()
        user_posts = existing_user.blogs
        return render_template("UserPage.html", welcome= welcome,
            title= user+"'s posts", blogs= user_posts)

    user_list = User.query.all()
    return render_template("allpost.html", title= "All Users",
        welcome= welcome, user_list= user_list)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pwd1']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            if existing_user.password == "":
                flash("Password is required", 'error')
                return render_template('login.html')
            elif existing_user.password == password:
                session['user'] = username
                flash("Logged in")
                return redirect("/blog")
            else:
                flash("Invalid password", 'error' )
                return render_template('login.html')
        else:
            flash("Invalid Username", 'error')
            return render_template('login.html')   
            
    return render_template('login.html', title ="Login")#, username=username)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pwd1']
        verify = request.form['pwd2']
        #TODO - add validation

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            #TODO - remember the user
            session['user'] = new_user.username
            return redirect('/blog')
       
    return render_template('register.html', title= "Register for this BLog")

@app.route('/logout')
def logout():
    if 'user' in session:
        del session['user']
    return redirect('/blog')

        
if __name__ == '__main__':
    app.run()