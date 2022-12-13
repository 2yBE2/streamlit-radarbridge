import streamlit as st
import calendar
import datetime
from io import StringIO
import csv
import pandas as pd
import numpy as np

st.set_page_config(
        page_title="Radar speed map",
        page_icon="🚦",
        menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': "### RDash for RadarBridge\nDashboard for viewing radar statistics and management.",
            }
        )

st.title("🚦 Analiza podatkov radarskih tabel")
uploaded_file = st.file_uploader("Izberi CSV datoteko", label_visibility='collapsed')
if uploaded_file is not None:
    file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    csv_file = csv.reader(file, delimiter=',', quotechar='|')

    processed_header = False
    speed_parameter_index = None
    for row in csv_file:
        if 'speed' in row and 'func' in row and 'status' in row and not processed_header:
            processed_header = True
            speed_parameter_index = row.index('speed')

            speed_column_count = 0
            for column in row:
                if 'speed' == column:
                    speed_column_count += 1
            if speed_column_count > 1:
                st.error("V CSV datoteki so lahko podatki za le eno radarsko tablo.")
            elif speed_column_count == 0:
                st.error("V CSV datoteki ni podatkov z radarske table.")
            continue
        elif 'Device ID' in row and processed_header:
            device_name = row[speed_parameter_index]
            continue
    st.write("## Analiza podatkov")
    df = pd.read_csv(uploaded_file)

    df.drop([0, 1], inplace=True)
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])

    df['speed'] = df['speed'].fillna(0)
    df['speed'] = df['speed'].astype(str).astype(float).round().astype(int)

    df.rename(columns={df.columns[0]: 'Čas', 'speed': 'Hitrost', 'ambient_light': 'Svetilnost', 'battery_voltage': 'Napetost akumulatorja', 'func': 'Funkcija', 'status': 'Status'}, inplace=True)

    measurements, radar = st.columns(2)
    measurements.metric('Št. meritev', len(df['Hitrost']))
    radar.metric('Ime merilca', device_name)
    Vd, Vdmax, Vdmin = st.columns(3)
    Vd.metric('Povprečna hitrost', str(round(df['Hitrost'].mean(), 2)) + " km/h")
    Vdmax.metric('Maksimalna hitrost', str(round(df['Hitrost'].max(), 2)) + " km/h")
    Vdmin.metric('Minimalna hitrost', str(round(df[df['Hitrost'] > 0]['Hitrost'].min(), 2)) + " km/h")

    V85, V50, V30, V10 = st.columns(4)
    V85.metric('V85', str(round(df[df['Hitrost'] > 0]['Hitrost'].quantile(0.85), 2)) + " km/h")
    V50.metric('V50', str(round(df[df['Hitrost'] > 0]['Hitrost'].quantile(0.50), 2)) + " km/h")
    V30.metric('V30', str(round(df[df['Hitrost'] > 0]['Hitrost'].quantile(0.30), 2)) + " km/h")
    V10.metric('V10', str(round(df[df['Hitrost'] > 0]['Hitrost'].quantile(0.10), 2)) + " km/h")

    st.dataframe(df)
    st.line_chart(df, x=df.columns[0], y='Hitrost')

    pd.options.plotting.backend = "plotly"
    fig = df[df['Hitrost'] > 0].plot(kind='hist', x='Hitrost', bins=10)
    st.plotly_chart(fig)
