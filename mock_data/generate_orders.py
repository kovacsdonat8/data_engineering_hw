import csv
import random
from datetime import datetime, timedelta
import os

def generate_daily_orders(date_str, num_orders=100):
    """Napi rendelési adatok generálása CSV fájlba."""
    os.makedirs('output', exist_ok=True)
    filename = f"output/orders_{date_str}.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['order_id', 'customer_id', 'product_id', 'quantity', 'order_timestamp', 'total_price'])

        for i in range(num_orders):
            order_id = f"ORD-{date_str.replace('-', '')}-{i:04d}"
            customer_id = random.randint(1, 50)
            product_id = random.randint(101, 110)
            quantity = random.randint(1, 5)

            # Véletlenszerű időpont a megadott napon belül
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            order_time = f"{date_str} {hour:02d}:{minute:02d}:00"

            # Fiktív ár számítás
            base_price = product_id * 1.5
            total_price = round(base_price * quantity, 2)

            writer.writerow([order_id, customer_id, product_id, quantity, order_time, total_price])

    print(f"[OK] {filename} sikeresen legenerálva {num_orders} sorral.")

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    generate_daily_orders(today, 150)