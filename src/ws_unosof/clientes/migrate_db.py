from database.db_unosof import insert_data_cst, delete_data_cst
from datetime import date
    
def save(data):
    try:
        
        if data:
            delete_data_cst()
            
        print("Cantidad de customers: ", {len(data)})
        
        for row in data:

            filtered_row = row[2:-4]

            try:
                filtered_row[0] = int(filtered_row[0]) if str(filtered_row[0]).isdigit() else 0
            except Exception as e:
                filtered_row[0] = 0

            try:
                filtered_row[2] = date.fromisoformat(filtered_row[2]).strftime('%Y-%m-%d')
            except Exception as e:
                filtered_row[2] = None

            try:
                filtered_row[3] = int(filtered_row[3]) if str(filtered_row[3]).replace('.', '', 1).isdigit() else 0.0
            except Exception as e:
                filtered_row[3] = 0.0

            try:
                filtered_row[17] = int(filtered_row[17]) if str(filtered_row[17]).isdigit() else 0
            except Exception as e:
                filtered_row[17] = 0.0

            insert_data_cst(tuple(filtered_row))

    except Exception as e:
        message = f"Error al guardar los datos con los clientes {e}"
        print(message)