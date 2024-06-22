
default:
	@echo -n '$$ '
	neocogs --default-name=world hello-with-configuration
	@echo -n '$$ '
	COGS_DEFAULT_NAME=world neocogs hello-with-configuration
	@echo -n '$$ '
	echo "default-name: world" >neocogs.conf
	@echo -n '$$ '
	neocogs hello-with-configuration
	@echo -n '$$ '
	rm neocogs.conf
	@echo -n '$$ '
	neocogs help default-name

