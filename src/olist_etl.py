"""
Projeto: Análise de E-commerce Brasileiro - Olist
Autor: Luca Maia Marques
Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Objetivo: 
    Transformar os dados brutos do dataset em um Star Schema
    pronto para ser usado no Power BI, em seguida gerar um dashboard
    que responda perguntas de negócio sobre vendas, logística e satisfação dos clientes.

Estrutura de saída:
    data/output/
        fPedidos.csv    -> Tabela fato central
        dData.csv       -> Dimensão de datas
        dCliente.csv    -> Dimensão de clientes
        dProduto.csv    -> imensão de produtos
        dVendedor.csv   -> Dimensão de vendedores
        dPagamento.csv  -> Dimensão de pagamentos
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

# -> Dimensão dData ----------------------------------
print('Criando dData...')

orders['order_purchase_timestamp'] = pd.to_datetime(orders["order_purchase_timestamp"])

datas_unicas = orders["order_purchase_timestamp"].dt.normalize().drop_duplicates().sort_values()

dData = pd.DataFrame({'data_completa': datas_unicas})
dData['sk_data']    = range(1, len(dData) + 1)
dData['data']       = dData['data_completa'].dt.date
dData['ano']        = dData['data_completa'].dt.year
dData['mes']        = dData['data_completa'].dt.month
dData['trimestre']  = dData['data_completa'].dt.quarter
dData['nome_mes']   = dData['data_completa'].dt.strftime('%B')
dData['semana_ano'] = dData['data_completa'].dt.isocalendar().week.astype(int)
dData['dia_semana'] = dData['data_completa'].dt.day_name()
dData['is_fim_semena'] = dData['data_completa'].dt.day_of_week >= 5

dData = dData[['sk_data', 'data', 'ano', 'mes', 'trimestre', 'nome_mes',
               'semana_ano', 'dia_semana', 'is_fim_semana']]

dData.to_csv('/data/output/dData.csv', index=False)

print(f'dData criada: {len(dData):,} datas únicas')

# -> Dimensão dCliente -------------------------------
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

# -> dPedidos
print('Criando fPedidos...')

orders['data_compra'] = orders['order_purchase_timestamp'].dt.normalize()
dData_lookup = dData.copy()
dData_lookup['data_completa'] = pd.to_datetime(dData['data'])
sk_mapa_map = dict(zip(dData_lookup['data_completa'], dData_lookup['sk_data']))

sk_cliente_map = dict(zip(dCliente['customer_id'], dCliente['sk_cliente']))


