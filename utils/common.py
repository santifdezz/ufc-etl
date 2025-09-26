import csv

def save_to_csv(data, filename, fieldnames):
    """Guarda datos en un archivo CSV con nombres de columnas en minúsculas y None como 'null'."""
    try:
        fieldnames_lower = [f.lower() for f in fieldnames]
        def none_to_null(row):
            new_row = {}
            for k, v in row.items():
                key = k.lower()
                new_row[key] = 'null' if v is None else v
            return new_row
        data_lower = [none_to_null(row) for row in data]
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames_lower, restval='null')
            writer.writeheader()
            writer.writerows(data_lower)
        print(f"Datos guardados en {filename} ({len(data)} registros)")
    except Exception as e:
        print(f"Error guardando {filename}: {e}")

def concurrent_map(func, items, max_workers=10):
    import concurrent.futures
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for result in executor.map(func, items):
            results.append(result)
    return results
