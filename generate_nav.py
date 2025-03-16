import os
import yaml
from collections import defaultdict

def scan_docs(docs_dir='docs'):
    """
    动态扫描文档目录，生成 MkDocs 导航配置
    改进点：
    - 使用 defaultdict 合并同一父目录下的文件
    - 支持中文字符路径处理
    """
    nav = []
    dir_map = defaultdict(list)  # 用于合并子目录项

    # 遍历 docs 目录（按字母顺序排序）
    for root, dirs, files in os.walk(docs_dir, topdown=True):
        # 排序处理（兼容中文字符）
        dirs.sort(key=lambda x: x.encode('utf-8'))
        files.sort(key=lambda x: x.encode('utf-8'))

        # 过滤隐藏文件和 README.md
        files = [f for f in files if not f.startswith('.') and f != 'README.md']
        
        current_dir = os.path.relpath(root, docs_dir)
        
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.join(current_dir, file) if current_dir != '.' else file
                title = os.path.splitext(file)[0]
                
                # 如果是子目录，记录到 dir_map
                if current_dir != '.':
                    parent_dir = os.path.split(current_dir)[-1]
                    dir_map[parent_dir].append({title: rel_path})
                else:
                    nav.append({title: rel_path})

    # 合并子目录项
    for dir_name, entries in dir_map.items():
        nav.append({dir_name: entries})
    
    return nav


def update_mkdocs_config():
    """
    更新 mkdocs.yml 配置，修复编码问题
    改进点：
    - 显式指定 UTF-8 编码读写文件
    - 添加异常处理和文件截断逻辑
    """
    try:
        # 读取时指定 UTF-8 编码[1,5](@ref)
        with open('mkdocs.yml', 'r+', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}  # 处理空文件情况
            config['nav'] = scan_docs()
            
            # 重置文件指针并截断旧内容
            f.seek(0)
            f.truncate()
            
            # 写入时允许 Unicode 字符[8](@ref)
            yaml.dump(
                config, f,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False
            )
    except UnicodeDecodeError as e:
        # 编码回退策略：尝试 GBK 编码[5](@ref)
        print(f"警告：UTF-8 解码失败，尝试 GBK 编码。错误详情：{e}")
        with open('mkdocs.yml', 'r+', encoding='gbk') as f:
            config = yaml.safe_load(f) or {}  # 处理空文件情况
            config['nav'] = scan_docs()
            
            # 重置文件指针并截断旧内容
            f.seek(0)
            f.truncate()
            
            # 写入时允许 Unicode 字符
            yaml.dump(
                config, f,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False
            )
    except Exception as e:
        print(f"严重错误：{str(e)}")


if __name__ == "__main__":
    update_mkdocs_config()