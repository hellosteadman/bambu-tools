def remote_subscription_delete(sender, instance, **kwargs):
	if instance.remote_id:
		from bambu.payments import site
		
		gateway = site.get_gateway(instance.gateway)
		gateway.delete_subscription(instance.remote_id)

def remote_client_delete(sender, instance, **kwargs):
	if instance.remote_id:
		from bambu.payments import site
		
		gateway = site.get_gateway(instance.gateway)
		gateway.delete_client(instance.remote_id)