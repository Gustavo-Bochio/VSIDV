import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
#from streamlit_elements import elements, mui, html
import pathlib
#import matplotlib as plt

st.set_page_config(
    page_title="VSIDV",
    page_icon="./logo01.png",  # Optional: You can also set a page icon (favicon)
    layout="wide",  # Optional: "centered" or "wide"
    initial_sidebar_state="auto",  # Optional: "auto", "expanded", or "collapsed"
)

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("style.css")
load_css(css_path)

st.header('Bem-vindo!')
st.write('Este é um programa para cálculo de parâmetros obtidos nos experimentos do Projeto VSIDV')


#inicialização de algumas variáveis que serão usadas posteriormente
df=None
submitted = False
option = 'X_Value'


#Menu Lateral
with st.sidebar:
    st.image('logo01.png') #Carrega a imagem do logo

    #Carregamento de arquivo txt - ponto experimental
    uploaded_file = st.file_uploader("Escolha um arquivo") 
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, skiprows=23, encoding='latin-1', delimiter='\t', decimal=',')
    
    #Carrega o menu de valores de referência - alpha e dpdx
    if df is not None:
        
        with st.form("gamma_dpdx"):
            st.write("Valores de referência:")
            gamma_inf = st.text_input("Limite inferior Gamma-Ray D", key="gamma_inf")
            gamma_sup = st.text_input("Limite superior Gamma-Ray D", key="gamma_sup")
            sensor_dpdx = st.selectbox('Sensor diferencial usado:', ['3 kPa', '10 kPa', '40 kPa'])
            submitted = st.form_submit_button("Submit")
            
#Corpo principal do programa - só carrega se houver um dataframe válido
if df is not None:

    #Linha horizontal para separar o cabeçalho do restante do corpo
    with st.container(key='ct01'):
        st.write('')

    #Escreve valores médios de J_g e J_l - alpha e dpdx se o menu de valores de referência foi submetido
    st.subheader('Características gerais:')
    Usg = np.mean(df['J_SF6'])
    Usl = np.mean(df['J_Oleo'])

    alpha = 1 #Adicionar cálculo de alpha

    if sensor_dpdx == '3 kPa':
        dpdx = np.mean(df['PDT-M-0101C-3kPa_mA'])
    elif sensor_dpdx == '10 kPa':
        dpdx = np.mean(df['PDT-M-0101B-10kPa_mA'])
    else:
        dpdx = np.mean(df['PDT-M-0101-40kPa_mA'])


    if not submitted:
        st.write(f"$$ U_{{sg}} = {Usg:.3f} ~m/s  ~||~  U_{{sl}} = {Usl:.3f} ~m/s$$")
    else:
        st.write(f"$$U_{{sg}} = {Usg:.3f} ~m/s  ~||~  U_{{sl}} = {Usl:.3f} ~m/s  ~||~  \\alpha  = {alpha:.3f}   ~||~  \\partial P / \\partial x = {dpdx:.3f}$$")

    st.divider(width="stretch") #Linha divisória

    
    # Primeira seção - gráfico temporal univariado e estatísticas básicas

    with st.container(key='dados'):
        st.subheader('Dados e gráficos')
        
        col01, col02 = st.columns([2, 1], gap='large')
        
        #Slider para definir a janela de observação
        with col01.container():

            slid_value = st.slider(label='Selecione uma janela:', min_value=df['X_Value'].min(), max_value=df['X_Value'].max(), value = (df['X_Value'].min() , df['X_Value'].max()), step=df['X_Value'][2]-df['X_Value'][1], key='slider')
            
            st.write(f"Você selecionou a faixa: {slid_value[0]:.2f} a {slid_value[1]:.2f}")

            condition = (df['X_Value'] >= slid_value[0]) & (df['X_Value'] < slid_value[1])
            filtered_df = df[condition] #novo dataframe - só com os valores no intervalo selecionado

        #Seleção da variável a ser plotada
        with col02.container():
            option = st.selectbox(
            'Selecione uma variável para avaliação:',
            df.columns, width=300)
            option, '- Sensor xxx'


        #Resumo estatístico
        dados = {'Média': [np.mean(filtered_df[option])],
            'Desvio Padrão': [np.std(filtered_df[option])],
            'Mediana': [np.median(filtered_df[option])],
            'Variância': [np.var(filtered_df[option])]}
        
        #Cria um pequeno DF para os valores estatísticos para criar a tabela
        stat_data = pd.DataFrame(dados).T

        stat_data.rename(columns={0: ''}, inplace=True)
        stat_data.index.name = 'Métrica'


        #Plotando gráficos e tabela
        colA, colB, colC = st.columns([2, 1, 1], gap='large')

        with colA.container(): #Gráfico de linha temporal

            fig = px.line(filtered_df, x='X_Value', y=option, title=f"{option} vs Tempo")
            st.plotly_chart(fig, key='graph')

        with colB.container(): #Boxplot

            bp_1 = px.box(filtered_df, y=option, title=f"{option} boxplot", color_discrete_sequence=px.colors.qualitative.Vivid)
            st.plotly_chart(bp_1)
        
        with colC.container(key='stats'): #Tabela de resumo estatístico
            st.dataframe(stat_data, width=300)
        
        #Opção de mostrar o dataframe completo
        if st.checkbox('Mostrar tabela de dados'):
            df


    st.divider(width="stretch") #Linha horizontal divisória


    # Segunda seção - comparação entre variáveis
    with st.container(key='multivar'):

        st.subheader('Análise multivariável')

        col01, col02 = st.columns([2, 1], gap='large')

        #Seleção do número de variáveis 
        with st.container(key='n_var'):
            nvar = st.selectbox(
            'Número de variáveis:',
            [1,2,3,4,5])
        
        vec_nvar = np.ones(nvar)

        cols = st.columns(vec_nvar, gap='medium')

        variable = [None] * nvar
        with st.container():
            for i, col in enumerate(cols):
                variable[i] = col.selectbox(
                f'Variável {i+1}:',
                df.columns)

        col1, col2 = st.columns([2, 1], gap='medium')

        fig2 = px.line(filtered_df, x='X_Value', y=variable, color_discrete_sequence=px.colors.qualitative.Vivid)
        bp_fig = px.box(filtered_df, y=variable)
        
        col1.plotly_chart(fig2)
        col2.plotly_chart(bp_fig)

    st.divider(width="stretch")
    with st.container(key='correl'):
        st.subheader('Correlacionando variáveis')

        col11, col12 = st.columns([1, 1], gap='large')

        lista = filtered_df.columns.tolist()


        x_corr = col11.selectbox(
            'Variável em x:',
            lista)
        
        lista.remove(x_corr)
        
        y_corr = col12.selectbox(
            'Variável em y:',
            lista)

        fig3 = px.scatter(filtered_df, x=x_corr, y=y_corr, color_discrete_sequence=px.colors.qualitative.Vivid, trendline="ols")
        tl_results = px.get_trendline_results(fig3)

        col11.plotly_chart(fig3)
    
        col12.write(tl_results.px_fit_results.iloc[0].summary())







    



