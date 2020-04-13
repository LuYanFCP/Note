# NetworkX的简要使用

## NetworkX基础知识

```python
import networkx as nx
```

图的种类：

1. 有向图: `G = nx.Graph()`
2. 无向图: `G = nx.DiGraph()`
3. 混合图: `G = nx.MultiGraph()`
4. 多图表的定向版本 `G = nx.MultiDiGraph()`

可以根据自己的需求进行图选择， `Multixx`为多条边的图。

所有图的节点要求节点是可hash的。

**图形内部数据结构基于邻接列表表示，并使用Python字典数据结构实现。图邻接结构被实现为Python词典字典。外部字典由节点键入自己的值，而这些字典本身就是由相邻节点键入与该边缘关联的边缘属性的字典。**

这样做的有点是可以快速的快速添加，删除和查找节点和邻居。

### 创建图

创建图有三种方式

1. 图生成器-创建网络拓扑的标准算法。
2. 从预先存在的（通常是文件）源中导入数据。
3. 显式添加边缘和节点。

#### 显式添加图

```python
import networkx as nx
G = nx.Graph()
G.add_node(0, name='0')  # G.add_node(n, object=x)
G.add_edge(1, 2)
G.add_edge(2, 3, weight=0.9)  # 添加特定的权重
# G.add_edge(n1，n2，object=x) 可以使用不同的边上的权重

# 可以通过add_xxx_from从可迭代的对象中添加节点
elist = [(1, 2), (2, 3), (1, 4), (4, 2)]
G.add_edges_from(elist)
elist = [('a', 'b', 5.0), ('b', 'c', 3.0), ('a', 'c', 1.0), ('c', 'd', 7.3)]
G.add_weighted_edges_from(elist)
```

Graph、node、edge都可以添加很多的属性，其中`Graph`的属性在创建的`Graph`的时候，直接指定，也可以给之后的过程进行指定`G.graphp[key]=val`

node可以添加任何属性, 可以通过`G.add_node(n, object=x)`进行添加。也可以通过`G[n][key]=val`进行修改。

可以通过`G.add_edge(n1，n2，object=x)`给边添加任何属性。`weight`是默认的属性，必须是数字，被用作一些算法中。

#### 图生成器

图生成器子包中提供了诸如binomial_graph() 和erdos_renyi_graph()之类的图生成器。

例子：使用生成器生成平衡二叉树

```python
G = generators.classic.balanced_tree(r=2, h=5)  # r为树的阶，h为树的高度
```

### 从文件中导入

支持各种格式包括`Edge List`、`GEXF`、`Pickle`、`GraphML`、`JSON`、`LEDA`、`YAML`、`SparseGraph6`、`Pajek`。可以从`networkx.readwrite`部分找到这些接口，这些接口可以方便读取和存储图。

## 图遍历

这些视图提供了属性的迭代以及成员资格查询和数据属性查找。视图引用图形数据结构，因此对图形的更改会反映在视图中。这类似于Python3中的字典视图。如果要在迭代时更改图形，则需要使用例如对于列表中的e（G.edges）：。视图提供类似集合的操作，例如合并和交集，以及使用G.`edges[u，v]['color']`进行类似dict的数据属性查找和迭代，对于e，使用`for e, datadict in G.edges.items():`对边进行遍历。 `python dicts`熟悉方法`G.edges.items()`和`G.edges.values()`。另外`G.edges.data()`提供了对特定的属性迭代，例如对`color`属性的遍历`e, e_color in G.edges.data('color'):`。

按properties提供边，邻接和度数。例如`nx.triangles(G，n)`给出包含节点n作为顶点的三角形的数量。

## 图算法

NetworkX提供了许多图形算法。这些包括最短路径和遍历（dfs，bfs，Beam search），聚类和同构算法等。

例如DFS就可以通过如下方式访问：

```python
G = nx.Graph()
e = [('a', 'b', 0.3), ('b', 'c', 0.9), ('a', 'c', 0.5), ('c', 'd', 1.2)]
G.add_weighted_edges_from(e)
print(nx.dijkstra_path(G, 'a', 'd'))
# ['a', 'c', 'd']
```

## 可视化

Networkx提供了简单的可视化，使用matplotlib进行绘制图像

如下为示例

```python
import networkx as nx
import matplotlib.pyplot as plt
G = nx.generators.classic.balanced_tree(r=2, h=3)
nx.draw(G)
plt.show()
```