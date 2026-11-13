from __future__ import annotations
import numpy as np
import pandas as pd

@__import__('functools').lru_cache(maxsize=1)
def load_demo_data() -> pd.DataFrame:
    """Create deterministic DEMO data. Not real Olist observations."""
    rng = np.random.default_rng(42)
    n = 1800
    dates = pd.date_range('2025-01-01', '2025-12-31', freq='D')
    categories = ['Bed & Bath', 'Health & Beauty', 'Sports & Leisure', 'Furniture', 'Computers', 'Housewares', 'Watches']
    products = {
        'Bed & Bath': ['Cotton Sheet Set', 'Bath Towel Pack', 'Pillow Set'],
        'Health & Beauty': ['Skin Care Kit', 'Hair Dryer', 'Wellness Set'],
        'Sports & Leisure': ['Yoga Mat', 'Training Shoes', 'Fitness Band'],
        'Furniture': ['Office Chair', 'Side Table', 'Bookshelf'],
        'Computers': ['Wireless Mouse', 'Mechanical Keyboard', 'USB Hub'],
        'Housewares': ['Cookware Set', 'Storage Box', 'Water Bottle'],
        'Watches': ['Classic Watch', 'Sport Watch', 'Smart Watch'],
    }
    category = rng.choice(categories, n, p=[.19,.18,.13,.12,.14,.15,.09])
    product = [rng.choice(products[c]) for c in category]
    price = rng.lognormal(mean=3.55, sigma=.65, size=n).round(2)
    quantity = rng.choice([1,2,3,4], n, p=[.68,.22,.08,.02])
    order_date = pd.to_datetime(rng.choice(dates, n))
    customer = rng.integers(10000, 10850, n)
    cities = rng.choice(['São Paulo','Rio de Janeiro','Belo Horizonte','Curitiba','Porto Alegre','Brasília','Salvador'], n)
    payment = rng.choice(['Credit card','Debit card','Boleto','Voucher'], n, p=[.62,.16,.17,.05])
    status = rng.choice(['Delivered','Shipped','Canceled','Processing'], n, p=[.88,.06,.03,.03])
    df = pd.DataFrame({
        'order_id':[f'DEMO-{i:05d}' for i in range(1,n+1)],
        'customer_id':[f'C-{x}' for x in customer],
        'customer_unique_id':[f'CU-{x}' for x in customer],
        'order_date':order_date,
        'product_name':product,
        'category':category,
        'quantity':quantity,
        'unit_price':price,
        'total_amount':(price*quantity).round(2),
        'city':cities,
        'payment_mode':payment,
        'delivery_status':status,
    })
    return df.sort_values('order_date').reset_index(drop=True)
