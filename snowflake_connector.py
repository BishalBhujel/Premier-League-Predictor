import snowflake.connector

def snowflake_connector_init():
    con = snowflake.connector.connect(
    user='BISHALBHUJEL112',
    password='Manchester20262027',
    account='UUOPOQH-CX35498',
    warehouse = 'COMPUTE_WH',
    database='trail',
    schema='trial_schema'
    )

    print('Connected to snowflake successfully')
    return con