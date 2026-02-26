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

## Raises an error when record mode is used without a live responder

* Verify that creating an adapter from cassette file "e2e/fixtures/simple_get.json" in "record" mode without a live responder raises an error

## Records a cassette to the store after a request in record mode

* Create a temporary cassette file
* Create an adapter from the temporary cassette file in "record" mode with a live responder
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data"
* Verify that the response status code is "200"
* Verify that the response body is "recorded response"
* Verify that the temporary cassette file contains "1" interaction

## Auto mode replays existing cassette and records missing interactions

* Create a temporary cassette file from "e2e/fixtures/simple_get.json"
* Create an adapter from the temporary cassette file in "auto" mode with a live responder
* Start the adapter on port "19876"
* Send a GET request to "http://localhost:19876/api/data"
* Verify that the response status code is "200"
* Verify that the response body is "hello from cassette"
* Send a GET request to "http://localhost:19876/api/other"
* Verify that the response status code is "200"
* Verify that the response body is "recorded response"
* Verify that the temporary cassette file contains "2" interactions

___
* Stop the adapter if running
