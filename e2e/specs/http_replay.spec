# HTTP Replay Server

This specification verifies that the HTTP replay server returns recorded responses from a Cassette.

## Returns recorded response for a matching GET request

* Create a cassette for "GET" method on "/api/data" with request body "" and status "200" and response body "hello"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data"
* Verify that the response status code is "200"
* Verify that the response body is "hello"

## Returns 500 for a request not in the Cassette

* Create a cassette for "GET" method on "/api/data" with request body "" and status "200" and response body "hello"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/unknown"
* Verify that the response status code is "500"

## Matches query string as part of request target

* Create a cassette for "GET" method on "/api/data?kind=user" with request body "" and status "200" and response body "hello-query"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data?kind=user"
* Verify that the response status code is "200"
* Verify that the response body is "hello-query"

## Returns recorded response for a matching POST request with body

* Create a cassette for "POST" method on "/api/data" with request body "req-body" and status "201" and response body "created"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a POST request to "http://localhost:19876/api/data" with body "req-body"
* Verify that the response status code is "201"
* Verify that the response body is "created"

## Returns recorded response for a matching PUT request

* Create a cassette for "PUT" method on "/api/items/1" with request body "update-data" and status "200" and response body "updated"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a PUT request to "http://localhost:19876/api/items/1" with body "update-data"
* Verify that the response status code is "200"
* Verify that the response body is "updated"

## Returns recorded response for a matching PATCH request

* Create a cassette for "PATCH" method on "/api/items/1" with request body "patch-data" and status "200" and response body "patched"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a PATCH request to "http://localhost:19876/api/items/1" with body "patch-data"
* Verify that the response status code is "200"
* Verify that the response body is "patched"

## Returns recorded response for a matching DELETE request

* Create a cassette for "DELETE" method on "/api/items/1" with request body "" and status "204" and response body ""
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a DELETE request to "http://localhost:19876/api/items/1"
* Verify that the response status code is "204"

## Returns recorded response for a matching HEAD request

* Create a cassette for "HEAD" method on "/api/health" with request body "" and status "200" and response body ""
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a HEAD request to "http://localhost:19876/api/health"
* Verify that the response status code is "200"

## Returns recorded response for a matching OPTIONS request

* Create a cassette for "OPTIONS" method on "/api/data" with request body "" and status "204" and response body ""
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send an OPTIONS request to "http://localhost:19876/api/data"
* Verify that the response status code is "204"

___
* Stop the adapter if running
