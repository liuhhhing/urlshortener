# urlshortener
## Description
This is a service providing the URL shortening functionality. For example, when it is given a long URL like below (using HTTP POST request):

```http://google.com/this/is/what/i/want_to/be/shorten```

The service will return the shortened URL as of below (example):

```http://urlshortener.com/6y78crfg```

The format will be: `http://<response URL prefix>/<shortened value with characters in [a-z][A-Z][0-9]>`
  
When the same shortened URL is entered in the browser (HTTP GET Request), the service will redirect the browser to the original long URL that stored.

## How to run it
It is a python program (support both python version 2 and version 3) so it can be run in cross platform manner. Below describe how this can be run in Linux platform:

To run it, basically just do ```python ./runner.py``` then it will by default binding all the address from sock.gethostname() of the running host and occupy the port 5050 for listening the request, with the output like below:

```
05-Dec-21 09:11:39 - INFO - Running The Shortener service
05-Dec-21 09:11:39 - INFO - Start the service
 * Serving Flask app 'runner' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
05-Dec-21 09:11:39 - WARNING -  * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
05-Dec-21 09:11:39 - INFO -  * Running on http://192.168.1.15:5050/ (Press CTRL+C to quit)
```

It is supported to change the binding address and port using argument. Below are all the arguments (all of them are optional) that supported and its description:

```
optional arguments:
  -h, --help            show this help message and exit
  --port PORT           The port the service running at
  --ip IP               The ip address to bind for running the service
  --responseUrlprefix RESPONSE_URL_PREFIX
                        The response URL prefix return to the POST request in
                        the format of http://www.myDesiredDomain/,when it is
                        not defined it will be defaulted to system hostname
                        and port like http://www.myHost.com:5050/
  --firstN FIRST_N      The first n characters from the hashed counter to form
                        the shortened URL
  --tokenUrl TOKEN_URL  The URL to get the range of available counter when it
                        is running in distributed manner (To-Be-Implemented)
  --countRange COUNT_RANGE
                        Hyphen separated range, for example 1-100, if it is
                        not defined it will be defaulted from 1 to sizeof(int)
  --mappingStoreFile MAPPING_STORE_FILE
                        The file path that the mapping file saved to, if it is
                        not defined it will be defaulted to be the current
                        running directory and named as mapping.sqlite
  --loggerFilePath LOGGER_FILE_PATH
                        The logger file path, if it is not specified, the log
                        will be outputted to consoleNotice the log file name
                        will be appended with the "_YYYYMMDDhhmmss" so on
                        every run the previous log will not be overwritten
```

When it run, it can be tested using some HTTP Rest API client like Postman or using curl command, below illustrate the behavior using curl:

```
$ curl -X POST -H "Content-Type: application/json" -d '[{"LongURL":"http://www.google.com"}]' http://192.168.1.15:5050/shorten
```

Now, we are going to shorten the http://www.google.com where the shortening service is running at 192.168.1.15 with port 5050, the return will be like:

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    92  100    55  100    37  11588   7796 --:--:-- --:--:-- --:--:-- 23000{"ShortenedURL":"http://192.168.1.15:5050/ef2d127"}
```

You can see the response is a JSON with key = "ShortenedURL" and the value = "http://192.168.1.15:5050/ef2d127", which is the shortened URL.

If we issue a GET request from curl using the shortened URL, it will be redirected to the long URL that we given above:

```
curl http://192.168.1.15:5050/ef2d127
```

It will return:

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   248  100   248    0     0  54469      0 --:--:-- --:--:-- --:--:-- 82666<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to target URL: <a href="http://www.google.com">http://www.google.com</a>. If not click the link.
```

## Technical Notes

