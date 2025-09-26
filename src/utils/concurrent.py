"""Concurrency utilities."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Iterator
import logging


logger = logging.getLogger(__name__)


def concurrent_map(func: Callable, items: List[Any], max_workers: int = 10) -> List[Any]:
    """Execute function over items concurrently."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(func, item): item for item in items}
        
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {item}: {e}")
                results.append(None)
    
    # Filter out None results
    return [r for r in results if r is not None]


def concurrent_map_with_progress(
    func: Callable, 
    items: List[Any], 
    max_workers: int = 10,
    progress_callback: Callable[[int, int], None] = None
) -> List[Any]:
    """Execute function with progress tracking."""
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
                logger.error(f"Error processing {item}: {e}")
                completed += 1
    
    # Sort by index and extract results
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results if r[1] is not None]
