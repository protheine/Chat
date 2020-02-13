from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
# from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model

class users(Model):
	isactive = columns.Boolean()
	isadmin = columns.Boolean()
	_id = columns.Text()
	email = columns.Text(primary_key=True)
	password = columns.Text()
	name = columns.Text()
	createdat = columns.DateTime()
	lastlogin = columns.DateTime()
	updatedat = columns.DateTime()



connection.setup(['192.168.0.95'], "users", protocol_version=3) #TODO: put at least the server ip in a separate config file