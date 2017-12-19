from flask import Flask, request, redirect, render_template, flash
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
    date = db.Column(db.DateTime)

    def __init__(self, title, body, date=None):
        self.title = title
        self.body = body
        if date is None:
            date = datetime.utcnow()
        self.date = date

    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False



@app.route("/")
def index():
    #TODO The /blog route displays all the blog posts.
    return redirect("/blog")
   
@app.route("/blog")
def display_blog_entries():
    # TODO refactor to use routes with variables instead of GET parameters
    
    if request.args:
        blogpost_id = request.args.get('id')
        blog = Blog.query.get(blogpost_id)
        return render_template('individualpost.html', title="Blog Entry", blog=blog)

    # if we're here, we need to display all the entries
    # TODO store sort direction in session[] so we remember user's preference
    sort = request.args.get('sort')
    if (sort=="newest"):
        blogs = Blog.query.order_by(Blog.date.DESC()).all()
    else:
        blogs = Blog.query.all()   
    return render_template('allpost.html', title="All Entries", blogs=blogs)

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():

    if request.method =='POST':
        newpost_title = request.form['title']
        newpost_body = request.form['body']
        newpost= Blog(newpost_title, newpost_body)
        
        if newpost.is_valid():
            db.session.add(newpost)
            db.session.commit()
            url = "/blog?id=" + str(newpost.id)
            return redirect(url)
        elif newpost_title =='':
            flash("Title is required to post in the blog")
            return render_template('newpost.html',title="New Post")
        elif (newpost_body == ''):
            flash("Body is required to post in the blog")
            return render_template('newpost.html',title="New Post")
    else:
        return render_template('newpost.html',title="New Post")
        
if __name__ == '__main__':
    app.run()