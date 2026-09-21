import snowflake.connector

def snowflake_connector_init():
    con = snowflake.connector.connect(
    user='bishal1',
    password='DataScience@1123',
    account='GBNRPYF-ZT81895',
    warehouse = 'COMPUTE_WH',
    database='trail',
    schema='trial_schema'
    )

    print('Connected to snowflake successfully')
    return con