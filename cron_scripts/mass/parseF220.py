#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !DESCRIPTION:
#
# !CALLING SEQUENCE:
#
# !REVISION HISTORY: 
# 19 Ago 2021 - J. G. de Mattos - Initial Version
#
# !REMARKS:
#
#EOP
#-----------------------------------------------------------------------------#
#BOC
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.rrule import rrule, HOURLY
import argparse

import sqlite3
from sqlite3 import Error

def create_connection(fileDB):
    conn = None
    try:
        conn = sqlite3.connect(fileDB)
        print(f'Successfully connected to SQLite version {sqlite3.version}')
    except Error as e:
        print(e)

    return conn


def createTable(conn, nome_tabela, campos, chave_primaria, chave_unica=None):
    """
    Cria uma tabela SQLite com os campos e chaves fornecidos.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados SQLite.
        nome_tabela (str): Nome da tabela a ser criada.
        campos (list): Lista de tuplas, onde cada tupla representa um campo da tabela
            e contém o nome do campo e o tipo de dado (ex: [('nome', 'TEXT'), ('idade', 'INTEGER')]).
        chave_primaria (list): Lista de nomes dos campos que serão a chave primária da tabela.
        chave_unica (list): Lista de nomes dos campos que devem ser únicos na tabela. Opcional.

    Exemplo:
        conn = sqlite3.connect('exemplo.db')
        campos = [('date', 'DATETIME'), ('outer', 'INTEGER'), ('inner', 'INTEGER'),
                  ('cost', 'FLOAT'), ('grad', 'FLOAT'), ('step', 'FLOAT'),
                  ('b', 'FLOAT'), ('Jb', 'FLOAT'), ('Jo', 'FLOAT'),
                  ('Jc', 'FLOAT'), ('Jl', 'FLOAT')]
        chave_primaria = ['date', 'outer', 'inner']
        chave_unica = ['outer', 'inner', 'date']
        createTable(conn, 'tabela', campos, chave_primaria, chave_unica)

    """
    try:
        cursor = conn.cursor()
        
        # Monta a query SQL de criação da tabela
        query = f"CREATE TABLE IF NOT EXISTS {nome_tabela} ("
        for campo in campos:
            query += f"{campo[0]} {campo[1]} NOT NULL, "
        query += f"PRIMARY KEY ({', '.join(chave_primaria)})"
        if chave_unica:
            query += f", UNIQUE ({', '.join(chave_unica)})"
        query += ")"
        
        # Executa a query
        cursor.execute(query)
        print(f"Tabela '{nome_tabela}' criada com sucesso")
    except sqlite3.Error as e:
        print(f"Erro ao criar tabela '{nome_tabela}': {e}")


def upsert_data(conn, nome_tabela, df, chave_primaria):
    """
    Faz upsert (insert ou update) dos dados de um DataFrame em uma tabela SQLite.
    Os dados serão inseridos se não existirem ainda na tabela, ou atualizados caso já existam.
    
    Args:
        conn (sqlite3.Connection): Conexão com o banco de dados SQLite.
        nome_tabela (str): Nome da tabela onde os dados serão inseridos/atualizados.
        df (pandas.DataFrame): DataFrame do pandas contendo os dados a serem inseridos/atualizados.
        chave_primaria (list): Lista de nomes dos campos que são a chave primária da tabela.
    """
    try:
        cursor = conn.cursor()
        
        # Monta a query SQL de upsert
        campos = ', '.join(df.columns)
        valores = ', '.join(['?'] * len(df.columns))
        update = ', '.join([f"{col} = excluded.{col}" for col in df.columns if col not in chave_primaria])
        query = f"INSERT INTO {nome_tabela} ({campos}) VALUES ({valores}) ON CONFLICT ({', '.join(chave_primaria)}) DO UPDATE SET {update}"
        
        # Executa a query para cada linha do DataFrame
        for _, row in df.iterrows():
            cursor.execute(query, tuple(row))
        
        # Finaliza a transação
        conn.commit()
        print("Dados inseridos/atualizados com sucesso")
        
    except sqlite3.Error as e:
        print(f"Erro ao inserir/atualizar dados: {e}")


def create_field_list(*field_groups):
    field_types = ['DATETIME','INTEGER','FLOAT']
    fields = []
    for i,field_names in enumerate(field_groups):
       fields.extend([(field, field_types[i]) for field in field_names])
    return fields
    


def iter_time(labeli, labelf, incr):
    first_date = datetime.strptime(str(labeli),"%Y%m%d%H")
    last_date = datetime.strptime(str(labelf),"%Y%m%d%H")
    return rrule(HOURLY, interval=incr, dtstart=first_date, until=last_date)

        
dateParser = lambda x: datetime.strptime(x, '%Y%m%d%H')

##-----------------------------------------------------------------------#
## parse arguments from command line 
parser = argparse.ArgumentParser(prog='parseF220',description='Parse GSI diag file fort.220.')

parser.add_argument('-i', type=int, action='store', dest='LABELI',help='set initial time (YYYYMMDDHH)', required=True)
parser.add_argument('-f', type=int, dest='LABELF',help='set final time (YYYYMMDDHH)', required=True)
parser.add_argument('--incr', type=int, dest='incr',help='set increment hours (HH)', default=6)
parser.add_argument('--path', dest='path', help='set path where is the data',default='.')
parser.add_argument('--fout', dest='fileNameOut', help='set fileName where data will be save',default='costFile.db')

args = parser.parse_args()
#args = parser.parse_args(['-i','2023020100','-f','2023022818','--incr','6','--path','/lustre_xc50/joao_gerd/SMNA-Oper/SMG/datainout/gsi/dataout'])
##
##-----------------------------------------------------------------------#





costFile  = args.fileNameOut
costTable = 'costFunc'
consTable = 'costCons'

costFunc = {}
costCons = {}

fieldsFix  = ('date','hour','outer','inner')
fieldsCost = ('cost', 'grad', 'step', 'b', 'Jb', 'Jo', 'Jc', 'Jl', 'gnormx', 'gnormy', 'gnorm', 'reduction')
fieldsCons = ('mean_ps', 'mean_pw', 'pdryini', 'qneg', 'qsat')

if os.path.isfile(costFile):

   print(f'File {costFile} already exists. Additional data will be appended to the existing file.')
   conn = create_connection(costFile)
   df = pd.read_sql_query(f"select date from {costTable} order by date", conn, parse_dates=["date"])
   print(f'We will retrieve the latest date from the file {costFile}')
   date = df.iloc[-1].date
   date += timedelta(hours=6)
   args.LABELI=date.strftime("%Y%m%d%H")

else:

   conn = create_connection(costFile)

   campos = create_field_list(fieldsFix[0:1],fieldsFix[1:4],fieldsCost)

   chave_primaria = ['date', 'hour', 'outer', 'inner']
   chave_unica = ['outer', 'inner', 'hour', 'date']
   createTable(conn, costTable, campos, chave_primaria, chave_unica)
   
   
   campos = create_field_list(fieldsFix[0:1],fieldsFix[1:3],fieldsCons)

   chave_primaria = ['date', 'hour', 'outer']
   chave_unica = ['outer', 'hour', 'date']
   createTable(conn, consTable, campos, chave_primaria, chave_unica)



for d,LABEL in enumerate(iter_time(args.LABELI, args.LABELF, args.incr)):
   anlDate = LABEL.strftime('%Y%m%d%H')
   tmp = vars(args)
   #file = args.path+'/'+anlDate+'/fort.220'
   #file = args.path.replace('%Y%m%d%H', LABEL.strftime("%Y%m%d%H"))+'/fort.220'
   file = os.path.join(tmp['path'],anlDate,'fort.220')
   date      = []
   hour      = []
   date2     = []
   hour2     = []
   costRows  = []
   JRows     = []
   gNormRows = []
   qNegRows  = []
   qSupRows  = []
   massRows  = []
   count     = []
   exists    = os.path.isfile(file)

   if exists:

      with open(file, 'r') as log:
         for line in log.readlines():
            # apagar espaços em branco no inicio
            # e no final da linha
            line = line.strip()
            l    = line.split()
            #
            # Parse cost,grad,step,b,step?
            #
            if 'cost,grad,step,b,step?' in line:
               JRows.append(l[2:8])
               #
               # date Append
               date.append(LABEL.strftime('%Y-%m-%d %H:%M:%S'))
               hour.append(LABEL.strftime('%H'))

            #
            # Parse gnorm(1:2)?
            #               
            if 'gnorm(1:2)' in line:
               gNormRows.append(l[2:4])


            #
            # Parse Jb,Jo,Jc,Jl
            #
            if 'costterms Jb,Jo,Jc,Jl  =' in line:
               costRows.append(l[5:9])


            #
            # Parse mass conservation terms
            #
            if 'mean_ps,' in line:
               massRows.append(l[4:7])
               date2.append(LABEL.strftime('%Y-%m-%d %H:%M:%S'))
               hour2.append(LABEL.strftime('%H'))


            #
            # Parse Negative and Supersaturated Humidity
            #
            if 'NEG RH COUNT,RMS=' in line:
               qNegRows.append(l[3:4])

            #
            #
            #
            if 'SUPERSAT RH COUNT,RMS='in line:
               qSupRows.append(l[3:4])

               
      # To get the gnorm value from the fort.220 file using the line that starts 
      # "cost,grad,step,b,step?:".  
      #
      # So, using the grad value on that line:
      #   gnorm[i]  = (grad[i]**)/(grad[0]**)
      #   reduct[i] = sqrt(gnorm)
      #
      gnorm = []
      reduction = []
      for row in JRows:
          denominator = float(JRows[0][3])

          if denominator != 0:
             norm   = float(row[3])**2 / denominator**2
             reduct = float(row[3]) / float(denominator)
             gnorm.append(norm)
             reduction.append(reduct)
             #reduction.append(np.sqrt(norm))

          else:
             # Lidar com a situação onde o denominador é zero (evitar a divisão por zero)
             # Você pode definir um valor padrão ou tomar alguma ação apropriada aqui.
             norm = -1e38
             gnorm.append(norm)
             reduction.append(norm)
             
      # Concatenando todos os campos em uma única lista
      all_fields = fieldsFix + fieldsCost

      #  dados em data, hour, JRows, costRows, gNormRows, gnorm e reduction
      data = np.column_stack([date, hour, JRows, costRows, gNormRows, gnorm, reduction])

      # Criando o DataFrame
      costFunc = pd.DataFrame(data, columns=all_fields)
      
      # Inserindo no bando de dados
      upsert_data(conn,costTable,costFunc,['date','hour','outer','inner'])


      # Concatenando todos os campos em uma única lista
      all_fields = fieldsFix[0:3] + fieldsCons

      #  dados em date2, hour2, loop, massRows, qNegRows,qSupRows
      loop = [ i for i in range(len(massRows))]
      data = np.column_stack([date2, hour2, loop, massRows, qNegRows, qSupRows])

      # Criando o DataFrame
      costCons = pd.DataFrame(data, columns=all_fields)

      upsert_data(conn,consTable,costCons,['date','hour','outer'])


conn.close()



#EOC
#-----------------------------------------------------------------------------#

