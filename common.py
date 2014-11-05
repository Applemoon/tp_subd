import json

from Entities.MyDatabase import MyDatabase


MYSQL_DUPLICATE_ENTITY_ERROR = 1062


def strToJson(value, isBool=False):
	if isBool:
		return (value != 0)

	if value == "None":
		return None

	return value
		

def tryEncode(value):
	if value != None:
		return value.encode('utf-8')

	return value


def getForumDict(short_name="", id=""):
	if id != "":
		sql_where = "forum = {}".format(id)
	elif short_name != "":
		sql_where = "short_name = '{}'".format(short_name)
	else:
		print "VERY BAD ERROR IN getForumDict"
		return dict()

	sql = """SELECT forum, name, short_name, user FROM Forum WHERE {};""".format(sql_where)
	dbase = MyDatabase()
	forum_list_sql = dbase.execute(sql)
	if not forum_list_sql:
		return dict()
	if not forum_list_sql[0]:
		return dict()

	forum_sql = forum_list_sql[0]
	forum = dict()
	forum['id'] = strToJson(forum_sql[0])
	forum['name'] = strToJson(forum_sql[1])
	forum['short_name'] = strToJson(forum_sql[2])
	forum['user'] = strToJson(forum_sql[3])
	return forum


def getPostList(user="", date="", forum="", id="", since="", limit=-1, sort='flat', 
				order='desc'):
	# WHERE part
	if id != "":
		sql_where = "post = {}".format(id)
	elif forum != "":
		sql_where = "forum = '{}'".format(forum)
	elif user != "" and date != "":
		sql_where = "user = '{user_value}' AND date = '{date_value}'".format(
			user_value = user, date_value = date)
	else:
		print "BAD ERROR IN getPostList"
		return list()

	# since part
	since_sql = ""
	if since != "":
		since_sql = """AND date > ='{}'""".format(since)

	# sort part
	if sort != 'flat' and sort != 'tree' and sort != 'parent_tree':
		print "Wrong sort value"
		return list()
	# sort_sql = """ORDER BY Post.date {}""".format(sort)
	sort_sql = """"""

	# limit part
	limit_sql = ""
	if limit != -1:
		try:
			limit = int(limit)
		except ValueError:
			print "Wrong limit value"
			return list()
		if limit < 0:
			print "Wrong limit value"
			return list()
		limit_sql = """LIMIT {}""".format(limit)

	# order part
	if order != 'asc' and order != 'desc':
		return [json.dumps({ "code": 3, "response": "Wrong order value"}, indent=4)]
	order_sql = """ORDER BY date {}""".format(order)

	sql = """SELECT post, user, thread, forum, message, parent, date, likes, dislikes, \
		isSpam, isEdited, isDeleted, isHighlighted, isApproved FROM Post \
		WHERE {where_value} {since_value} {limit_value} {order_value} \
			{sort_value};""".format(
			where_value = sql_where, 
			since_value = since_sql,
			limit_value = limit_sql,
			order_value = order_sql,
			sort_value  = sort_sql)

	db = MyDatabase()
	post_list_sql = db.execute(sql)
	if not post_list_sql:
		return list()
	if not post_list_sql[0]:
		return list()
	
	post_list = list()
	for post_sql in post_list_sql:
		post = dict()
		post['post'] = strToJson(post_sql[0])
		post['user'] = strToJson(post_sql[1])
		post['thread'] = strToJson(post_sql[2])
		post['forum'] = strToJson(post_sql[3])
		post['message'] = strToJson(post_sql[4])
		post['parent'] = strToJson(post_sql[5])
		post['date'] = post_sql[5]
		post['likes'] = strToJson(post_sql[7])
		post['dislikes'] = strToJson(post_sql[8])
		post['isSpam'] = strToJson(post_sql[9], True)
		post['isEdited'] = strToJson(post_sql[10], True)
		post['isDeleted'] = strToJson(post_sql[11], True)
		post['isHighlighted'] = strToJson(post_sql[12], True)
		post['isApproved'] = strToJson(post_sql[13], True)
		post_list.append(post)

	return post_list


def getThreadList(id="", title="", forum=""):
	if id != "":
		sql_where = "thread = {}".format(id)
	elif title != "":
		sql_where = "title = '{}'".format(title)
	elif forum != "":
		sql_where = "forum = '{}'".format(forum)
	else:
		print "VERY BAD ERROR IN getThreadList"
		return list()

	sql = """SELECT thread, title, user, message, forum, isDeleted, isClosed, date, \
		slug, likes, dislikes, points FROM Thread WHERE {};""".format(sql_where)

	db = MyDatabase()
	thread_list_sql = db.execute(sql)
	if not thread_list_sql:
		return list()

	thread_list = list()
	for thread_sql in thread_list_sql:
		thread = dict()
		thread['thread'] = strToJson(thread_sql[0])
		thread['title'] = strToJson(thread_sql[1])
		thread['user'] = strToJson(thread_sql[2])
		thread['message'] = strToJson(thread_sql[3])
		thread['forum'] = strToJson(thread_sql[4])
		thread['isDeleted'] = strToJson(thread_sql[5], True)
		thread['isClosed'] = strToJson(thread_sql[6], True)
		date = thread_sql[7].strftime('%Y-%m-%d %H:%M:%S')
		thread['date'] = strToJson(date)
		thread['slug'] = strToJson(thread_sql[8])
		thread['likes'] = strToJson(thread_sql[9])
		thread['dislikes'] = strToJson(thread_sql[10])
		thread['points'] = strToJson(thread_sql[11])

		thread_list.append(thread)

	return thread_list


def getUserDict(email):
	sql = """SELECT user, email, name, username, isAnonymous, about FROM User \
		WHERE email = %s;"""
	args = (email)
	db = MyDatabase()
	user_list_sql = db.execute(sql, args)
	if not user_list_sql:
		return dict()
	if not user_list_sql[0]:
		return dict()

	user_sql = user_list_sql[0]
	
	user = dict()
	user["id"] = strToJson(user_sql[0])
	user["email"] = strToJson(user_sql[1])
	user["name"] = strToJson(user_sql[2])
	user["username"] = strToJson(user_sql[3])
	user["isAnonymous"] = strToJson(user_sql[4], True)
	user["about"] = strToJson(user_sql[5])

	return user