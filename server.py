import json
from flask import Flask

from Entities.MyDatabase import db
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
    # db.execute("""TRUNCATE TABLE Forum;""", post=True)
    # db.execute("""TRUNCATE TABLE User;""", post=True)
    # db.execute("""TRUNCATE TABLE Post;""")
    # db.execute("""TRUNCATE TABLE Thread;""", post=True)
    # db.execute("""TRUNCATE TABLE Subscription;""", post=True)
    # db.execute("""TRUNCATE TABLE Follower;""", post=True)

    # this is faster
    db.execute("""DELETE Forum.* FROM Forum;""", post=True)
    db.execute("""DELETE User.* FROM User;""", post=True)
    db.execute("""DELETE Post.* FROM  Post;""")
    db.execute("""DELETE Thread.* FROM  Thread;""", post=True)
    db.execute("""DELETE Subscription.* FROM Subscription;""", post=True)
    db.execute("""DELETE Follower.* FROM Follower;""", post=True)
    return json.dumps({"code": 0, "response": "OK"})


@app.before_request
def db_connect():
    db.init_connection_and_cursor()


@app.teardown_request
def db_disconnect(exception):
    db.close_connections()


if __name__ == "__main__":
    app.run()
