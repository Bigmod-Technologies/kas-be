from datetime import datetime
import re
from django.core.exceptions import AppRegistryNotReady


def generate_order_number():
    """
    Generate a unique sequential order number.
    Returns a unique order number formatted with ORD prefix, year, and leading zeros (e.g., ORD-2025-0001, ORD-2025-0002, ORD-2025-0557, ...)
    """
    try:
        # Import here to avoid circular import
        from apps.sales.models import OrderDelivery
    except AppRegistryNotReady:
        # Return a temporary number if apps aren't ready (e.g., during migrations)
        return f"ORD-{datetime.now().year}-0001"
    
    # Get current year
    current_year = datetime.now().year
    
    try:
        # Get all existing order numbers for current year
        existing_orders = OrderDelivery.objects.values_list('order_number', flat=True).exclude(order_number__isnull=True).exclude(order_number='')
        
        # Filter orders that start with ORD-{current_year}
        ord_year_prefix = f"ORD-{current_year}"
        current_year_orders = [o for o in existing_orders if str(o).startswith(ord_year_prefix)]
    except Exception:
        # If database is not ready (e.g., during migrations), return a default number
        return f"ORD-{current_year}-0001"
    
    if not current_year_orders:
        # No existing order numbers for current year, start from 1
        next_number = 1
    else:
        # Extract sequential numbers from current year orders
        numbers = []
        for order in current_year_orders:
            # Extract number after the ORD-YYYY prefix (format: ORD-YYYY-0001)
            # Match pattern: ORD-YYYY-NNNN where NNNN is the sequential number
            match = re.search(rf'^ORD-{re.escape(str(current_year))}-(\d+)$', str(order))
            if match:
                numbers.append(int(match.group(1)))
        
        if numbers:
            # Get the maximum number and increment
            next_number = max(numbers) + 1
        else:
            # No matching format found, start from 1
            next_number = 1
    
    # Format with ORD prefix, year, and leading zeros (4 digits: ORD-2025-0001, ORD-2025-0002, etc.)
    order_number = f"ORD-{current_year}-{next_number:04d}"
    
    # Ensure uniqueness (in case of race condition)
    try:
        max_attempts = 100
        for attempt in range(max_attempts):
            if not OrderDelivery.objects.filter(order_number=order_number).exists():
                return order_number
            # If exists, increment and try again
            next_number += 1
            order_number = f"ORD-{current_year}-{next_number:04d}"
        
        # Fallback: if all attempts fail (extremely rare), use timestamp-based number
        # Extract last 4 digits of timestamp to maintain format consistency
        timestamp = int(datetime.now().timestamp())
        fallback_number = (timestamp % 9999) + 1  # Range: 1-9999 to avoid 0000
        fallback_order = f"ORD-{current_year}-{fallback_number:04d}"
        
        # Check if fallback is unique
        if not OrderDelivery.objects.filter(order_number=fallback_order).exists():
            return fallback_order
    except Exception:
        # If database is not ready, return the calculated number anyway
        return order_number
    
    # Last resort: increment next_number once more (it was last checked value that existed)
    # Ensure it wraps around properly if it exceeds 9999
    final_number = (next_number + 1) if (next_number + 1) <= 9999 else 1
    return f"ORD-{current_year}-{final_number:04d}"


