import base64
import json
import os
import io
from io import BytesIO
from typing import List, Optional

import boto3
from config.db import alteracoes, cadernos, conn, db_alt, db_cf88, lei, q_cf88
from fastapi import APIRouter, File, Query, UploadFile
from matplotlib import image
from models.lei import Alteracoes, Titulo
from PIL import Image
from pydantic import BaseModel

AWS_S3_CREDS = {
    "aws_access_key_id":"AKIAVPGZOBLXZ5XCG7XN",
    "aws_secret_access_key": "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"
}
s3 = boto3.client('s3',**AWS_S3_CREDS)
app_routes = APIRouter()

class base64upload(BaseModel):
    base64_img:str
# APIS RELACIONADAS A LEI

@app_routes.get("/titulo" ,tags = ["lei"])
async def find_all_titulos():
# Aqui é para pegar toodos os títulos 
# para a primeira apresentação da lei ou criação de cadernos
    t = lei.find({"tipo":"título"})
    return list(t)


@app_routes.get('/lista/{lista_id}',tags = ["lei"])
# essa função é o começo de receber uma lista de parametros e 
# retnornar as leis dentro dessa lista  
async def find_list(item_ids:List[int]=Query([])):
    ids = []
    for item in lei.find({"_id" : {"$in": item_ids}}):
        ids.append(item)
    
    return ids

@app_routes.get('/lei/caderno/todos',tags = ["lei"])

async def find_all_titulos():
    tipos = ["título","capitulo","secao","subsecao"]
    superiores = lei.find({"tipo" : {"$in": tipos}})

    return list(superiores)

@app_routes.get('/lei/{item_id}',tags = ["lei"])
# Essa função retorna a lei de acordo com o id
# Necessário adicionar um path antes, pq quando existe 
# typo ele retorna para cá
async def find_all_titulos(item_id:int):
    a = lei.find({"_id":item_id})

    return list(a)

# APIS RELACIONADAS A LEI

# API RELACIONADA A USUARIOS

@app_routes.post('/createuser',tags = ["user"])
async def create_user(user:str):
#aqui a gente cria um campo de usuário para salvar as 
# alterações feitas durante a resolução de questão e etc
    user = user.lower()
    if alteracoes.find_one({"_id":user}) == {}:
        new_user = {
            "_id": user,
            "questoes_feitas":[],
            "alteracoes":{  
            }
                }
        alteracoes.insert_one(new_user)
        return new_user
    return "usuario já existente"

@app_routes.get("/users" ,tags = ["user"])   
# uma função simplesmente para pegar todos os usuários que já possuem 
# um campo de alterações já criados
async def get_users():
    users = alteracoes.find({})
    
    return list(users)

@app_routes.get("/get_all_q_user/{user}" ,tags = ["user"])
async def get_user_questoes(user:str):
    user = alteracoes.find_one({"_id":user})

    id_lei_list = list(user["alteracoes"].keys())
    id_lei_list = list(map(int, id_lei_list))
    
    
    return id_lei_list

@app_routes.get("/user/{user}" ,tags = ["user"])   
# uma função simplesmente para pegar todos os usuários que já possuem 
# um campo de alterações já criados
async def get_user(user:str):
    users = alteracoes.find_one({"_id":user})
    
    return users

# API RELACIONADA A USUARIOS

# API RELACIONADA A CADERNOS
@app_routes.get("/cadernos/{user}",tags = ["cadernos"])
# essa função recebe um usuário e retorna os cadernos referentes a ele
async def get_cadernos(user:str):
    return cadernos.find_one({"_id":user})


@app_routes.post("/cadernos",tags = ["cadernos"])
# Adicionar Imagem
async def post_cadernos(user:str):
    dict_to_caderno = {"_id":user,
    "cadernos":{},
    "caderno_ativo":"",
    "ultimo_caderno":""
}
    cadernos.insert_one(dict_to_caderno)
    return dict_to_caderno

@app_routes.put("/cadernos",tags = ["cadernos"])

# Aqui foi a criação de um caderno base para não teste
async def put_cadernos(user:str,id:int,nome_caderno:str,indice_lei :list,bancas:list,cargos:list):
    ids = indice_lei
    # listas que precisam vir do front

    lista_id_sim_front = ids
    lista_pais = []
    lista_final = []
    so_ids_filhos = []

    ids_sub = lei.find({"$or":[{"sub_titulo":{"$in": ids}},{"sub_capitulo":{"$in": ids}},
    {"sub_sec":{"$in": ids}},{"sub_subsecao":{"$in": ids}},{"sub_artigo":{"$in": ids}},
    {"sub_niv2":{"$in": ids}},{"sub_niv3":{"$in": ids}}]})

    ids_sub = list(ids_sub)

    for i in ids_sub:
        if "sub_subsecao" in i:

           lista_pais.append(i["sub_subsecao"])
        elif "sub_sec" in i:
           lista_pais.append(i["sub_sec"])
        elif "sub_capitulo" in i:
           lista_pais.append(i["sub_capitulo"])
        elif "sub_titulo" in i:
           lista_pais.append(i["sub_titulo"])    
    
    lista_pais = list(set(lista_pais))
    
    for i in ids_sub:
        so_ids_filhos.append(i["_id"])


    lista_final = so_ids_filhos + lista_pais
    lista_final = [i for n, i in enumerate(lista_final) if i not in lista_final[n + 1:]]

    # PRA CIMA É A LOGICA PARA PEGAR TODOS OS IDS FILHOS

    minha_busca = {"_id" : user }

    dicta = cadernos.find_one({"_id":user})

    dicta["cadernos"][str(id)] = {"nome_caderno":nome_caderno,
            "indices_lei":lista_final,
            "bancas":bancas,
            "cargos":cargos}
    

    newvalues = { "$set": {"cadernos": dicta["cadernos"]}}

    cadernos.update_one(minha_busca, newvalues)

    return dicta

@app_routes.get('/teste/caderno/lista_filhos/',tags = ["cadernos"])
async def pegar_filhos(ids:list[int]= Query([])):
    # listas que precisam vir do front

    
    lista_pais = []
    lista_final = []
    so_ids_filhos = []

    ids_sub = lei.find({"$or":[{"sub_titulo":{"$in": ids}},{"sub_capitulo":{"$in": ids}},
    {"sub_sec":{"$in": ids}},{"sub_subsecao":{"$in": ids}},{"sub_artigo":{"$in": ids}},
    {"sub_niv2":{"$in": ids}},{"sub_niv3":{"$in": ids}}]})

    ids_sub = list(ids_sub)

    for i in ids_sub:
        if "sub_subsecao" in i:

           lista_pais.append(i["sub_subsecao"])
        if "sub_sec" in i:
           lista_pais.append(i["sub_sec"])
        if "sub_capitulo" in i:
           lista_pais.append(i["sub_capitulo"])
        if "sub_titulo" in i:
           lista_pais.append(i["sub_titulo"])    
    
    lista_pais = list(set(lista_pais))
    
    for i in ids_sub:
        so_ids_filhos.append(i["_id"])


    lista_final = so_ids_filhos + lista_pais
    lista_final = [i for n, i in enumerate(lista_final) if i not in lista_final[n + 1:]]


    
    return lista_final

@app_routes.get('/cadernos/lista_filhos/react/',tags = ["cadernos"])
async def pegar_filhos(tipo : str,ids_para_react:list[int]= Query([])):
    # listas que precisam vir do front


    lista_pais = []
    lista_final = []
    so_ids_filhos = []

    # ids_sub = lei.find({"$or":[{"sub_titulo":{"$in": ids_para_react}},{"sub_capitulo":{"$in": ids_para_react}},
    # {"sub_sec":{"$in": ids_para_react}},{"sub_subsecao":{"$in": ids_para_react}}]})

    ids_sub = lei.find({
        "$and":[
            {"$or":
            [{"sub_titulo":{"$in": ids_para_react}},{"sub_capitulo":{"$in": ids_para_react}},
            {"sub_sec":{"$in": ids_para_react}},{"sub_subsecao":{"$in": ids_para_react}}
    ]},
    {"tipo":tipo}]
    })

   
    lista_final = list(ids_sub)
    
    return lista_final

@app_routes.get('/lista/createcaderno/{lista_id}',tags = ["cadernos"])
# essa função é o começo de receber uma lista de parametros e 
# retnornar as leis dentro dessa lista  
async def find_list(item_ids:List[int]=Query([])):
    ids = []
    tipos = ["título","capitulo","secao","subsecao"]


    for item in lei.find({"$and":[{"_id" : {"$in": item_ids}},{"tipo":{"$in":tipos}}]}):
        ids.append(item)
    return ids

# CRIAR PUT DE CADERNO_ATIVO
@app_routes.put("/cad/definir_atual",tags = ["cadernos"])
async def selecionar_caderno(user:str,caderno_id:int):
    minha_busca = {"_id" : user }
    
    newvalues = { "$set": { "caderno_ativo":caderno_id} }

    cadernos.update_one(minha_busca, newvalues)

    return "ok"


# API RELACIONADA A CADERNOS

# API RELACIONADA A QUESTOES

@app_routes.put('/adicionarquestao',tags = ["Questao"])
# mudar campo ateracoes para id_lei
# colocar obs para cada questao 
# mudar os 2 anexos para uma lista
# Essa função recebe um usuário e adiciona uma questão

async def adicionar_questao(user : str , id_questao:int, id_lei:int,correcao:Optional[str] = ""):
    minha_busca = {"_id" : user }

    dicta = alteracoes.find_one({"_id":user})
    dicta["questoes_feitas"].append(id_questao)
    if str(id_lei) in dicta["alteracoes"]:
        dicta["alteracoes"][str(id_lei)]["questoes"].append({"id_q": id_questao,"correcao":correcao,"anexo":""})
    else:
        dicta["alteracoes"][str(id_lei)] = {"obs":"","anexos":"","questoes":[{"id_q":id_questao,"correcao":correcao,"anexos":""}]}

    newvalues = { "$set": { "questoes_feitas": dicta["questoes_feitas"],
                            "alteracoes":dicta["alteracoes"]
     } }

    alteracoes.update_one(minha_busca, newvalues)

    return dicta

@app_routes.get("/get_q_individual/{user}/questao/{id_lei}",tags = ["Questao"])
async def get_questao_individual(user:str,id_lei:int):
    user = alteracoes.find_one({"_id":user})

    alteracoes_lei = user["alteracoes"][str(id_lei)]["questoes"]
    
    
    return alteracoes_lei


@app_routes.get("/questoes/cf88/uma",tags = ["Questao"])
async def read_items(q: Optional[List[int]] = Query([None]),q_c: Optional[List[int]] = Query(None)):
    print(q)
    if q == None:
        q = []
    
    q_com_c = q_cf88.find_one({"$and":[{"_id" : {"$nin": q}},{"id_lei":{"$in":q_c}}]})

    if q_com_c == None:
        q =  q_cf88.find_one({"_id" : {"$nin": q}})
        print("SEM LEI AGREGADA")
    else:
        q = q_com_c
        print("COM LEI AGREGADA")
    
    return q

@app_routes.get("/questoes/cf88",tags = ["Questao"])
#retorna as questões referentes a CF88
async def get_q_cf88():
    questoes = q_cf88.find()
    questoes= list(questoes)
    
    return questoes

# API RELACIONADA A QUESTOES


@app_routes.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app_routes.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

@app_routes.post("/base64ToS3")
async def create_upload_file(upload_base64:base64upload):
    imagem_url = upload_base64.base64_img
    format, imgstr = imagem_url.split(';base64,') 
    im = Image.open(BytesIO(base64.b64decode(imgstr)))

    in_mem_file = io.BytesIO()
    im.save(in_mem_file, format=im.format)
    in_mem_file.seek(0)
    bucket = 'startup-bucket-xuxu'
    file_name = im
    key_name = 'TESTE FASTAPI2.JPEG'
    s3.upload_fileobj(
    in_mem_file, # This is what i am trying to upload
    bucket,
    key_name,

)
    url= 'https://%s.s3.amazonaws.com/%s' % (bucket, key_name)

    a = {
        "usuario" :"",
        "tipo_anexo":"",
        "url_do_anexo":"",
        "endereco":"",
    }


    
    
    return "OK"



