from fastapi import FastAPI
import sys
print('TESTING check unittest:', 'unittest' in sys.modules)
print('TESTING check pytest:', 'pytest' in sys.modules)
app = FastAPI()
print('SYS ARGV:', sys.argv)
