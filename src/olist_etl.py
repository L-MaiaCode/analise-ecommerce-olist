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

# -> Dimensão dCliente ----------------------------------
print('Criando dCliente...')

dCliente = customers[[
    'customer_id',
    'customer_unique_id',
    'customer_city',
    'customer_state'
]].drop_duplicates(subset='customer_id').copy()

# Mapeamento das regiões
regioes = {
    "AC":"Norte","AM":"Norte","AP":"Norte","PA":"Norte","RO":"Norte","RR":"Norte","TO":"Norte",
    "AL":"Nordeste","BA":"Nordeste","CE":"Nordeste","MA":"Nordeste","PB":"Nordeste",
    "PE":"Nordeste","PI":"Nordeste","RN":"Nordeste","SE":"Nordeste",
    "DF":"Centro-Oeste","GO":"Centro-Oeste","MS":"Centro-Oeste","MT":"Centro-Oeste",
    "ES":"Sudeste","MG":"Sudeste","RJ":"Sudeste","SP":"Sudeste",
    "PR":"Sul","RS":"Sul","SC":"Sul"
}

dCliente['regioes'] = dCliente['customer_state'].map(regioes)

dCliente = dCliente.rename(columns={
    'customer_city': 'cidade',
    'customer_state': 'estado'
})

dCliente.insert(0, 'sk_cliente', range(1, len(dCliente) + 1))

dCliente.to_csv(f'data/output/dCliente.csv', index=False)

print(f'dCliente criada: {len(dCliente):,} clientes')

# -> Dimensão dProduto ---------------------------------------
print('Criando dProduto...')

dProduto = products.merge(
    category_translation,
    on='product_category_name',
    how='left'
)

# Colunas relevantes para análise
dProduto = dProduto[[
    'product_id',
    'product_category_name',
    'product_category_name_english',
    'product_photos_qty',
    'product_weight_g',
    'product_length_cm',
    'product_height_cm',
    'product_width_cm',
]]

# Preenchimento de nulos com mediana por categoria
for col in ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']:
    mediana = dProduto[col].median()
    dProduto[col] = dProduto[col].fillna(mediana)

dProduto['product_category_name_english'] = (
    dProduto["product_category_name_english"].fillna('sem categoria')
)

dProduto = dProduto.rename(columns={
    "product_category_name": "categoria_pt",
    "product_category_name_english": "categoria_en",
    "product_weight_g": "peso_g",
    "product_length_cm": "comprimento_cm",
    "product_height_cm": "altura_cm",
    "product_width_cm": "largura_cm",
    "product_photos_qty": "qtd_fotos"
})

dProduto.insert(0, 'sk_produto', range(1, len(dProduto) + 1))

dProduto.to_csv('data/output/dProduto.csv', index=False)
print(f'dProduto criada {len(dProduto):,} produtos')

# -> Dimensão Vendedor ---------------------------------
print('Criando dVendedor...')

dVendedor = sellers[[
    "seller_id",
    "seller_city",
    "seller_state"
]].copy()

dVendedor['regiao'] = dVendedor['seller_state'].map(regioes)

dVendedor.rename(columns={
    'seller_city': 'cidade',
    'seller_state': 'estado'
})

dVendedor.insert(0, 'sk_vendedor', range(1, len(dVendedor) + 1))

dVendedor.to_csv('data/output/dVendedor.csv', index=False)

print(f'dVendedor criada: {len(dVendedor):,} vendedores')

# -> Dimensão Pagamento -------------------------------------
print('Criando dPagamentos...')

pagamento_principal = (
    order_payments
    .sort_values('payment_value', ascending=False)
    .drop_duplicates(subset='order_id')
)

dPagamento = pagamento_principal[[
    'order_id',
    'payment_type',
    'payment_installments',
    'payment_value'
]].copy()

dPagamento = dPagamento.rename(columns={
    'payment_type': 'tipo_pagamento',
    'payment_installments': 'parcelas',
    'payment_value': 'valor_pago'
})

dPagamento.insert(0, 'sk_pagamento', range(1, len(dPagamento) + 1))

dPagamento.to_csv('data/output/dPagamento.csv', index=False)

print(f'dPagamento criada: {len(dPagamento):,} registros de pagamento')

# -> Avaliações por pedido
