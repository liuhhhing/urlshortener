# urlshortener
## Description
This is a service providing the URL shortening functionality. For example, when it is given a long URL like below:

```http://google.com/this/is/what/i/want_to/be/shortended```

Then, the service will return the shortened URL as of below (example):

```http://urlshortener.com/6y78crf```

The format will be: `http://<the service provider host name>/<shortened values with character [a-z][A-Z][0-9]>`
  
When the same shortened URL is entered in the browser, the service will direct the browser to the original long URL that stored.

## How to run it
It is a python program so it can be run in cross platform manner. Below describe how this can be run in Linux platform:

To run it, basically just do ```./runner.py``` then it will by default binding all the address of the running host and occupy the port 5050, with the output like below:

```
 * Serving Flask app "runner" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5050/ (Press CTRL+C to quit)
```

It means that it is binding all the address on the running host and occupying the port 5050 successfully.

It is supported to change the binding address and port using argument. Below are all the arguments (all of them are optional) that supported and its description:

```
optional arguments:
  -h, --help               show this help message and exit
  --port PORT              The port the service running at
  --ip IP                  The ip address to bind for running the service
  --urlprefix URL_PREFIX   The URL prefix return to the POST request
  --firstN FIRST_N         The first n characters from the hashed counter to form the shortened URL
  --tokenUrl TOKEN_URL     The URL to refresh the unique range of counter from when it is running in distributed manner
  --countRange COUNT_RANGE Hyphen separated range, for example 1-100, if it is not defined it will be default run from 1 to infinite

```

They will be further explained in the Technical Notes part.

## Technical Notes
