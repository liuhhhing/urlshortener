# python urlshortener service
## Description
This is a service written in python and providing the URL shortening functionality. For example, when it is given a long URL like below (using HTTP POST request):

```http://google.com/this/is/what/i/want_to/be/shorten```

The service will return the shortened URL as of below (example):

```http://urlshortener.com/6y78crfg```

The response URL will be in the format: `http://<response URL prefix>/<shortened value with characters in [a-z][A-Z][0-9]>`
  
When the stored shortened URL is entered in the browser (HTTP GET Request), the service will redirect the browser to the original long URL that stored.

## How to run it
### Service
It is a python program (support both python version 2 and version 3) so it can be run in cross platform manner. Below describe how this can be run in Linux platform:

To run it, basically just do ```python ./runner.py``` then it will by default bind address '0.0.0.0' in the running host and occupy the port 5050 for listening the request, with the output like below:

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

It is supported to change the binding address and port using proccess arguments. Below are all the arguments (all of them are optional) that supported and its description, they are available from the `python ./runner.py --help`:

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

### Client - HTTP Based
#### Shorten Request
```
POST /shorten
```
> Body Parameter

```
[
    {
        "LongURL": "http://www.google.com/the/url/need/to/be/shortened"
    }
]
```

> Example Response

> 200 Response
```
[
    {
        "ShortenedURL":"http://myHost:5050/578yu21"
    }
]
```

The POST HTTP call can be triggered using some HTTP Rest API client like Postman or using curl command, below illustrate the behavior using curl:

```
$ curl -X POST -H "Content-Type: application/json" -d '[{"LongURL":"http://www.google.com"}]' http://192.168.1.15:5050/shorten
```

Now, we are going to shorten the http://www.google.com where the shortening service is running at 192.168.1.15 with port 5050, the return will be like:

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    92  100    55  100    37  11588   7796 --:--:-- --:--:-- --:--:-- 23000{"ShortenedURL":"http://192.168.1.15:5050/ef2d127"}
```

You can see the response is a JSON with key = "ShortenedURL" and the value = "http://192.168.1.15:5050/ef2d127", which is the shortened URL. The response URL prefix http://192.168.1.15:5050 can be specified by the argument `--responseUrlprefix`.


#### Redirection Request
```
GET /{hashed_value}
```

If we issue a GET request from curl using the shortened URL, it will be redirected to the long URL that we given above, to test it using curl, see below:

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

You can see from the curl response above it is returning the original long URL.

## Technical Notes
This python program is using the python web application "flask", for detail please read this link https://flask.palletsprojects.com/en/2.0.x/quickstart/

Basically the following modules implemented the logic:
```
runner.py
mappingStore.py
shortener.py
```

The idea of the program is to assign an unique id (specified in argument `--countRange`) to each incoming `POST /shorten` request, the unique id will be hashed using SHA256 and the first 7 characters (specified in argument `--firstN`) will be used as the shortened URL key.

The unique id is a range of integer that the program assigned to, it can be 1 to 10, 50 to 200 or 1 to sizeof(int), ... etc.

The reason of hashing the unqiue id instead of hashing the longURL is that, this can avoid the hash clash when the first 7 characters can be the same over some long URLs. Even though the hash of unique id can still be clashed (consider the hash of integer 'n' can clash the hash of integer 'm'), since it is controlled by the program it can be avoided by finding the next unique id from the range until no clash happens.

Another reason for using a range of id is that when we want to run the program as microservice, and when multiple of the instance is run, they can be assigned with different range of id so they won't be clashed. However, this needs another service to provide the range of id that is being "free-to-use" or "being-used" and get retrieved by the program (this can be specified by the argument `--tokenUrl`, but it is in to-be-implemented stage).

### runner.py
Basically it is the `main` of the program. With the help of flask, the API entry is provided in the way like below:

The POST API /shorten, in runner.py
```
@app.route("/shorten", methods=['POST'])
def shorten():
    if request.method == 'POST':
    ... (the shortening logic)
```

The GET API, in runner.py
```
@app.route('/<hashed_id>')
def redirect_to_link(hashed_id):
    ... (the redirection logic)
```

It will use the shortener.py and mappingStore.py to help doing the hashing, counter and mapping storage. To be brief, the runner.py will do:

> General
1. Do logging, the logging file can be specified by the `--loggerFilePath` and on each start of the program, the logging file name will be appended with the datetime %Y%m%d%H%M%S so the log of the previous run won't be lost.
2. Use flask to accept HTTP request and do response.
3. Store the mapping using sqlite3

> For POST /shorten
1. Check from the incoming `POST /shorten` request, the LongURL exists or not, using the **mappingStore.py**
2. If yes it will return the stored shortURL directly
3. If no, it will do the hashing, increment the counter, and store the new mapping, using **shortener.py**
4. If all counter used up and no clean hash can be found, it will return Error response of 400
5. If a clean hash can be located, it will return a success response of 200

> For Get /{hash_id}
1. Check from the incoming /{hash_id} GET request, the shortURL exists or not, using the **mappingStore.py**
2. If yes, it will redirect to the LongURL that stored
3. If no, it will return Error response of 400

### shortener.py
The shortener basically maintain a counter (specified by the argument `--countRange`) and do the hashing, to be brief, it will do:

1. Assign a unique id (over the given range) to the incoming LongURL request
2. Hash the unique id and check if the hashed id found duplicate, using **mappingStore.py**
3. If duplicate is found, just locate another unique id until the hash won't clash
4. If all the unique id are used up and still clash, return error
5. If the tokenUrl (specified by the argument `--tokenUrl`) is implemented, the step 4 above should go to retrieve another 'free-to-use' id range from the range assigner service rather than return error, unless the range assigner service is also failed.

### mappingStore.py
The mappingStore basically provide the interface to save and load the mapping data. The data are physically stored as a file and can be specified by the argument `--mappingStoreFile`. To be brief, it will do:

1. Provide read/write to the db using sqlite3
2. Provide hash search for duplicate check
3. Provide longURL search for existing check
4. Provide insertion of mapping (id, longUrl, hash)

## Future Work
There is a list of TODO for this work:

1. Support retreiving the range of free-to-use id from a service so it can be run in microservice manner
2. Check if the incoming LongURL request is a valid URL (at least the format is correct), rather than allowing them put a random text
3. Support HTTPS
4. Support Authentication optionally
5. Rather than using a range of id (say like 1 to 10) to hash, we should further 'encode' the id using a secret key before hashing. It will be safer from security point of view when the attacker can guess the hash value from 1, 2, 3, 4 ... and retreive the LongURL. URL Shortener to some extent is to hide the information from the actual Long URL, which could be public only to certain people. Consider when you want to share a photo from your own cloud and the URL is shortened and sent to only few invited people, you don't want someone can retrieve the LongURL from the shortner map.

