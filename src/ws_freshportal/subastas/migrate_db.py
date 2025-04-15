import xlrd
import pandas as pd
from os import devnull
from database.db_freshportal import insert_subastas, delete_subastas
from datetime import datetime, timedelta

def delete_old_data():
    fecha_limite = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')    
    delete_subastas((fecha_limite, ))
    
def save():
    # Ruta al archivo Excel
    input_file = r"C:/Users/mateo/Desktop/Chamba/API/Web-Scraping_API/src/ws_freshportal/subastas/FloridayIoYieldExcel.xls"
    try:
        # Abrir el archivo Excel usando xlrd para evitar errores de corrupción
        wb = xlrd.open_workbook(input_file, logfile=open(devnull, 'w'), ignore_workbook_corruption=True)
        df = pd.read_excel(wb, dtype=str, skiprows=0, engine='xlrd')  # Leer el contenido del archivo .xls
        print("Archivo Excel leído correctamente. Procesando datos...")

        # Validar si el DataFrame tiene contenido
        if df.empty:
            print("El archivo Excel no contiene datos. No se realizará ningún procesamiento.")
        else:
            delete_old_data()

        def clean_float(valor):
            """ Limpia y convierte un valor numérico a float. Retorna None si es vacío o no convertible. """
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            valor = str(valor).strip().replace("€", "")
    
            # Si hay comas, las dejamos solo si son separadores de decimales
            if "," in valor and "." not in valor:
                valor = valor.replace(",", ".")  # Comas como separadores decimales
            else:
                valor = valor.replace(",", "")  # Si no es un separador decimal, eliminamos la coma

            try:
                return float(valor)
            except ValueError:
                return None

        def clean_text(valor):
            """ Limpia y retorna texto sin espacios innecesarios. """
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            return str(valor).strip()

        def clean_date(valor):
            """Limpia y convierte una fecha al formato '%Y-%m-%d'. Retorna None si la fecha es inválida o vacía."""
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            try:
                # Indicar el formato explícito según los datos de entrada (modificar si es necesario)
                return pd.to_datetime(valor, format='%d-%m-%Y').strftime('%Y-%m-%d')
            except ValueError:
                try:
                    # Si falla, intenta con el formato alternativo
                    return pd.to_datetime(valor, format='%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    return None
                
        # Iterar sobre las filas del DataFrame
        for index, row in df.iterrows():
            try:
                # Procesar las fechas (columna 0 y 1)
                fecha_auction = clean_date(row.iloc[0])  # Usar iloc para acceder por posición
                fecha_subasta = clean_date(row.iloc[1])  # Usar iloc para acceder por posición

                # Construir la fila con tipos correctos
                data = [
                    fecha_auction,
                    fecha_subasta,         
                    clean_text(row.iloc[2]),
                    clean_text(row.iloc[3]),  
                    clean_text(row.iloc[4]), 
                    clean_text(row.iloc[5]),
                    clean_text(row.iloc[6]),
                    clean_text(row.iloc[7]),
                    clean_text(row.iloc[8]),
                    clean_text(row.iloc[9]),
                    clean_text(row.iloc[10]),
                    clean_text(row.iloc[11]), 
                    clean_text(row.iloc[12]),
                    clean_float(row.iloc[13]),
                    clean_float(row.iloc[14])
                ]

                # Insertar en la base de datos
                insert_subastas(tuple(data))

            except Exception as fila_error:
                print(f"Error en la fila: {row}, Detalle: {fila_error}")
                
        print("Inserción finalizada correctamente.")

    except Exception as e:
        print(f"Ocurrió un error general: {e}")