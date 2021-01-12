import os
import json
import pickle

from py2neo import Graph, Node

from lib.life import Life
from lib.utils import write_to_file
from lib.mapping import PREFIX_LABEL_MAP, PREFIX_S_REL_MAP, PREFIX_V_REL_MAP
from const import URI, USERNAME, PASSWORD


class CivilAviationKnowledgeGraph:

    def __init__(self):
        self.data_path = "./data/data.json"
        self.export_dir = "./data/dicts/"

        self.graph = Graph(URI, auth=(USERNAME, PASSWORD))
        self.life = Life()
        self.entities = {}  # 收集实体
        self.attrs = {}  # 实体属性
        self.rels_structures = set()  # 实体结构关系
        self.rels_structures_life = {}  # 实体结构关系的生命周期
        self.rels_values = []  # 实体值关系
        self.cur_value_rel_src = None  # 记录值关系的源节点
        self.cur_index_name = None  # 记录当前指标名称

    def collect(self):
        print("开始收集数据...")
        with open(self.data_path, 'r', encoding='gbk') as fp:
            data = json.load(fp)
            # 开始以递归方式收集数据
            self._travel(data, first_time=True)
        print("数据收集完毕!")

    def _travel(self, objs: dict, parent: tuple = None, first_time=False):
        for fields, entities in objs.items():
            # 分离前缀和实体名
            prefix, name = fields.split('-')
            if first_time:
                self.life.encode(name)
                self.cur_value_rel_src = (prefix, name)
            if prefix == 'I' and entities.get("next"):
                self.cur_index_name = name
            # 获取实体属性
            attrs = entities.get("attrs")
            if attrs:
                self.collect_attrs(name, attrs)
            # 获取下一层实体
            next_ = entities.get("next")
            # 获取关系
            rels = entities.get("rels")

            self.collect_entity(prefix, name)
            if parent:
                self.collect_structure_rel(parent, (prefix, name))
            if rels:
                self.collect_value_rel((prefix, name), rels)
            if next_:
                self._travel(next_, (prefix, name))

    def collect_entity(self, key: str, name: str):
        """ 收集实体 """
        self.entities.setdefault(key, set()).add(name)

    def collect_attrs(self, name: str, attrs: dict):
        """ 收集实体的属性 """
        self.attrs[name] = attrs

    def collect_structure_rel(self, src: tuple, dst: tuple):
        """ 收集实体结构关系 """
        key = (src[0] + '-' + dst[0], src[1], dst[1])
        self.rels_structures.add(key)
        # 计算生命周期
        life = self.rels_structures_life.get(key)
        code = self.life.get_life(self.cur_value_rel_src[1])
        if life is None:
            self.rels_structures_life[key] = code
        else:
            if not self.life.live(code, life):
                self.rels_structures_life[key] = self.life.extend_life(life, code)

    def collect_value_rel(self, dst: tuple, attrs: dict):
        """ 收集实体值关系 """
        if dst[0] == 'A':
            # Year-Area($Index$)
            attrs['name'] = self.cur_index_name
        self.rels_values.append((self.cur_value_rel_src[0] + '-' + dst[0],
                                 self.cur_value_rel_src[1], dst[1], attrs))

    def build(self):
        """ 从收集的数据中构建知识图谱 """
        print("开始构建实体...")
        self.build_nodes()
        print("实体构建完毕!")

        print("开始构建关系...")
        self.build_relationships()
        print("关系构建完毕!")

    def build_nodes(self):
        """ 构建实体结点 """
        for prefix, nodes in self.entities.items():
            label = PREFIX_LABEL_MAP[prefix]
            for name in nodes:
                self.create_node(label, name, self.attrs.get(name))

    def build_relationships(self):
        """ 构建实体关系 """
        for (prefix, src, dst) in self.rels_structures:
            a, b = prefix.split('-')
            la = PREFIX_LABEL_MAP[a]
            lb = PREFIX_LABEL_MAP[b]
            rel = PREFIX_S_REL_MAP[prefix]
            self.create_relationship(la, lb, src, dst, rel,
                                     {'life': self.rels_structures_life[(prefix, src, dst)]})

        for (prefix, src, dst, attrs) in self.rels_values:
            a, b = prefix.split('-')
            la = PREFIX_LABEL_MAP[a]
            lb = PREFIX_LABEL_MAP[b]
            rel = PREFIX_V_REL_MAP[prefix]
            self.create_relationship(la, lb, src, dst,
                                     rel if rel else attrs['name'], attrs)

    def create_node(self, label: str, name: str, attrs=None):
        """ 创建结点 """
        if attrs is None:
            attrs = {}
        node = Node(label, name=name, **attrs)
        self.graph.create(node)

    def create_relationship(self, src_label: str, dst_label: str, src: str, dst: str, rel: str, attrs=None):
        """ 创建关系 """
        if attrs:
            rel_attrs = ", ".join([f"{k}: '{v}'" for k, v in attrs.items()])
        else:
            rel_attrs = "name:'%s'" % rel
        query = f"match(s:{src_label}),(d:{dst_label}) where s.name='{src}' and d.name='{dst}' " \
                f"create (s)-[rel:{rel} {{{rel_attrs}}}]->(d)"
        try:
            self.graph.run(query)
        except Exception as err:
            print(err)

    def export_collections(self):
        """ 导出收集的实体 """
        if not os.path.exists(self.export_dir):
            os.mkdir(self.export_dir)
        for key, values in self.entities.items():
            write_to_file(f"./data/dicts/{PREFIX_LABEL_MAP[key]}.txt", values)
        print("导出实体数据完毕.")

    def export_fast_index_table(self):
        """ 导出指标快表 """
        striped = ['的', '比', '一', '三', '0', '1', '与', '年', '占', '有', '增', '长',
                   '减', '大', '小', '上', '直', '和', '~', '为', '实', '现', '双', '原',
                   '全', '额', '计', '部', '个', '地', '区', '行', '目', '基', '例', '常',
                   '时', '国', '内', '港', '澳', '台', '际']
        fast_table = set(''.join(self.entities['I']))
        for char in striped:
            fast_table.remove(char)
        write_to_file("./data/dicts/fast_index_table.txt", [''.join(fast_table)])

    def export_life_code(self):
        """ 导出生命周期编码 """
        with open("./data/dicts/life.pk", 'wb') as f:
            pickle.dump(self.life, f)


if __name__ == '__main__':
    cakg = CivilAviationKnowledgeGraph()
    cakg.collect()
    cakg.build()
    cakg.export_collections()
    cakg.export_fast_index_table()
    cakg.export_life_code()
