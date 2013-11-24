def anonymous(view):
	view._allow_anonymous = True
	return view