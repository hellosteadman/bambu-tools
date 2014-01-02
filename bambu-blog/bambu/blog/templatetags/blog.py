from django.template import Library
from django.db.models import Count
from django.core.exceptions import FieldError
from taggit import VERSION as TAGGIT_VERSION
from taggit.managers import TaggableManager
from taggit.models import TaggedItem, Tag

T_MAX = 6.0
T_MIN = 2.0

register = Library()

def get_weight_fun(t_min, t_max, f_min, f_max):
	def weight_fun(f_i, t_min = t_min, t_max = t_max, f_min = f_min, f_max = f_max):
		if f_max == f_min:
			mult_fac = 1.0
		else:
			mult_fac = float(t_max - t_min) / float(f_max - f_min)
			
		return int(t_max - (f_max - f_i) * mult_fac)
	return weight_fun

@register.inclusion_tag('blog/tag-cloud.inc.html')
def tag_cloud():
	try:
		queryset = Tag.objects.annotate(
			num_times = Count('taggeditem_items')
		)
	except FieldError:
		queryset = Tag.objects.annotate(
			num_times = Count('taggit_taggeditem_items')
		)
	
	num_times = queryset.values_list('num_times', flat = True)
	if(len(num_times) == 0):
		return {}
	
	weight_fun = get_weight_fun(T_MIN, T_MAX, min(num_times), max(num_times))
	queryset = queryset.order_by('name')
	
	for tag in queryset:
		tag.weight = weight_fun(tag.num_times)
	
	return {
		'tags': queryset
	}