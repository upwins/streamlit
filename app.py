import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import util_scripts as util

import os
from dotenv import load_dotenv

import streamlit as st

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_DBR_URI = os.getenv('MONGO_DBR_URI')

st.set_page_config(layout='wide')

reload_data_driver = False

if (reload_data_driver):

    records = []

    # Create a new client and connect to the server
    client = MongoClient(MONGO_DBR_URI, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["upwins_db"]
    view_name = "spectral_library"
    spectral_library = db[view_name]

    records = spectral_library.find()

    df = pd.DataFrame(records)
    df.to_pickle('data/data.pkl')

else:
    if "df" not in st.session_state:
        st.session_state.df = pd.read_pickle('data/data.pkl')

#if "sc" not in st.session_state:
#    st.session_state.sc = util.SpectralCollection(st.session_state.df)

sc = util.SpectralCollection(st.session_state.df)

codes = ['part', 'age', 'health', 'bloom']
list_by = 'name'

pd.set_option('display.max_columns', None)


#df_totals = st.session_state.sc.df_with_codes(codes, list_by)
st.session_state.df_totals = sc.df_with_codes(codes, list_by)

st.markdown("# UPWINS: Plot Spectra")

st.markdown("## Totals")

st.table(st.session_state.df_totals)

species_list = [
    'Chasmanthium_latifolium',
    'Ammophila_breviligulata',
    'Panicum_amarum',
    'Panicum_virgatum',
    'Baccharis_halimifolia',
    'Iva_frutescens',
    'Solidago_sempervirens',
    'Robinia_hispida',
    'Morella_pennsylvanica',
    'Rosa_rugosa',
    'Chamaecrista_fasciculata',
    'Solidago_rugosa',
    'Ilex_vomitoria'
]

st.markdown("## Species")

selected_species = st.multiselect("Select Species", options=species_list)

st.markdown("## Filters")

left_column, right_column = st.columns(2)

filters = {
    'name': '',
    'fname': '',
    'genus': '',
    'species': '',
    'age': '',
    'health': '',
    'part': '',
    'type': '',
    'bloom': '',
    'date': ''
}

for i, (key, value) in enumerate(filters.items()):
    if (key in ['name', 'fname']):
        continue
    
    options = sc.code_dict[key][1].copy()
    options.insert(0, '')

    if i % 2 == 0:
        if len(options) > 1:
            filters[key] = left_column.selectbox(key, options)
        else:
            filters[key] = left_column.text_input(key, key=key)   
    else:
        if len(options) > 1:
            filters[key] = right_column.selectbox(key, options)
        else:
            filters[key] = right_column.text_input(key, key=key)

# left_column.text_input('name', key='name')
# left_column.text_input('fname', key='fname')
# left_column.text_input('genus', key='genus')
# left_column.text_input('species', key='species')
# left_column.text_input('age', key='age')

# right_column.text_input('health', key='health')
# right_column.text_input('part', key='part')
# right_column.text_input('type', key='type')
# right_column.text_input('bloom', key='bloom')
# right_column.text_input('date', key='date')

#st.write(st.session_state.items())

st.markdown("## Plot")

plotby = st.selectbox("Plot by", filters.keys())

if st.button("Plot", type="primary"):

    filter = {}
    for key, val in filters.items():
        #st.write(key, val)
        if val:
            filter[key] = val

    
    #plotby = 'age'

    for species in selected_species:
       filter['name'] = species
       #st.session_state.sc.plot_with_filter(filter, plotby)
       sc.plot_with_filter(filter, plotby)
       st.pyplot(plt.gcf())