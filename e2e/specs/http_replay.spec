# HTTP Replay Server

This specification verifies that the HTTP replay server returns recorded responses from a Cassette.

## Returns recorded response for a matching GET request

* Create a GET cassette for "/api/data" with status "200" and body "hello"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data"
* Verify that the response status code is "200"
* Verify that the response body is "hello"

## Returns 500 for a request not in the Cassette

* Create a GET cassette for "/api/data" with status "200" and body "hello"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/unknown"
* Verify that the response status code is "500"

## Matches query string as part of request target

* Create a GET cassette for "/api/data?kind=user" with status "200" and body "hello-query"
* Create a replay broker with the cassette
* Create an HTTP adapter with the broker
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data?kind=user"
* Verify that the response status code is "200"
* Verify that the response body is "hello-query"

___
* Stop the adapter if running
