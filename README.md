# Price Merger

A web-scraper paired with a price history combination algorithm, that allows to analyse shared price changes across a list of products.

### Algorithm structure:
- Collect a list of https://www.e-katalog.ru/ product URLs using a search query or a target url
- Parse the price history data from product pages using the URLs list
- Convert price data into relative units using the formula: (current / average) * 100%
- Average out all the graphs with each other  

### How to setup?
- Download the chrome driver matching your chrome version from: https://chromedriver.storage.googleapis.com/index.html
- Configure the program in default.env
- Rename default.env to .env, done.