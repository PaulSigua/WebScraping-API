from database.db import execute_select_query, execute_insert_query, execute_params_query

url_login_query = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'url_login'"""

user_login = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'user_name'"""

password_login = """SELECT prm_valor 
                        FROM dbo.Parametros_Sistema
                        WHERE id_grupo = 1 AND prm_descripcion LIKE 'password'"""

def get_url_login():
    return execute_select_query(1, url_login_query)

def get_user_login():
    return execute_select_query(1, user_login)

def get_password_login():
    return execute_select_query(1, password_login)

# SUBASTAS
insert_query_subastas = """INSERT INTO rptFresh_Portal_Subastas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

url_data_subastas_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 13 AND prm_descripcion = 'url_s'"""
                
delete_query_subastas = """DELETE FROM rptFresh_Portal_Subastas
            WHERE sub_invoice_date > ?"""

def insert_subastas(params):
    return execute_insert_query(1, insert_query_subastas, params)

def get_url_data_subastas():
    return execute_select_query(1, url_data_subastas_query)

def delete_subastas(param):
    return execute_params_query(1, delete_query_subastas, param)

# VENTAS
insert_query_ventas = """INSERT INTO rptFresh_Portal_Ventas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

url_data_ventas_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 10 AND prm_descripcion = 'url_v'"""

delete_query_ventas = """DELETE FROM rptFresh_Portal_Ventas
            WHERE vent_invoice_date > ?"""

def insert_ventas(params):
    return execute_insert_query(1, insert_query_ventas, params)

def get_url_data_ventas():
    return execute_select_query(1, url_data_ventas_query)

def delete_ventas(param):
    return execute_params_query(1, delete_query_ventas, param)