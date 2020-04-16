# Cybersafe

*A digital safe to contain sensitive data*

By Timothé ALBOUY, Arnaud PERNET, Youssef EL HOR, Gwenn QUELO

## Requirements

To use Cybersafe, you'll need Docker and docker-compose:
- https://docs.docker.com/get-docker/
- https://docs.docker.com/compose/install/

## Build

To launch the services, enter `docker-compose up --build --force-recreate`.

Then you can access the different services at these addresses:
- Users API: http://0.0.0.0:5500
- Safe API: http://0.0.0.0:5501
- Token dealer: http://0.0.0.0:5502
- Back-office: http://0.0.0.0:5503

## Application architecture

### Back-office

The back-office is the front-end consumer of the Users and Safe REST APIs. Using it, you can register, login, create and retrieve protected resources.

The back-office was made using Flask, and the requests are made server-side, so it means that the JWT are stored in the session variables and not in the localStorage of the browser or the store of a front-end framework. It is not really a security improvement, but it eased the development.

### Asynchronism

When the token dealer is down, we don't want the whole application to fail. When a REST API sends a request to the token dealer and doesn't receive a reply back, it sends to the client an error message but retries the request again until the token dealer responds. Once the response has been received, the given credentials are stored in a whitelist in the API so that we don't have to send a request to the token dealer again.

But there is a problem with this approach: if we send a signing request and receive back a JWT that we store in a whitelist with its associated username, then the same token is issued to the client even after its expiration date. The opposite problem applies for the verifying requests, if we store the JWT in a whitelist, then the token can be replayed after its expiration date. To tackle that, we had to verify API-side that the JWT has not expired using the `exp` claim.

### Networking

In order to isolate properly each service, we created 3 networks in the `docker-compose.yml` file:
- frontend-n,
- token-n,
- database-n

### Documentation

You can access the Swagger documentation for the User and Safe APIs at the `/apidocs` URL.
