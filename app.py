import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Funções auxiliares

def calculate_max_drawdown(prices):
    if len(prices) < 2:
        return 500

    max_drawdown = 0
    max_price = -np.inf
    min_price = np.inf

    for price in prices:
        if price > max_price:
            max_price = price
            min_price = price
        elif price < min_price:
            min_price = price

        drawdown = max_price - min_price
        max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown

def get_biggest_red_run(delta_money):
    # Inicializa a contagem da maior sequência de números negativos e a contagem temporária
    biggest_red_run = 0
    temp_red_run = 0

    # Itera sobre cada elemento do array de valores ordenados
    for value in delta_money:
        # Verifica se o valor é negativo
        if value < 0:
            # Incrementa a contagem temporária
            temp_red_run += 1
        else:
            # Se o valor não é negativo, verifica se a contagem temporária é maior que a maior sequência encontrada
            if temp_red_run > biggest_red_run:
                biggest_red_run = temp_red_run

            # Reinicia a contagem temporária
            temp_red_run = 0

    # Verifica novamente após iterar por todo o array, caso a maior sequência esteja no final
    if temp_red_run > biggest_red_run:
        biggest_red_run = temp_red_run

    # Retorna o tamanho da maior sequência de números negativos
    return biggest_red_run


st.markdown("""### 💰Ferramenta de Dimensionamento de Banca""")

col1, col2 = st.columns(2)
# Usar a coluna do meio (col2) para adicionar a entrada de texto
with col1:
    winrate= st.text_input("Qual a Precisão Média do Sistema? (Exemplo: 0.35)", key = "precisao")
with col2:
    odd_media = st.text_input("Qual a Odd média das apostas? (Exemplo: 3.25 )", key = "odd_media")

botao1 = st.button('Calcular Distribuições')

if botao1:
    winrate= float(winrate)
    odd_media = float(odd_media)

    # Roda simulação
    historias = []
    for j in range(5000):
        historia = []
        for i in range(100):
            green = (np.random.uniform(low=0.0, high=1.0, size=None) <= winrate)
            if green == True:
                delta_money = odd_media - 1
            else:
                delta_money = -1
            historia.append(delta_money)
        historias.append(historia)


    # Processa histórias
    historias_acumuladas = []
    unidades = []
    drawdowns = []
    minimo_acumulado = []
    maior_red_run = []

    for historia in historias:
        unidades.append(np.array(historia).sum())
        historia_acumulada = np.array(historia).cumsum()
        historias_acumuladas.append(historia_acumulada)
        drawdowns.append(calculate_max_drawdown(historia_acumulada))
        maior_red_run.append(get_biggest_red_run(historia))
        minimo_acumulado.append(historia_acumulada.min())



    
    # Gráfico de Drawdown
    fig, ax = plt.subplots(figsize=(15,5))
    drawdowns_arr = np.array(drawdowns)
    drawdown_10 = np.percentile(drawdowns_arr,90)
    drawdown_20 = np.percentile(drawdowns_arr,80)
    drawdown_50 = np.percentile(drawdowns_arr,50)

    # Número de bins
    num_bins = 30

    # Valor limite para mudar a cor
    threshold = drawdown_10

    ax.set_title(f'Distribuição de Drawdown - Winrate : {winrate:.2f} e Odd Média de Atuação : {odd_media:.2f} ', pad = 10)

    # Calcule o histograma
    hist, bin_edges, patches = plt.hist(drawdowns_arr, bins=num_bins, alpha=0.5, edgecolor='white', density = True)
    ax.axvline(drawdown_10, color='red', linestyle = '--', label = f'10% de probabilidade do método sofrer um Drawdown superior a {drawdown_10:.2f}')
    ax.axvline(drawdown_20, color='#F6B103', linestyle = '--', label = f'20% de probabilidade do método sofrer um Drawdown superior a {drawdown_20:.2f}')
    ax.axvline(drawdown_50, color='green', linestyle = '--', label = f'50% de probabilidade do método sofrer um Drawdown superior a {drawdown_50:.2f}')

    # Atualize as cores de acordo com o limite estabelecido
    for i, patch in enumerate(patches):
        left_bin_edge = bin_edges[i]
        if left_bin_edge >= threshold:
            patch.set_fc('red')
        else:
            patch.set_fc('green')

    plt.xlabel('Drawdown')
    plt.ylabel('Densidade de Probabilidade')
    ax.legend()
    plt.show()
    st.pyplot(fig)

     # Gráfico de RedRun
    fig, ax = plt.subplots(figsize=(15,5))
    maior_red_run_arr = np.array(maior_red_run)
    redrun_10 = np.percentile(maior_red_run_arr,90)
    redrun_20 = np.percentile(maior_red_run_arr,80)
    redrun_50 = np.percentile(maior_red_run_arr,50)

    # Número de bins
    num_bins = 20

    # Valor limite para mudar a cor
    threshold = redrun_10

    ax.set_title(f'Distribuição de Bad Run - Winrate : {winrate:.2f} e Odd Média de Atuação : {odd_media:.2f} ', pad = 10)

    # Calcule o histograma
    hist, bin_edges, patches = plt.hist(maior_red_run_arr, bins=num_bins, alpha=0.5, edgecolor='white', density = True)
    ax.axvline(redrun_10, color='red', linestyle = '--', label = f'10% de probabilidade do método sofrer uma Bad run superior a {redrun_10:.2f}')
    ax.axvline(redrun_20, color='#F6B103', linestyle = '--', label = f'20% de probabilidade do método sofrer um Bad run superior a {redrun_20:.2f}')
    ax.axvline(redrun_50, color='green', linestyle = '--', label = f'50% de probabilidade do método sofrer um Bad run superior a {redrun_50:.2f}')

    # Atualize as cores de acordo com o limite estabelecido
    for i, patch in enumerate(patches):
        left_bin_edge = bin_edges[i]
        if left_bin_edge >= threshold:
            patch.set_fc('red')
        else:
            patch.set_fc('green')

    plt.xlabel('Maior Bad Run em 100 Bets')
    plt.ylabel('Densidade de Probabilidade')
    ax.legend()
    plt.show()
    st.pyplot(fig)


    fig2, ax = plt.subplots(figsize=(15,5))
    minimo_arr = np.array(minimo_acumulado)
    minimo_90 = np.percentile(minimo_arr,10)
    minimo_95 = np.percentile(minimo_arr,5)
    minimo_80 = np.percentile(minimo_arr,20)

    minimo_50 = np.percentile(minimo_arr,50)


    # Número de bins
    num_bins = 30
    # Valor limite para mudar a cor
    threshold = minimo_95

    ax.set_title(f'Distribuição de Saldo Mínimo - Winrate : {winrate:.2f} e Odd Média de Atuação : {odd_media:.2f} ', pad = 10)
    # Calcule o histograma
    hist, bin_edges, patches = plt.hist(minimo_arr, bins=num_bins, alpha=0.5, edgecolor='white', density = True)
    ax.axvline(minimo_90, color='#F6B103', linestyle = '--', label = f'90% de probabilidade do método não assumir um saldo mínimo menor que {minimo_90:.2f}')
    ax.axvline(minimo_95, color='red', linestyle = '--', label = f'95% de probabilidade do método não assumir um saldo mínimo menor que {minimo_95:.2f}')
    ax.axvline(minimo_50, color='green', linestyle = '--', label = f'50% de probabilidade do método não assumir um saldo mínimo menor que {minimo_50:.2f}')

    # Atualize as cores de acordo com o limite estabelecido
    for i, patch in enumerate(patches):
        left_bin_edge = bin_edges[i]
        if left_bin_edge >= threshold:
            patch.set_fc('green')
        else:
            patch.set_fc('red')

    plt.xlabel('Mínimo')
    plt.ylabel('Densidade de Probabilidade')
    ax.legend()
    st.pyplot(fig2)

    st.markdown('-**Sugestões de dimensionamento de Banca.**')
    st.write(f'Sugestão conservadora - 95% de Probabilidade de Sobreviver 100 Apostas: {np.abs(minimo_95):.1f} Unidades de Saldo Inicial ')
    st.write(f'Sugestão moderada - 90% de Probabilidade de Sobreviver 100 Apostas  : {np.abs(minimo_90):.1f} Unidades de Saldo Inicial ')
    st.write(f'Sugestão agressiva - 80% de Probabilidade de Sobreviver 100 Apostas : {np.abs(minimo_80):.1f} Unidades de Saldo Inicial ')
    st.markdown('⚡**Atenção**⚡: O cálculo acima depende da não deterioração da Precisão do sistema.')

    

    

