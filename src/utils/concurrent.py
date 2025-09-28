"""
Utilidades para concurrencia y procesamiento paralelo en el proyecto UFC ETL.
Incluye funciones para ejecutar tareas en paralelo utilizando hilos y para realizar seguimiento de progreso.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Iterator
import logging


logger = logging.getLogger(__name__)


def concurrent_map(func: Callable, items: List[Any], max_workers: int = 10) -> List[Any]:
    """
    Ejecuta una función sobre una lista de elementos de forma concurrente utilizando hilos.
    Los resultados que generen excepciones se registran y se filtran del resultado final.
    Args:
        func (Callable): Función a aplicar a cada elemento.
        items (List[Any]): Lista de elementos a procesar.
        max_workers (int): Número máximo de hilos concurrentes.
    Returns:
        List[Any]: Lista de resultados exitosos (excluye los que generaron error).
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(func, item): item for item in items}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error procesando {item}: {e}")
                results.append(None)
    # Se filtran los resultados para eliminar aquellos que sean None (errores)
    return [r for r in results if r is not None]


def concurrent_map_with_progress(
    func: Callable, 
    items: List[Any], 
    max_workers: int = 10,
    progress_callback: Callable[[int, int], None] = None
) -> List[Any]:
    """
    Ejecuta una función sobre una lista de elementos de forma concurrente, permitiendo seguimiento del progreso.
    Cada tarea puede reportar su avance mediante un callback opcional.
    Args:
        func (Callable): Función a aplicar a cada elemento (debe aceptar el índice como segundo argumento).
        items (List[Any]): Lista de elementos a procesar.
        max_workers (int): Número máximo de hilos concurrentes.
        progress_callback (Callable, opcional): Función callback para reportar progreso (completados, total).
    Returns:
        List[Any]: Lista de resultados exitosos (excluye los que generaron error), ordenados por índice original.
    """
    results = []
    total = len(items)
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(func, item, idx): (item, idx) 
                          for idx, item in enumerate(items)}
        for future in as_completed(future_to_item):
            item, idx = future_to_item[future]
            try:
                result = future.result()
                results.append((idx, result))
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
            except Exception as e:
                logger.error(f"Error procesando {item}: {e}")
                completed += 1
    # Ordena los resultados por índice y extrae los valores finales
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results if r[1] is not None]
