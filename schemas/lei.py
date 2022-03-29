def tituloEntity(item)-> dict:
    return{
        "_id":item["_id"],
        "tipo":str(item["tipo"]),
        "texto":item["texto"],
        "subordinado":item["subordinado"]
    }

def titulosEntity(entity) ->list:
    return[tituloEntity(item) for item in entity]


def testeEntity(item)-> dict:
    return{
        "_id":item["_id"],
        "teste":item["teste"]
    }

def testesEntity(entity) ->list:
    return[testeEntity(item) for item in entity]