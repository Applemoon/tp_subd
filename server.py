from flask import Flask

from Entities.MyDatabase import MyDatabase
from Entities.Forum import module as forum_module
from Entities.Post import module as post_module
from Entities.User import module as user_module
from Entities.Thread import module as thread_module


app = Flask(__name__)
app.register_blueprint(forum_module)
app.register_blueprint(post_module)
app.register_blueprint(user_module)
app.register_blueprint(thread_module)


@app.route('/db/api/clear/', methods=['POST'])
def clear():
    db = MyDatabase()
    return db.clear()


if __name__ == "__main__":
    app.run()
