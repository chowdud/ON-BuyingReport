import streamlit as st
import pandas as pd
from io import BytesIO


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def process_report(df: pd.DataFrame):
    for index, row in df.iterrows():
        shop_name = row['Shop Name']

        # Skip ePaws shop
        if "ePaws Pet Supplies" in shop_name:
            continue

        product_title = row['Product Title']
        sku = row['SKU']
        inventory_quantity = row['Inventory Quantity'] if row['Inventory Quantity'] else 0
        product_cost = row['Product cost'] if row['Product cost'] else 0
        last_30_days_sales = row['Last 30 Days Units from Today'] if row['Last 30 Days Units from Today'] else 0
        last_90_days_sales = row['Last 90 Days Units from Today'] if row['Last 90 Days Units from Today'] else 0

        if inventory_quantity == 0 and last_30_days_sales > 0:
            unit_buy = last_30_days_sales + 1
        elif 0 < inventory_quantity <= last_30_days_sales and last_30_days_sales > 0:
            unit_buy = last_30_days_sales - inventory_quantity
        elif inventory_quantity > last_30_days_sales:
            ratio = last_30_days_sales / inventory_quantity
            if ratio >= 0.80:
                unit_buy = (inventory_quantity - last_30_days_sales) * 2
            else:
                unit_buy = 0
        else:
            unit_buy = 0

        buy_cost = round(product_cost * unit_buy, 2)

        print(f"Shop Name: {shop_name}")
        print(f"Product Title: {product_title}")
        print(f"SKU: {sku}")
        print(f"Inventory Quantity: {inventory_quantity}")
        print(f"Last 30 Days Sales: {last_30_days_sales}")
        print(f"Last 90 Days Sales: {last_90_days_sales}")
        print(f"Product Cost: {product_cost}")
        print(f"Unit Buy: {unit_buy}")
        print(f"Buy Cost: {buy_cost}")
        print("======================================")

        print(df.loc[(df['SKU'] == sku) & (df['Shop Name'] == 'K9 Leathers')])

        if not df.loc[(df['SKU'] == sku) & (df['Shop Name'] == 'K9 Leathers')].empty:
            row_index = df.loc[(df['SKU'] == sku) & (df['Shop Name'] == 'K9 Leathers')].index[0]
            df.loc[row_index, 'Unit Buy'] = unit_buy
            df.loc[row_index, 'Buy Cost'] = buy_cost

    return to_excel(df)


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_excel(uploaded_file)
    # st.write(dataframe)
    # process_report(dataframe)
    excel = process_report(dataframe)
    st.download_button(label='Download Excel file', data=excel, file_name='data.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
