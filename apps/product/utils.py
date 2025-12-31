from datetime import datetime
import re
from apps.product.models import Product


def generate_sku():
    """
    Generate a unique sequential SKU number.
    Returns a unique SKU formatted with SKU prefix and leading zeros (e.g., SKU-0001, SKU-0002, SKU-0557, ...)
    """
    # Get all existing SKUs
    existing_skus = Product.objects.values_list('sku', flat=True).exclude(sku__isnull=True).exclude(sku='')
    
    if not existing_skus:
        # No existing SKUs, start from 1
        next_number = 1
    else:
        # Extract numeric values from existing SKUs
        numbers = []
        for sku in existing_skus:
            # Try to extract number from SKU
            # Handle formats like: "1", "SKU-1", "SKU-0001", "001", etc.
            numeric_match = re.search(r'\d+', str(sku))
            if numeric_match:
                numbers.append(int(numeric_match.group()))
        
        if numbers:
            # Get the maximum number and increment
            next_number = max(numbers) + 1
        else:
            # No numeric SKUs found, start from 1
            next_number = 1
    
    # Format with SKU prefix and leading zeros (4 digits: SKU-0001, SKU-0002, etc.)
    sku = f"SKU-{next_number:04d}"
    
    # Ensure uniqueness (in case of race condition)
    max_attempts = 100
    for attempt in range(max_attempts):
        if not Product.objects.filter(sku=sku).exists():
            return sku
        # If exists, increment and try again
        next_number += 1
        sku = f"SKU-{next_number:04d}"
    
    # Fallback: use timestamp if all attempts fail
    timestamp = int(datetime.now().timestamp())
    return str(timestamp)

