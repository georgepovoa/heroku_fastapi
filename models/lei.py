from typing import List
from pydantic import BaseModel

class Titulo(BaseModel):
    _id:int
    texto:str
    tipo:str
    subordinado:list
    

class Alteracoes(BaseModel):
    _id:int
    usuario : str
    id_questões_feitas:list
    alteracoes : List[dict] = []

# {
#     id_questões_feitas:[1,2], #esses ids aglutinam as informações espalhadas pelos campos questões no resto do banco
#     alterações[
#     {     id_lei:0,
#          observações: “obs para apracer na lei”,
#            arquivos_vinculados: [arquivo1, arquivo2],
#         questões[
#         {    id_questão:1
#             correção: “correção”
#             anexos:arquivo1
#         } ,          

#         {    id_questão:2  #sem corerção pq a questão está certa
#         }           
#         ],
#     }
#     ]
