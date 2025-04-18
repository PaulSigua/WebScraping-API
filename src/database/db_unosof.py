from database.db import execute_insert_query, execute_select_query, execute_params_query, execute_query

url_login_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'url_login'"""

user_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'user_name'"""

password_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'password'"""

def get_url_login():
    return execute_select_query(2, url_login_query)

def get_user_login():
    return execute_select_query(2, user_query)

def get_password_login():
    return execute_select_query(2, password_query)

# DAE
url_dae_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 9 AND prm_descripcion = 'url_dae'"""

insert_dae_data_query = """INSERT INTO rptDAE_Developer VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

delete_dae_data_query = """DELETE FROM dbo.rptDAE_Developer
            WHERE PARSE(dae_fecha_vuelo as date) > ?"""

def get_url_data_dae():
    return execute_select_query(2, url_dae_query) 

def insert_data_dae(param):
    return execute_insert_query(2, insert_dae_data_query, param)

def delete_data_dae(param):
    return execute_params_query(2, delete_dae_data_query, param)

# CUSTOMERS
url_cst_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 11 AND prm_descripcion = 'url_cst'"""

insert_cst_data_query = """INSERT INTO rptCUSTOMERS VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

delete_cst_data_query = """DELETE FROM dbo.rptCUSTOMERS"""

def get_url_data_cst():
    return execute_select_query(2, url_cst_query) 

def insert_data_cst(param):
    return execute_insert_query(2, insert_cst_data_query, param)

def delete_data_cst():
    return execute_query(2, delete_cst_data_query)

# SALES
url_sales_query = """SELECT prm_valor FROM Parametros_Sistema
	            WHERE id_grupo = 9 AND prm_descripcion LIKE 'url_sales'"""

insert_report_sales_query = """INSERT INTO rptUnosof_Reportes_Ventas_Orden_Permanente VALUES (?,?,?,?,?,?,?,?,?,?)"""

delete_report_sales_query = """DELETE FROM rptUnosof_Reportes_Ventas_Orden_Permanente
            WHERE rvent_fecha_inicio_consulta >= ?"""

# Sales Master Report SKU (Reports)
# Open Maerkets
# Standing Orders
# Prebooks
             
# insert_cst_data_query

def get_url_data_sales():
    return execute_select_query(2, url_sales_query)

def insert_data_sales(param):
    return execute_insert_query(2, insert_report_sales_query, param)

def delete_data_sales(param):
    return execute_params_query(2, delete_report_sales_query, param)