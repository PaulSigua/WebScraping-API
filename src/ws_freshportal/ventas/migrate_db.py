from datetime import datetime, timedelta
from database.db_freshportal import delete_ventas, insert_ventas

def delete_old_records():
    # Obtener la fecha límite (hoy - 15 días)
    fecha_limite = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
    delete_ventas((fecha_limite, ))
    
def save(data):
    try:
        
        if data:
            delete_old_records()
        
        def clean_float(value):
            """ Limpia y convierte un value numérico a float. Retorna None si es vacío o no convertible. """
            if value is None or str(value).strip() == "":
                return None
            value = str(value).strip().replace(".", "").replace(",", ".").replace("€", "")
            try:
                return float(value)
            except ValueError:
                return None

        def clean_text(value):
            """ Limpia y retorna texto sin espacios innecesarios. """
            if value is None or str(value).strip() == "":
                return None
            return str(value).strip()

        def clean_date(value):
            """ Limpia y convierte una fecha al formato '%Y-%m-%d'. Retorna None si es inválida. """
            if value is None or str(value).strip() == "":
                return None
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return None

        def clean_porcentaje(value):
            """ Limpia y convierte un porcentaje a float sin el símbolo %. """
            if value is None or str(value).strip() == "":
                return None
            value = str(value).strip().replace("%", "")
            try:
                return float(value)
            except ValueError:
                return None

        for row in data:
            invoice_date = clean_date(row[1])

            row_list = [
                clean_text(row[0]),
                invoice_date,
                clean_text(row[2]),
                clean_text(row[3]),
                clean_text(row[4]),
                clean_text(row[5]),
                clean_text(row[6]),
                clean_text(row[7]),
                clean_text(row[8]),
                clean_text(row[9]),
                clean_text(row[10]),
                clean_text(row[11]),
                clean_text(row[12]),
                clean_text(row[13]),
                clean_text(row[14]),
                clean_text(row[15]),
                clean_text(row[16]),
                clean_text(row[17]),
                clean_text(row[18]),
                clean_float(row[19]),
                clean_float(row[20]),
                clean_float(row[21]),
                clean_float(row[22]),
                clean_float(row[23]),
                clean_float(row[24]),
                clean_float(row[25]),
                clean_float(row[26]),
                clean_float(row[27]),
                clean_porcentaje(row[28])
            ]

            # print("CLEAN ROW: ", row_list)  # Aquí podrías hacer insert DB, guardar JSON, etc.
            insert_ventas(row_list)
            
    except Exception as e:
        print(f'ERROR: {e}')