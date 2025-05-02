from datetime import datetime, timedelta
from database.db_unosof import insert_data_dae, delete_data_dae

def delete_old_records():
    """Elimina registros antiguos de la tabla rptDAE_Developer."""
    fecha_limite = (datetime.now() - timedelta(days=46)).strftime('%Y-%m-%d')
    delete_data_dae((fecha_limite, ))

def save(data):
    """Lee datos y los inserta en la base de datos evitando duplicados."""
    try:
        # if data:
        #     delete_old_records()
        
        for row in data:
            # Intentar convertir los valores de las columnas
            try:
                # Convertir a entero en row[1]
                row[1] = int(row[1]) 
                
                # Convertir fecha en row[14]
                dateTimeObj = datetime.strptime(row[14], '%b-%d-%Y')
                row[14] = dateTimeObj.strftime('%Y-%m-%d')
                
                # Convertir otras columnas a float o int según corresponda
                row[19] = float(row[19]) if row[19] not in ("", None) else 0.0
                row[20] = float(row[20]) if row[20] not in ("", None) else 0.0
                row[21] = float(row[21]) if row[21] not in ("", None) else 0.0
                row[25] = float(row[25]) if row[25] not in ("", None) else 0.0
                row[28] = int(row[28]) if row[28] not in ("", None) else 0
                row[29] = float(row[29]) if row[29] not in ("", None) else 0.0
                row[31] = float(row[31]) if row[31] not in ("", None) else 0.0
                row[32] = float(row[32]) if row[32] not in ("", None) else 0.0
                row[36] = float(row[36]) if row[36] not in ("", None) else 0.0
                row[37] = float(row[37]) if row[37] not in ("", None) else 0.0
                row[38] = float(row[38]) if row[38] not in ("", None) else 0.0
                row[43] = int(row[43]) if row[43] not in ("", None) else 0
                
            except ValueError as e:
                print(f"Error al procesar los datos: {e}. Row: {row}")
                continue

            # Insertar los datos en la base de datos
            insert_data_dae(row)
            print(f'Insertando datos: {row}')
            
    except Exception as e:
        print(f"Ocurrió un error al guardar los datos: {e}")