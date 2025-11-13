import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime
from pathlib import Path

class VisualizadorFocosPlotly:
    def __init__(self, arquivo_csv=None):
        """
        Inicializa o visualizador
        Procura o arquivo CSV em diferentes locais possíveis
        """
        self.arquivo_csv = self.encontrar_arquivo_csv(arquivo_csv)
        self.df = None
        self.carregar_dados()
    
    def encontrar_arquivo_csv(self, arquivo_fornecido):
        """
        Procura o arquivo CSV em diferentes localizações possíveis
        """
        # Lista de possíveis locais onde o arquivo pode estar
        possiveis_caminhos = []
        
        if arquivo_fornecido:
            # Se um arquivo foi fornecido, adiciona ele primeiro
            possiveis_caminhos.append(arquivo_fornecido)
        
        # Adicionar caminhos padrão baseados na estrutura do projeto
        base_dir = Path.cwd()  # Diretório atual
        
        # Estrutura esperada: APS/output/dados_ordenados.csv
        possiveis_caminhos.extend([
            base_dir / 'output' / 'dados_ordenados.csv',
            base_dir / 'output' / 'dados.csv',
            base_dir / 'dados_ordenados.csv',
            base_dir / '..' / 'output' / 'dados_ordenados.csv',
            Path('output/dados_ordenados.csv'),
            Path('dados_ordenados.csv'),
            Path('../output/dados_ordenados.csv')
        ])
        
        # Procurar o arquivo
        for caminho in possiveis_caminhos:
            caminho = Path(caminho)
            if caminho.exists() and caminho.is_file():
                print(f"Arquivo CSV encontrado em: {caminho.resolve()}")
                return str(caminho.resolve())
        
        # Se não encontrou, listar arquivos disponíveis
        print("Arquivo CSV não encontrado nos locais esperados!")
        print("\nEstrutura atual do diretório:")
        
        # Mostrar estrutura de pastas
        print(f"\nDiretório atual: {base_dir}")
        
        # Verificar se existe pasta output
        output_dir = base_dir / 'output'
        if output_dir.exists():
            print(f"\nConteúdo da pasta 'output':")
            for arquivo in output_dir.iterdir():
                if arquivo.suffix == '.csv':
                    print(f"   - {arquivo.name}")
        else:
            print("Pasta 'output' não encontrada")
        
        # Listar CSVs no diretório atual
        csvs_local = list(base_dir.glob('*.csv'))
        if csvs_local:
            print(f"\nArquivos CSV no diretório atual:")
            for csv in csvs_local:
                print(f"   - {csv.name}")
        
        # Pedir ao usuário o caminho correto
        print("\n" + "="*50)
        caminho_usuario = input("Digite o caminho completo para o arquivo CSV ordenado\n(ou pressione Enter para sair): ").strip()
        
        if caminho_usuario:
            if Path(caminho_usuario).exists():
                return caminho_usuario
            else:
                print(f"Arquivo '{caminho_usuario}' não existe!")
                sys.exit(1)
        else:
            print("\nDicas:")
            print("1. Execute primeiro o programa MergeSort em C")
            print("2. Certifique-se que o arquivo 'dados_ordenados.csv' foi gerado")
            print("3. Verifique se está na pasta 'output'")
            print("\nVocê pode especificar o arquivo ao executar:")
            print("   python visualizador_plotly.py caminho/para/arquivo.csv")
            sys.exit(1)
        
    def carregar_dados(self):
        """Carrega e prepara os dados"""
        try:
            print(f"Carregando dados de: {self.arquivo_csv}")
            
            # Ler CSV
            self.df = pd.read_csv(self.arquivo_csv)
            
            # Limpar espaços
            self.df.columns = self.df.columns.str.strip()
            for col in self.df.select_dtypes(include=['object']).columns:
                self.df[col] = self.df[col].str.strip()
            
            # Converter data
            self.df['data_pas'] = pd.to_datetime(self.df['data_pas'])
            
            # Criar colunas auxiliares
            self.df['mes'] = self.df['data_pas'].dt.month
            self.df['mes_nome'] = self.df['data_pas'].dt.strftime('%B')
            self.df['dia_semana'] = self.df['data_pas'].dt.day_name()
            self.df['hora'] = self.df['data_pas'].dt.hour
            self.df['data'] = self.df['data_pas'].dt.date
            
            print(f"{len(self.df)} registros carregados!")
            print(f"Período: {self.df['data_pas'].min()} até {self.df['data_pas'].max()}")
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            raise
    
    def criar_mapa_interativo(self):
        """Cria mapa interativo com os focos"""
        print("Criando mapa interativo...")
        
        fig = px.scatter_mapbox(
            self.df,
            lat='lat',
            lon='lon',
            hover_name='municipio',
            hover_data={
                'estado': True,
                'bioma': True,
                'data_pas': '|%Y-%m-%d %H:%M',
                'lat': ':.4f',
                'lon': ':.4f'
            },
            color='bioma',
            color_discrete_sequence=px.colors.qualitative.Set1,
            zoom=6,
            height=700,
            title='Focos de Calor - Mapa - Santa Catarina'
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":50,"l":0,"b":0},
            font=dict(family="Arial", size=12)
        )
        
        return fig
    
    def criar_mapa_densidade(self):
        """Cria mapa de densidade (heatmap)"""
        print("Criando mapa de densidade...")
        
        fig = go.Figure(go.Densitymapbox(
            lat=self.df['lat'],
            lon=self.df['lon'],
            radius=15,
            colorscale='Hot',
            showscale=True,
            colorbar=dict(
                title="Densidade",
                thickness=20,
                len=0.7
            )
        ))
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=-27, lon=-50),
                zoom=6
            ),
            height=700,
            title='🌡️ Mapa de Densidade de Focos de Calor',
            margin={"r":0,"t":50,"l":0,"b":0}
        )
        
        return fig
    
    def criar_serie_temporal(self):
        """Cria gráfico de série temporal"""
        print("📈 Criando série temporal...")
        
        # Agrupar por dia
        focos_dia = self.df.groupby('data').size().reset_index(name='focos')
        
        fig = px.line(
            focos_dia,
            x='data',
            y='focos',
            title='📊 Evolução Temporal dos Focos de Calor',
            labels={'focos': 'Número de Focos', 'data': 'Data'},
            markers=True
        )
        
        # Adicionar linha de tendência
        fig.add_trace(go.Scatter(
            x=focos_dia['data'],
            y=focos_dia['focos'].rolling(window=7, center=True).mean(),
            mode='lines',
            name='Média Móvel (7 dias)',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            hovermode='x unified',
            height=500,
            showlegend=True,
            xaxis_title="Data",
            yaxis_title="Número de Focos"
        )
        
        return fig
    
    def criar_top_municipios(self):
        """Cria gráfico dos top municípios"""
        print("🏙️ Criando ranking de municípios...")
        
        top_15 = self.df['municipio'].value_counts().head(15)
        
        fig = px.bar(
            x=top_15.values,
            y=top_15.index,
            orientation='h',
            title='🏆 Top 15 Municípios com Mais Focos de Calor',
            labels={'x': 'Número de Focos', 'y': 'Município'},
            color=top_15.values,
            color_continuous_scale='Reds',
            text=top_15.values
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            height=600,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}
        )
        
        return fig
    
    def criar_analise_temporal_completa(self):
        """Cria análise temporal múltipla"""
        print("🕐 Criando análise temporal completa...")
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribuição por Hora do Dia', 
                          'Distribuição por Dia da Semana',
                          'Distribuição por Mês', 
                          'Heatmap Hora vs Dia da Semana'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'heatmap'}]]
        )
        
        # Por hora
        por_hora = self.df['hora'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(x=por_hora.index, y=por_hora.values, 
                   marker_color='lightblue', name='Por Hora'),
            row=1, col=1
        )
        
        # Por dia da semana
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                     'Friday', 'Saturday', 'Sunday']
        por_dia = self.df['dia_semana'].value_counts().reindex(dias_ordem)
        dias_pt = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        fig.add_trace(
            go.Bar(x=dias_pt, y=por_dia.values, 
                   marker_color='lightgreen', name='Por Dia'),
            row=1, col=2
        )
        
        # Por mês
        meses_nomes = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                      7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        por_mes = self.df['mes'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(x=[meses_nomes[m] for m in por_mes.index], 
                   y=por_mes.values, marker_color='coral', name='Por Mês'),
            row=2, col=1
        )
        
        # Heatmap hora vs dia
        pivot_table = pd.crosstab(self.df['hora'], self.df['dia_semana'])
        pivot_table = pivot_table.reindex(columns=dias_ordem, fill_value=0)
        
        fig.add_trace(
            go.Heatmap(
                z=pivot_table.values,
                x=dias_pt,
                y=list(range(24)),
                colorscale='YlOrRd',
                showscale=True
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="⏰ Análise Temporal Completa dos Focos de Calor"
        )
        
        # Atualizar eixos
        fig.update_xaxes(title_text="Hora", row=1, col=1)
        fig.update_xaxes(title_text="Dia da Semana", row=1, col=2)
        fig.update_xaxes(title_text="Mês", row=2, col=1)
        fig.update_xaxes(title_text="Dia da Semana", row=2, col=2)
        
        fig.update_yaxes(title_text="Focos", row=1, col=1)
        fig.update_yaxes(title_text="Focos", row=1, col=2)
        fig.update_yaxes(title_text="Focos", row=2, col=1)
        fig.update_yaxes(title_text="Hora", row=2, col=2)
        
        return fig
    
    def criar_analise_bioma(self):
        """Cria análise por bioma"""
        print("🌳 Criando análise por bioma...")
        
        # Criar subplot com pizza e barras
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Distribuição por Bioma', 
                          'Evolução Temporal por Bioma'),
            specs=[[{'type': 'pie'}, {'type': 'scatter'}]]
        )
        
        # Pizza
        bioma_counts = self.df['bioma'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=bioma_counts.index,
                values=bioma_counts.values,
                hole=0.3,
                marker=dict(colors=px.colors.sequential.RdBu)
            ),
            row=1, col=1
        )
        
        # Série temporal por bioma
        for bioma in self.df['bioma'].unique():
            df_bioma = self.df[self.df['bioma'] == bioma]
            focos_dia = df_bioma.groupby('data').size()
            
            fig.add_trace(
                go.Scatter(
                    x=focos_dia.index,
                    y=focos_dia.values,
                    mode='lines',
                    name=bioma,
                    line=dict(width=2)
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            height=500,
            title_text="🌿 Análise de Focos por Bioma",
            showlegend=True
        )
        
        return fig
    
    def criar_dashboard_completo(self):
        """Cria dashboard unificado com apenas as visualizações essenciais"""
        print("🎯 Criando dashboard completo...")
        
        # Estatísticas
        total_focos = len(self.df)
        municipios_afetados = self.df['municipio'].nunique()
        periodo_dias = (self.df['data_pas'].max() - self.df['data_pas'].min()).days
        media_diaria = total_focos / max(periodo_dias, 1)
        
        # Criar figura com subplots otimizados
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                '📈 Evolução Temporal dos Focos',
                '🏆 Top 10 Municípios Mais Afetados',
                '🌿 Biomas Afetados por Mês',
                '🗺️ Mapa Interativo de Focos'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'bar'}],
                [{'type': 'bar', 'colspan': 2}, None],
                [{'type': 'scattermapbox', 'colspan': 2}, None]
            ],
            row_heights=[0.25, 0.25, 0.5],
            vertical_spacing=0.08,
            horizontal_spacing=0.12
        )
        
        # 1. EVOLUÇÃO TEMPORAL (mais detalhada)
        focos_dia = self.df.groupby('data').size().reset_index(name='focos')
        
        # Linha principal
        fig.add_trace(
            go.Scatter(
                x=focos_dia['data'], 
                y=focos_dia['focos'],
                mode='lines+markers',
                name='Focos Diários',
                line=dict(color='#FF6B6B', width=2),
                marker=dict(size=6, color='#FF6B6B'),
                hovertemplate='<b>Data:</b> %{x}<br><b>Focos:</b> %{y}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Média móvel
        fig.add_trace(
            go.Scatter(
                x=focos_dia['data'],
                y=focos_dia['focos'].rolling(window=7, center=True).mean(),
                mode='lines',
                name='Média 7 dias',
                line=dict(color='#4ECDC4', width=3, dash='dot'),
                hovertemplate='<b>Média:</b> %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. TOP 10 MUNICÍPIOS (ordenado do mais para o menos afetado)
        top_10 = self.df['municipio'].value_counts().head(10)
        # Inverter ordem para mostrar o mais afetado em cima
        top_10_ordered = top_10.sort_values(ascending=True)
        
        # Criar gradiente de cores
        colors = px.colors.sequential.Reds[3:] * 2  # Usar tons de vermelho
        
        fig.add_trace(
            go.Bar(
                x=top_10_ordered.values,
                y=top_10_ordered.index,
                orientation='h',
                marker=dict(
                    color=top_10_ordered.values,
                    colorscale='Reds',
                    showscale=False,
                    line=dict(color='darkred', width=1)
                ),
                text=[f'{val} focos' for val in top_10_ordered.values],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Focos: %{x}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. BIOMAS AFETADOS POR MÊS (gráfico de barras agrupadas)
        # Criar tabela pivô
        biomas_mes = self.df.groupby(['mes', 'bioma']).size().reset_index(name='focos')
        
        meses_nomes = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                      7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        biomas_mes['mes_nome'] = biomas_mes['mes'].map(meses_nomes)
        
        # Criar uma barra para cada bioma
        biomas_unicos = self.df['bioma'].unique()
        cores_biomas = ['#2E7D32', '#1B5E20', '#4CAF50', '#81C784']  # Tons de verde
        
        for i, bioma in enumerate(biomas_unicos):
            dados_bioma = biomas_mes[biomas_mes['bioma'] == bioma]
            
            # Garantir que todos os meses estejam presentes
            meses_completos = pd.DataFrame({'mes': range(1, 13)})
            meses_completos['mes_nome'] = meses_completos['mes'].map(meses_nomes)
            dados_bioma = meses_completos.merge(
                dados_bioma, on='mes', how='left', suffixes=('', '_y')
            ).fillna(0)
            
            fig.add_trace(
                go.Bar(
                    x=dados_bioma['mes_nome_x'] if 'mes_nome_x' in dados_bioma.columns else dados_bioma['mes_nome'],
                    y=dados_bioma['focos'] if 'focos' in dados_bioma.columns else 0,
                    name=bioma,
                    marker_color=cores_biomas[i % len(cores_biomas)],
                    hovertemplate=f'<b>{bioma}</b><br>Mês: %{{x}}<br>Focos: %{{y}}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # 4. MAPA INTERATIVO (versão original, mais limpa)
        fig.add_trace(
            go.Scattermapbox(
                lat=self.df['lat'],
                lon=self.df['lon'],
                mode='markers',
                marker=dict(
                    size=5,
                    color='red',
                    opacity=0.6
                ),
                text=self.df['municipio'],
                hovertemplate='<b>%{text}</b><br>Lat: %{lat:.4f}<br>Lon: %{lon:.4f}<extra></extra>',
                name='Focos'
            ),
            row=3, col=1
        )
        
        # Configurar layout do mapa
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=-27, lon=-50),
                zoom=6
            ),
            height=1000,
            showlegend=True,
            title={
                'text': "DASHBOARD DE ANÁLISE DE FOCOS DE CALOR - SANTA CATARINA",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2C3E50'}
            },
            paper_bgcolor='#F5F5F5',
            plot_bgcolor='white',
            font=dict(family="Arial", size=12)
        )
        
        # Atualizar eixos
        fig.update_xaxes(title_text="Data", row=1, col=1, showgrid=True, gridcolor='#E0E0E0')
        fig.update_yaxes(title_text="Número de Focos", row=1, col=1, showgrid=True, gridcolor='#E0E0E0')
        
        fig.update_xaxes(title_text="Número de Focos", row=1, col=2, showgrid=True, gridcolor='#E0E0E0')
        fig.update_yaxes(title_text="", row=1, col=2, showgrid=False)
        
        fig.update_xaxes(title_text="Mês", row=2, col=1, showgrid=False)
        fig.update_yaxes(title_text="Número de Focos", row=2, col=1, showgrid=True, gridcolor='#E0E0E0')
        
        # Adicionar anotação com estatísticas
        stats_text = f"""
        <b>📊 ESTATÍSTICAS GERAIS</b><br>
        Total de Focos: {total_focos}<br>
        Municípios Afetados: {municipios_afetados}<br>
        Período: {periodo_dias} dias<br>
        Média Diária: {media_diaria:.1f} focos
        """
        
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="white",
            bordercolor="#2C3E50",
            borderwidth=2,
            font=dict(size=11),
            align="left"
        )
        
        return fig
    
    def salvar_todas_visualizacoes(self, pasta='visualizacoes'):
        """Salva e abre diretamente o dashboard"""
        
        # Criar pasta se não existir
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            
        print(f"\n💾 Gerando Dashboard...")
        
        # Gerar o dashboard
        dashboard = self.criar_dashboard_completo()
        
        # Salvar dashboard diretamente como index.html para abrir direto
        caminho = os.path.join(pasta, 'dashboard.html')
        caminho_index = os.path.join(pasta, 'index.html')
        
        # Salvar em ambos os arquivos (dashboard.html e index.html)
        dashboard.write_html(caminho)
        dashboard.write_html(caminho_index)  # Salva também como index para abrir direto
        
        print(f"   ✅ Dashboard salvo!")
        print(f"\n🎉 Dashboard gerado com sucesso!")
        print(f"📂 Arquivo: {caminho}")
        
        return caminho_index  # Retorna o caminho do index para abrir


# Função principal
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visualizador de Focos de Calor com Plotly',
        epilog='Exemplo: python visualizador_plotly.py output/dados_ordenados.csv'
    )
    parser.add_argument(
        'arquivo', 
        nargs='?', 
        default=None,
        help='Caminho para o arquivo CSV ordenado (ex: output/dados_ordenados.csv)'
    )
    parser.add_argument(
        '--output', '-o',
        default='visualizacoes',
        help='Pasta de saída para os HTMLs (padrão: visualizacoes)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🔥 VISUALIZADOR PLOTLY - FOCOS DE CALOR")
    print("="*60)
    print(f"📍 Diretório de trabalho: {os.getcwd()}")
    
    # Criar visualizador (ele vai procurar o arquivo automaticamente)
    try:
        vis = VisualizadorFocosPlotly(args.arquivo)
        
        # Salvar dashboard
        dashboard_path = vis.salvar_todas_visualizacoes(args.output)
        
        print("\n✨ Dashboard gerado com sucesso!")
        print(f"🌐 Abrindo dashboard no navegador...")
        
        # Tentar abrir automaticamente no navegador
        import webbrowser
        if Path(dashboard_path).exists():
            try:
                webbrowser.open(str(Path(dashboard_path).resolve()))
                print("🚀 Dashboard aberto!")
            except:
                print(f"⚠️  Não foi possível abrir automaticamente.")
                print(f"📂 Abra manualmente: {dashboard_path}")
    
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        print("\n💡 Verifique se:")
        print("   1. O arquivo CSV foi gerado pelo MergeSort")
        print("   2. O arquivo está na pasta 'output'")
        print("   3. Você tem as bibliotecas instaladas (pandas, plotly)")
        sys.exit(1)

if __name__ == "__main__":
    main()