from pymongo import MongoClient

conn = MongoClient("mongodb+srv://georgepovoa12:asdasd12@cluster0.y0ias.mongodb.net/cluster0?retryWrites=true&w=majority")

db_cf88 = conn["CF88"]


lei = db_cf88["Lei"]

q_cf88 =  db_cf88["Questoes_Catalogadas"]

db_alt = conn["alteracoes"]


alteracoes = db_alt["usuarios"]

db_cadernos = conn["cadernos"]

cadernos = db_cadernos["usuarios"]