# TransactionTracker

To run the app first create your venv
```bash
python3 -m venv venv
```

Then activate your venv
```bash
. venv/bin/activate
```

Install the requirements
```bash
pip install -r dev_requirements.txt
```

Run the app
```bash
python3 appserver.py
```

You will need to configure the database in config.py if you don't
have mysql installed you can use sqlite or any database you like.
```python
...
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/database'
...
```
Then you're all set to start development!
