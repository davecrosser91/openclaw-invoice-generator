run-db:
	docker run --name postgres_container -e POSTGRES_PASSWORD=mysecret -e POSTGRES_USER="Benedikt" -e POSTGRES_DB=postgres_db -d -v postgres_volume:/var/lib/postgresql/data -p 8005:5432 postgres
