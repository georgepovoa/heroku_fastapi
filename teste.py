teste = {
        "usuario": "user",
        "questoes_feitas":[1,2,3],
        "alteracoes":{ 
            "1":{
                "obs" : "",
                "aqr":[],
                "quest":[
                    {
                        "id_q":1,
                        "correcao":"tem correcao",
                        "anexos":"url",
                    }
                ]

            }
        }
            }

if "3" in teste["alteracoes"]:
    print(teste["alteracoes"]["1"]["quest"])
else:
    teste["alteracoes"]["3"] = {
                "obs" : "",
                "aqr":[],
                "quest":[
                    {
                        "id_q":2,
                        "correcao":"tem correcao",
                        "anexos":"url",
                    }
                ]

            }


print(teste)