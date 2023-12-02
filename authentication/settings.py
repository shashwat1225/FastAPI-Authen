from kavenegar import KavenegarAPI
from decouple import config

kavenegarSMSApi = KavenegarAPI(config('KAVENEGAR_API_KEY'))