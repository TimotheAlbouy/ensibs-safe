# Cybersafe

*A digital safe to contain sensitive data*

By Timothé ALBOUY, Arnaud PERNET, Youssef EL HOR, Gwenn QUELO

## Requirements

To use Cybersafe, you'll need docker and docker-compose:

- https://docs.docker.com/get-docker/
- https://docs.docker.com/compose/install/

## Build

To launch the services, enter `docker-compose up --build --force-recreate`.

The code of the front-end consumer of the 2 REST APIs is in the `back_office` module. On this back-office, you can register, login, create and retrieve resources. After launching, you can access it at this URL: `http://localhost:5003`.

You can access the Swagger documentation of both APIs at the `/apidocs` URL.

