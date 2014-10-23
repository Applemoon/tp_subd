MYSQL_DUPLICATE_ENTITY_ERROR = 1062


def strToJson(value, isBool=False):
	if isBool:
		return (value != 0)

	if value == "None":
		return None

	return value
		