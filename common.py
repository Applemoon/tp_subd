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