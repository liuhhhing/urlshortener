# urlshortener
## Description
This is a service providing the URL shortening functionality. For example, when it is given a long URL like below:

```http://google.com/this/is/what/i/want_to/be/shortended```

Then, the service will return the shortened URL as of below (example):

```http://urlshortener.com/6y78crf```

The format will be: `http://<the service provider host name>/<shortened values with character [a-z][A-Z][0-9]>`
  
When the same shortened URL is entered in the browser, the service will direct the browser to the original long URL that stored.

## How to run it
It is a python program so it can be run in cross platform manner. Below descript how this can be run in Linux platform:

To run it, basically just do ```./runner.py``` then it will by default binding all the address of the running host and occupy the port 5050, with the output like below:

```

```

## Technical Notes
