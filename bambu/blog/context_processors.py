from bambu.blog.models import Post

def latest(request):
	return {
		'latest_blog_posts': Post.objects.live
	}