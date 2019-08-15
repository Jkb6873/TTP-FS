A simple Python + Flask + SQLAlchemy backend with a minimal javascript frontend. 

Work on replacing the frontend with one that uses React + Redux and adding a proper start up script has begun, but is on hold for now. 

Run using:
```
export FLASK_APP=application.py
python -m flask run
```

The project consists of 5 sections:
- Database
  - This section initializes SQLAlchemy, and creates models to define how Users and Transactions look. 
  - The Users table stores contact info, a salted hash for logging in, and funds that a user can spend. A User is created with a default of $5000.
  - The Transactions table stores each buying and selling event, which is aggregated when the user wants to view which stocks they currently have.
  - Total current stocks are not stored, because the frontend will require both a history of transactions and a current inventory of stocks owned. Since both are rendered on the same page, I decided to have the latter generated on demand. 
- Routes
  - This section contains all the routes available by the API.
  - The routes /buy, /sell, and /transactions all have the @validate_login wrapper, which requires a JWT cookie to be in the flask session. 
  - If the JWT cookie does not exist, the decorator routes the user to a log in page. 
  - This decorator inserts the user ID into each route's parameters, so the user cannot manually supply a user ID, it can only be done via first using the /login route.
  - /
    - GET request
    - Requires a JWT cookie.
    - Requires no parameters.
    - Serves the home page template. 
  - /buy 
    - POST request
    - Requires a JWT cookie.
    - Requires a string symbol, and an optional numeric count for number of purchased stocks. 
    - Returns a response with error code 400 on invalid input, and code 200 along with current balance on success.
  - /sell 
    - POST request
    - Requires a JWT cookie.
    - Requires a string symbol, and an optional numeric count for number of sold stocks.
    - Returns a response with error code 400 on invalid input, and code 200 along with current balance on success.
  - /transactions
    - GET request
    - Requires a JWT cookie.
    - Requires no parameters. 
    - Returns a JSON object of all transactions a user made.
  - /login
    - POST request
    - Requires a string email, and a string password. 
    - Returns an error code of 403 on invalid credentials. Otherwise, puts a JWT token in the user's session.
  - /logout
    - GET request
    - Requires no parameters.
    - Clears the session of all cookies, including the JWT.
    - Returns a 200, and redirects to a log in page. 
  - /register
    - POST request
    - Requires a string name, string email, and a string password
    - Returns an error code of 400 on incorrect input, otherwise creates a new user and grants a new JWT.
- Static
  - Basic CSS and JS. Will be improved upon eventually. 
  - Basic features are a Chart.js pie chart and a list of transactions. Very barebones. 
- Templates
  - Basic Jinja templates served by the routes. 
- Config and Utils
  - config.py grabs all the engironmental variables required for this project.
  - Utils.py implements:
    - A JSON encoder that lets us return transactions in a clean format. 
    - The @validate_login wrapper, which checks for a JWT cookie, then passes the user to the route they requested with their ID as an additional parameter, or to a login page if the JWT is invalid.
    - A function for storing the JWT in the user's session
    - A function that checks the JWT.
