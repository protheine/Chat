from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
# from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model

class users(Model):
	is_active = columns.Boolean()
	is_admin = columns.Boolean()
	_id = columns.Text()
	email = columns.Text(primary_key=True)
	password = columns.Text()
	name = columns.Text()
	created_at = columns.DateTime()
	last_login = columns.DateTime()
	updated_at = columns.DateTime()



connection.setup(['192.168.0.95'], "users", protocol_version=3) #TODO: put at least the server ip in a separate config file