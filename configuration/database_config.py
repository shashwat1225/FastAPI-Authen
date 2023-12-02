from decouple import config

db_config = {
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
    'host': config('DB_HOST'),
    'port': config('DB_PORT'),
    'db': config('DB_NAME'),
}