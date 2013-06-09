from django.utils.functional import update_wrapper

def anonymous(view):
	view._allow_anonymous = True
	return view