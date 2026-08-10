import os
import pandas as pd
from openpyxl import load_workbook
import snowflake.connector

file_path = os.getcwd() + '/datasets/history_points_table.xlsx'

# Get all sheet names
sheet_names = pd.ExcelFile(file_path).sheet_names

data = {}

for sheet in sheet_names:
    # Extract year from sheet name
    year = sheet.split('_')[-1]

    sheet_type = sheet.split('_')[0]

    # Create data_2020, data_2021, etc.
    variable_name = f'data_{year}'

    # Read the sheet
    df = pd.read_excel(file_path, sheet_name=sheet)

    df.columns = [
        f'{column}_{sheet_type}'
        for column in df.columns
    ]

    if variable_name not in data:
        data[variable_name] = df
    else:
        # Merge side-by-side
        data[variable_name] = pd.concat(
            [data[variable_name], df],
            axis=1
        )

con = snowflake.connector.connect(
 user='BISHALBHUJEL112',
 password='Manchester20262027',
 account='UUOPOQH-CX35498',
 warehouse = 'COMPUTE_WH',
 database='trail',
 schema='trial_schema'
)

print('connected to snowflake')

for year in data:
    table_name = year
    columns = data[year].columns.tolist()
    snowflake_column_name = []
    for column in columns:
        if column.split('_')[0] in ('name', 'shortName','abbr'):
            snowflake_column_name.append(column + ' varchar')
        else:
            snowflake_column_name.append(column + ' number')
    column_definition = ", ".join(snowflake_column_name)

    sql = f'''Create  or Replace table {table_name}
       ({column_definition});'''

    print(sql)

    con.cursor().execute(sql)

    for value in data[year].values:
        value_list = value.tolist()
        value_list = [
        x.replace("'", "") if isinstance(x, str) else x
        for x in value_list
    ]
        sql = f'''
        insert into {table_name}
            select {str(value_list)[1:-1]};'''
        print(sql)
        con.cursor().execute(sql)