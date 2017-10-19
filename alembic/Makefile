.PHONY: schema jenkinsschema


schema:
	alembic upgrade head


schema_acc:
	alembic --name acceptance upgrade head


schema_jenkins:
	./await_db.sh
	alembic -c alembic_jenkins.ini upgrade head
