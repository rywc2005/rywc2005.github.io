import os
import yaml

def scan_docs(docs_dir='docs'):
    nav = []
    for root, dirs, files in os.walk(docs_dir):
        # 按目录层级排序
        dirs.sort()
        files.sort()
        # 排除隐藏文件和 README.md
        files = [f for f in files if not f.startswith('.') and f != 'README.md']
        # 构建导航项
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                nav_entry = {os.path.splitext(file)[0]: rel_path}
                if root != docs_dir:  # 处理子目录
                    parent_dir = os.path.basename(root)
                    nav.append({parent_dir: [nav_entry]})
                else:
                    nav.append(nav_entry)
    return nav

# 更新 mkdocs.yml
with open('mkdocs.yml', 'r+') as f:
    config = yaml.safe_load(f)
    config['nav'] = scan_docs()
    f.seek(0)
    yaml.dump(config, f, sort_keys=False)