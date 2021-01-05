from flask import Flask



# insantiating Flask class object in variable "app" 
app = Flask(__name__)



@app.route('/')
def index():
    return "Hello BSDK Flask chal raha h"












app.run()
