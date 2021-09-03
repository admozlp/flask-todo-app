from enum import unique
from flask import Flask,render_template,redirect,request,url_for,session
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/tr\PycharmProjects/22.TodoApp/todo.db'
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfaya ulaşmak için giriş yapmalısınız","danger")
            return redirect(url_for("login"))
    return decorated_function


app.secret_key = "todo"
# Oluşturulan her clası bir tablo olarak ekliyoruz veritabanına
class Todo(db.Model):
    id = db.Column(db.Integer,primary_key = True)# auto inclement oluyor
    title = db.Column(db.String(80))
    complete = db.Column(db.Boolean)
    author_id = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))

#index sayfasını görüntüleme

@app.route("/")
@login_required
def index():
    todos = Todo.query.filter_by(author_id=session["user_id"])
    return render_template("index.html",todos=todos)
    
   



@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")          
        password = sha256_crypt.encrypt(request.form.get("password"))
        users = User.query.filter_by(username = username).first()
        
        if users:
            flash("Bu kullanıcı adı kullanılmakta","danger")
            return redirect(url_for("register"))
        newuser = User(username = username,password= password)
        db.session.add(newuser)
        db.session.commit()
        flash("Kayıt Başarıyla Tamamlandı","success")
        return redirect(url_for("login"))

    else:
        return render_template("register.html")

@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password  = request.form.get("password")
        user = User.query.filter_by(username = username).first()
        if user:
            real_pas = user.password
            if sha256_crypt.verify(password,real_pas):
                session["logged_in"] = True
                session["username"] = user.username
                session["user_id"] = user.id
          
                flash("Giriş Yapıldı","success")
                return redirect(url_for("index"))
            flash("Parola Yanlış","danger")
            return redirect(url_for("login"))
        else:
            flash("Böyle Bir Kullanıcı Bulunmuyor","danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış Yapıldı","success")
    return redirect(url_for("index"))


# Todo ekleme
@app.route("/add", methods = ["POST"])
def addTodo():
    title = request.form.get("title")
    newTodo = Todo(title = title,complete= False,author_id = session["user_id"])
    db.session.add(newTodo)
    db.session.commit()
     
    return redirect(url_for("index"))





# Todo başlık ve durumunu güncelleme
@app.route("/edit/<string:id>", methods = ["GET","POST"])
def edittodo(id):
    if request.method == "POST":
        TODO = Todo.query.filter_by(id=id).first()
        todo = Todo.query.filter_by(id=id).first()
        if request.form.get("title") == "":
            todo.title = TODO.title
        else:
            todo.title = request.form.get("title")

        if request.form.get("durum"):
            todo.complete = True
        else:
            todo.complete = False
        db.session.commit()
        return redirect(url_for("index"))
    else:
        todo = Todo.query.filter_by(id=id).first()
        return render_template("edit.html",todo = todo)

# Todo Silme
@app.route("/delete/<string:id>")
def delete(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))
    
if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)