class Feature:
	switch = False
	verbose_name = None
	description = u''
	upgrade_cta = None
	
	def test(self, user, **kwargs):
		return self.switch and False or 0