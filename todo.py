from flask import Flask,render_template,redirect,request,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/tr\PycharmProjects/22.TodoApp/todo.db'
db = SQLAlchemy(app)

# Oluşturulan her clası bir tablo olarak ekliyoruz veritabanına
class Todo(db.Model):
    id = db.Column(db.Integer,primary_key = True)# auto inclement oluyor
    title = db.Column(db.String(80))
    complete = db.Column(db.Boolean)

#index sayfasını görüntüleme
@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template("index.html",todos = todos)

# Todo ekleme
@app.route("/add", methods = ["POST"])
def addTodo():
    title = request.form.get("title")
    newTodo = Todo(title = title,complete= False)
    db.session.add(newTodo)
    db.session.commit()
     
    return redirect(url_for("index"))

# Todo başlık ve durumunu güncelleme
@app.route("/edit/<string:id>", methods = ["GET","POST"])
def edittodo(id):
    if request.method == "POST":
        todo = Todo.query.filter_by(id=id).first()
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