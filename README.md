### Check sites selling second-hand goods

Application for checking various sites for specific listings of goods (e.g. check Yahoo! Auctions and Jimoty for 'Bicycle Panniers')

### Run the application
_Note: This will change soon._

From the project root:
```bash
cd src/main
python main.py
```


### Run tests
#### Unit tests
From the project root:
```bash
cd src
python -m unittest discover -s test/unit
```

#### Integration tests
From the project root:
```bash
cd src
python -m unittest discover -s test/integration
```

### Notes on files

- `.env` - Default environment variables for docker-compose.