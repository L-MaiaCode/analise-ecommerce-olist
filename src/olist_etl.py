"""

"""
import pandas as pd

# Lendo os arquivos
caminho_bruto = "data/raw"

customers = pd.read_csv(f'{caminho_bruto}/olist_customers_dataset.csv')
geolocation = pd.read_csv(f'{caminho_bruto}/olist_geolocation_dataset.csv')
order_items = pd.read_csv(f'{caminho_bruto}/olist_order_items_dataset.csv')
order_payments = pd.read_csv(f'{caminho_bruto}/olist_order_payments_dataset.csv')
order_reviews = pd.read_csv(f'{caminho_bruto}/olist_order_reviews_dataset.csv')
orders = pd.read_csv(f'{caminho_bruto}/olist_orders_dataset.csv')
products = pd.read_csv(f'{caminho_bruto}/olist_products_dataset.csv')
sellers = pd.read_csv(f'{caminho_bruto}/olist_sellers_dataset.csv')
category_translation = pd.read_csv(f'{caminho_bruto}/product_category_name_translation.csv')

# Dataset para auxiliar na análise exploratória
datasets = {
    'customers':customers,
    'geolocation':geolocation,
    'order_items':order_items,
    'order_payments':order_payments,
    'order_reviews':order_reviews,
    'orders':orders,
    'products':products,
    'sellers':sellers,
    'category_translation':category_translation
}

# Análise exploratória rápida
for name, df in datasets.items():
    nulls = df.isnull().sum().sum()
    nulls_cols_count = df.isnull().any().sum()
    
    colunas_com_nulo = df.columns[df.isnull().any()].to_list()
    nomes_colunas_str = ', '.join(colunas_com_nulo)
    
    if not nomes_colunas_str:
        nomes_colunas_str = 'Nenhuma'

    print(f'{name:<25}: {len(df):>8} linhas, {df.shape[1]:>2} colunas, {nulls:>2} valores nulos, {nulls_cols_count:>2} colunas com nulos')
    print(f'{"":<25} -> Colunas afetadas: {nomes_colunas_str}\n')
