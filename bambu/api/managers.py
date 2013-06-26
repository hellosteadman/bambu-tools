from django.db.models import Manager

class TokenManager(Manager):
	"""
	Manager for the ``bambu.api.models.Task`` model.
	"""
	
	def create_token(self, app, token_type, timestamp, user = None):
		"""
		Create an OAuth token of a given time.
		
		::param app: The app to bind the token to
		::type app: ``bambu.api.models.App``
		
		::param token_type: The type of token to create, either 1 for a request token or 2 for an access token
		::type token_type: integer
		
		::param timestamp: The UNIX timestamp for the token
		::type timestamp: integer
		
		::param user: The user to attach the token to
		::type user: ``django.contrib.auth.models.User``
		
		::default user: None
		
		"""
		
		token, created = self.select_for_update().get_or_create(
			app = app, 
			token_type = token_type, 
			timestamp = timestamp,
			user = user
		)
		
		return token