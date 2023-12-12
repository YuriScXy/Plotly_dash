import getpass
import oracledb
import pandas as pd


def consulta(dataIni="'01/11/2023'",dataFinal="'30/11/2023'"):
    oracledb.init_oracle_client()
    
    un = "jiva"
    cs = "exclusiva.duckdns.org:18012/orcl"
    pw = "tecsis"
    codemp =  []
    vlr = []
    dtvenc = []
    dhbaixa = []
    pendente = []
    provisao = []
    tipo = []
    
    consultaSql = f"""SELECT * FROM (SELECT * FROM (SELECT dtvenc, codemp, sum(vlrdesdob) AS VLRDESDOB , PENDENTE,PROVISAO , 'DESPESA' AS TIPO FROM VW_002_DESPESAS WHERE trunc(DTVENC) > '01/01/2022' group by dtvenc,pendente,provisao,codemp) UNION ALL SELECT * FROM (SELECT dtvenc,codemp, sum(vlrdesdob) AS VLRDESDOB, PENDENTE,PROVISAO , 'RECEITAS' AS TIPO FROM VW_001_RECEITAS WHERE trunc(DTVENC) > '01/01/2022' group by dtvenc,pendente,provisao,codemp))"""
    
    with oracledb.connect(user=un, password=pw, dsn=cs, encoding='UTF-8') as connection:
        with connection.cursor() as cursor:
            sql = f"{consultaSql}"
            cursor.execute(sql)
            results = cursor.fetchall()
            
    
    for r in results:
        dtvenc.append(r[0])
        codemp.append(r[1])
        vlr.append(r[2])
        pendente.append(r[3])
        provisao.append(r[4])
        tipo.append(r[5])
        

    
    df = pd.DataFrame({
        "data" : dtvenc,
        "Empresa" : codemp,
        "Valor" : vlr,
        "status" : pendente,
        "provisao" : provisao,
        "tipo" :tipo
    })
    df['Valor']= round(df["Valor"],2)
   
    return df     

