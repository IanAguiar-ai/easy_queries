import openai
import pandas as pd
import sqlite3
import openpyxl

def pass_to_sql(dataframe, name:str = "main_table"):
    db_connection = sqlite3.connect("sales.db")
    dataframe.to_sql(name, db_connection, if_exists = "replace", index=False)
    print(f'Dados limpos exportados para a tabela "{name}" no banco de dados SQLite.')
    
    return db_connection

def request(text:str, key:str, db_global):
    openai.api_key = key
    
    model_engine = "text-davinci-003"
    completion = openai.Completion.create(engine = model_engine,
                                                  prompt = text,
                                                  max_tokens = 100)
    #print(completion["choices"][0]["text"])
    
    t = completion["choices"][0]["text"]
    for_query = t.replace("\n"," ")

    cursor = db_global.cursor()   
    cursor.execute(for_query)
    result = cursor.fetchall()
    cursor.close()
    
    return completion, result

def to_excel(db:list, name = "temporario"):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    for row in db:
        sheet.append(row)

    workbook.save(f"{name}.xlsx")
    print(f"Arquivo Excel '{name}.xlsx' criado e salvo com sucesso.")

def main(path_excel, request, name_new_excel):
    df = pd.read_csv(path_excel)
    db_global = pass_to_sql(df)
    cod, temp_df = request("quero os horarios que mais vendem produtos")
    to_excel(temp_df, name_new_excel)
    db_global.close()
    return cod, temp_df
    
