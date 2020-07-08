db = {
    'user':'root',
    'password':'whdnjswns',
    'host':'python-backend-test.cjaocenjfsvh.ap-northeast-2.rds.amazonaws.com',
    'port':3306,
    'database':'miniter'
}
DB_URL = f"mysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"

test_db = {
    'user': 'root',
    'password': 'whdnjswns',
    'host': 'python-backend-test.cjaocenjfsvh.ap-northeast-2.rds.amazonaws.com',
    'port': 3306,
    'database': 'miniter'
}

test_config = {
    'DB_URL' : f"mysql://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}"
}