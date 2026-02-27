# HTTP replay adapter factory tests

This specification verifies that the HTTP adapter can be created from a Cassette file using the factory method.

## Creates an adapter from a cassette file and replays a GET request

* Create an adapter from cassette file "e2e/fixtures/simple_get.json"
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data"
* Verify that the response status code is "200"
* Verify that the response body is "hello from cassette"

## Raises an error when the cassette file does not exist

* Verify that creating an adapter from cassette file "e2e/fixtures/nonexistent.json" raises an error

## Raises an error when the cassette file contains invalid JSON

* Verify that creating an adapter from cassette file "e2e/fixtures/invalid.json" raises an error

___
* Stop the adapter if running
