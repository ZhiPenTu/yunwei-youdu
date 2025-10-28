import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import networkx as nx
from collections import defaultdict

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def fetch_zt_pool_data():
    """获取涨停板池数据"""
    try:
        df = ak.stock_zt_pool_em(date="20250704")  # 替换为最新日期
        print("获取数据成功！记录数:", len(df))
        print(df.head())

        stock_board_concept_name_em_df = ak.stock_board_concept_name_em()
        print(stock_board_concept_name_em_df)
        return df
    except Exception as e:
        print("获取数据失败:", e)
        return None

# 功能1：探索涨停池中个股的涨幅高度
def analyze_zt_height(df):
    """分析连板数分布"""
    print("\n===== 涨停高度分析 =====")
    
    # 添加连板天数排名
    df['连板天数排名'] = df['连板数'].rank(method='min', ascending=False).astype(int)
    
    # 输出龙头股信息
    top3 = df.nlargest(3, '连板数')[['名称', '连板数', '最新价', '所属行业']]
    print("\n涨停高度TOP3:\n", top3)
    
    # 可视化
    plt.figure(figsize=(12, 6))
    
    # 连板天数分布直方图
    plt.subplot(121)
    sns.histplot(df['连板数'], bins=15, kde=True)
    plt.title('连板天数分布')
    plt.xlabel('连板数')
    
    # TOP10个股展示
    plt.subplot(122)
    top10 = df.nlargest(10, '连板数')
    sns.barplot(x='连板数', y='名称', data=top10)
    plt.title('连板天数TOP10')
    plt.tight_layout()
    plt.savefig('涨停高度分析.png')
    plt.show()

# 功能2：探索板块延展性
def analyze_sector_extension(df):
    """分析板块延展性"""
    print("\n===== 板块延展性分析 =====")
    
    # 解包多重概念板块
    concept_counts = defaultdict(int)
    all_relations = []
    
    for _, row in df.iterrows():
        concepts = [c.strip() for c in str(row['所属概念']).split(',') if c.strip()]
        industry = row['所属行业']
        
        # 统计概念板块频次
        for concept in concepts:
            concept_counts[concept] += 1
            
            # 收集行业-概念关系
            all_relations.append({'行业': industry, '概念': concept})
    
    # 转换为DataFrame
    relations_df = pd.DataFrame(all_relations)
    
    # 可视化1：热门概念板块TOP10
    plt.figure(figsize=(12, 5))
    top_concepts = pd.Series(concept_counts).sort_values(ascending=False).head(10)
    sns.barplot(x=top_concepts.values, y=top_concepts.index)
    plt.title('热门概念板块TOP10')
    plt.xlabel('涨停股数量')
    plt.savefig('热门概念板块.png')
    plt.show()
    
    # 可视化2：行业-概念关联网络
    plt.figure(figsize=(14, 10))
    G = nx.Graph()
    
    # 添加行业节点（蓝色）
    industries = df['所属行业'].unique()
    for industry in industries:
        G.add_node(industry, node_color='skyblue', node_size=500)
    
    # 添加概念节点（橙色）和边
    for concept in top_concepts.index:
        G.add_node(concept, node_color='orange', node_size=200 + concept_counts[concept]*10)
        
        # 添加关联边
        linked_industries = relations_df[relations_df['概念'] == concept]['行业'].unique()
        for industry in linked_industries:
            G.add_edge(industry, concept)
    
    # 绘制网络
    node_colors = [G.nodes[n]['node_color'] for n in G.nodes]
    node_sizes = [G.nodes[n]['node_size'] for n in G.nodes]
    
    pos = nx.spring_layout(G, k=0.5)
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, 
            node_color=node_colors, alpha=0.7, edge_color='gray', 
            font_size=10, width=1.5)
    plt.title('行业-概念关联网络')
    plt.savefig('行业概念关联网络.png')
    plt.show()

# 功能3：探索板块关联关系
def analyze_sector_relations(df):
    """分析行业板块和概念板块的关联"""
    print("\n===== 板块关联关系分析 =====")
    
    # 创建板块关联矩阵
    concept_list = []
    industry_list = df['所属行业'].unique().tolist()
    
    for concepts in df['所属概念'].str.split(','):
        if isinstance(concepts, list):
            concept_list.extend([c.strip() for c in concepts if c.strip()])
    
    # 过滤出现频次低的概念
    concept_counts = pd.Series(concept_list).value_counts()
    top_concepts = concept_counts[concept_counts >= 3].index.tolist()
    
    # 创建空矩阵
    relation_matrix = pd.DataFrame(0, index=industry_list, columns=top_concepts)
    
    # 填充关联矩阵
    for _, row in df.iterrows():
        industry = row['所属行业']
        concepts = [c.strip() for c in str(row['所属概念']).split(',') if c.strip() in top_concepts]
        
        for concept in concepts:
            relation_matrix.loc[industry, concept] += 1
    
    # 可视化热度矩阵
    plt.figure(figsize=(16, 12))
    sns.heatmap(relation_matrix.T, cmap="YlGnBu", annot=True, fmt='d', linewidths=.5)
    plt.title('行业-概念板块关联热度图')
    plt.xlabel('行业板块')
    plt.ylabel('概念板块')
    plt.savefig('板块关联热度图.png')
    plt.show()

# 功能4：探索板块强度
def analyze_sector_strength(df):
    """分析板块强度"""
    print("\n===== 板块强度分析 =====")
    
    # 行业板块强度分析
    industry_df = df.groupby('所属行业').agg(
        涨停数量=('名称', 'count'),
        平均连板天数=('连板数', 'mean'),
        平均涨幅=('最新价', lambda x: ((x / x.mean() - 1) * 100).mean())
    ).reset_index()
    
    # 复合强度计算
    scaler = MinMaxScaler()
    industry_df['强度分数'] = (industry_df['涨停数量'] * 0.4 + 
                           industry_df['平均连板天数'] * 0.3 + 
                           industry_df['平均涨幅'] * 0.3)
    
    # 标准化评分
    industry_df['强度分数'] = scaler.fit_transform(industry_df[['强度分数']]) * 100
    
    # 可视化
    plt.figure(figsize=(14, 8))
    top_industries = industry_df.nlargest(15, '强度分数')
    
    # 创建子图网格
    ax = plt.subplot(121)
    sns.barplot(x='强度分数', y='所属行业', data=top_industries, ax=ax)
    ax.set_title('行业板块强度TOP15')
    
    # 三维泡泡图
    ax = plt.subplot(122, projection='3d')
    ax.scatter(top_industries['涨停数量'], 
               top_industries['平均连板天数'], 
               top_industries['平均涨幅'],
               s=top_industries['强度分数']*2,  # 泡泡大小代表强度
               c=top_industries['强度分数'], 
               cmap='coolwarm', 
               alpha=0.7)
    
    # 添加标签
    for i, row in top_industries.iterrows():
        ax.text(row['涨停数量'], row['平均连板天数'], row['平均涨幅'], 
                row['所属行业'], fontsize=9)
    
    ax.set_xlabel('涨停数量')
    ax.set_ylabel('平均连板天数')
    ax.set_zlabel('平均涨幅(%)')
    ax.set_title('板块强度三维分析')
    
    plt.tight_layout()
    plt.savefig('板块强度分析.png')
    plt.show()

# 主函数
def main():
    # 获取数据
    df = fetch_zt_pool_data()
    if df is None or len(df) == 0:
        print("无有效数据，程序退出")
        return
    
    # 执行分析功能
    analyze_zt_height(df.copy())
    analyze_sector_extension(df.copy())
    analyze_sector_relations(df.copy())
    analyze_sector_strength(df.copy())

if __name__ == "__main__":
    main()