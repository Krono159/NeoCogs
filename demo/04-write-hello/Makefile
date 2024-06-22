
default:
	@echo -n '$$ '
	neocogs write-hello
	@echo -n '$$ '
	neocogs write-hello -o hello.txt
	@echo -n '$$ '
	cat hello.txt; rm hello.txt
	@echo -n '$$ '
	neocogs write-hello --output=hello.txt world
	@echo -n '$$ '
	cat hello.txt; rm hello.txt
	@echo -n '$$ '
	neocogs help write-hello

