from modules.alpha import AlphaClass
from modules.beta import BetaClass
from modules.gamma import GammaClass
from flask import Flask, jsonify

flaskapp = Flask(__name__)

# Initialize classes
alpha_instance = AlphaClass()
beta_instance = BetaClass()
gamma_instance = GammaClass()

flaskapp.get("/random")


def random_number():
    return jsonify({"random_number": alpha_instance.random_number()})


@flaskapp.get("/randomchoice")
def random_choice():
    return jsonify({"random_choice": alpha_instance.random_choice()})
