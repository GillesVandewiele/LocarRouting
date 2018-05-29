# Locar Routing

A python script that tries to find an optimal sequence of packages (with pickup- and delivery-locations) when driving from A to B. The sequence should be as long as possible, and the total distance should not exceed a `max_dist` parameter, which is set by the user.

## Setting up the routing API

The python script is wrapped in an API, with flask. In order to install all requirements, go to the `router` directory and run

`python3 -m pip install -r requirements.txt`

Afterwards, run 

`python3 api.py`

You should get a message in the form of ` * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`

## Front-end application

A demo application can be found in the `App/` directory. Just open `locar.html` in a modern browser (Chrome, Chromium, Firefox, ...)