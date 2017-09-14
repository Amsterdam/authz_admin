.PHONY: schema jenkinsschema


schema:
	alembic upgrade head


schema_acc:
	alembic --name acceptance upgrade head


schema_jenkins:
	alembic -c alembic_jenkins.ini upgrade head
