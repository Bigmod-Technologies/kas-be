from datetime import datetime
import re
from apps.product.models import Product, Purchase


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


def generate_voucher_number():
    """
    Generate a unique sequential voucher number.
    Returns a unique voucher number formatted with PAY prefix, year, and leading zeros (e.g., PAY-2025-0001, PAY-2025-0002, PAY-2025-0557, ...)
    """
    # Get current year
    current_year = datetime.now().year
    
    # Get all existing voucher numbers for current year
    existing_vouchers = Purchase.objects.values_list('voucher_number', flat=True).exclude(voucher_number__isnull=True).exclude(voucher_number='')
    
    # Filter vouchers that start with PAY-{current_year}
    pay_year_prefix = f"PAY-{current_year}"
    current_year_vouchers = [v for v in existing_vouchers if str(v).startswith(pay_year_prefix)]
    
    if not current_year_vouchers:
        # No existing voucher numbers for current year, start from 1
        next_number = 1
    else:
        # Extract sequential numbers from current year vouchers
        numbers = []
        for voucher in current_year_vouchers:
            # Extract number after the PAY-YYYY prefix (format: PAY-YYYY-0001)
            # Match pattern: PAY-YYYY-NNNN where NNNN is the sequential number
            match = re.search(rf'^PAY-{re.escape(str(current_year))}-(\d+)', str(voucher))
            if match:
                numbers.append(int(match.group(1)))
        
        if numbers:
            # Get the maximum number and increment
            next_number = max(numbers) + 1
        else:
            # No matching format found, start from 1
            next_number = 1
    
    # Format with PAY prefix, year, and leading zeros (4 digits: PAY-2025-0001, PAY-2025-0002, etc.)
    voucher_number = f"PAY-{current_year}-{next_number:04d}"
    
    # Ensure uniqueness (in case of race condition)
    max_attempts = 100
    for attempt in range(max_attempts):
        if not Purchase.objects.filter(voucher_number=voucher_number).exists():
            return voucher_number
        # If exists, increment and try again
        next_number += 1
        voucher_number = f"PAY-{current_year}-{next_number:04d}"
    
    # Fallback: if all attempts fail (extremely rare), use timestamp-based number
    # Extract last 4 digits of timestamp to maintain format consistency
    timestamp = int(datetime.now().timestamp())
    fallback_number = (timestamp % 9999) + 1  # Range: 1-9999 to avoid 0000
    fallback_voucher = f"PAY-{current_year}-{fallback_number:04d}"
    
    # Check if fallback is unique
    if not Purchase.objects.filter(voucher_number=fallback_voucher).exists():
        return fallback_voucher
    
    # Last resort: increment next_number once more (it was last checked value that existed)
    # Ensure it wraps around properly if it exceeds 9999
    final_number = (next_number + 1) if (next_number + 1) <= 9999 else 1
    return f"PAY-{current_year}-{final_number:04d}"

