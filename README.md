# Price analyser

## Algorithm structure:
- Collect a list of https://www.e-katalog.ru/ product URLs using a search query
- Parse the price history data from product pages using the URLs list
- Convert price data into relative units using the formula: (current / average) * 100%
- Average out all the graphs with each other  

*Rename default.env to .env before working*