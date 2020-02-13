from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
# from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model

class users(Model):
	owner_name = columns.Text()
	address = columns.Text()
	city = columns.Text()
	country = columns.Text()
	email = columns.Text(primary_key=True)
	first_name = columns.Text()
	last_name = columns.Text()
	nickname = columns.Text()
	zip_code = columns.Text()



connection.setup(['192.168.0.97'], "users_infos", protocol_version=3) #TODO: put at least the server ip in a separate config file