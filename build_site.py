# coding=utf-8
import os
import json
import glob
from pathlib import Path

import markdown  # 需要 pip install markdown

ROOT = Path(__file__).parent
MD_DIR = ROOT / "md"
TITLE_MAP_FILE = ROOT / "thread_title_map.json"
OUT_DIR = ROOT / "board_info"
POSTS_DIR = OUT_DIR / "posts"

with open("thread_title_map.json", "r", encoding="utf-8") as f:
    title_map = json.load(f)


def load_title_map():
    if not TITLE_MAP_FILE.exists():
        print("thread_title_map.json 不存在，请先上传该文件。")
        return {}
    with open(TITLE_MAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_index_page(posts_meta, title_map):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    items_html = ""
    # 按照映射表的顺序来遍历
    for tid, title in title_map.items():
        items_html += f"""
        <div class="post-item">
          <a href="posts/{tid}.html" class="post-link">
            <span class="post-title">{title}</span>
            <span class="post-id">#{tid}</span>
          </a>
        </div>
        """

    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>板块帖子列表</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="site-header">
    <h1>板块帖子列表</h1>
  </header>
  <main class="main-container">
    <div id="post-list">
      {items_html}
    </div>
  </main>
</body>
</html>
"""
    with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

# 按帖子id排序如下
# def build_index_page(posts_meta):
#     OUT_DIR.mkdir(parents=True, exist_ok=True)

#     posts_meta_sorted = sorted(posts_meta, key=lambda x: x["threadid"], reverse=True)

#     items_html = ""
#     for p in posts_meta_sorted:
#         items_html += f"""
#         <div class="post-item">
#           <a href="posts/{p['threadid']}.html" class="post-link">
#             <span class="post-title">{p['title']}</span>
#             <span class="post-id">#{p['threadid']}</span>
#           </a>
#         </div>
#         """

#     index_html = f"""<!DOCTYPE html>
# <html lang="zh-CN">
# <head>
#   <meta charset="UTF-8">
#   <title>板块帖子列表</title>
#   <link rel="stylesheet" href="style.css">
# </head>
# <body>
#   <header class="site-header">
#     <h1>板块帖子列表</h1>
#   </header>
#   <main class="main-container">
#     <div id="post-list">
#       {items_html}
#     </div>
#   </main>
# </body>
# </html>
# """
#     with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
#         f.write(index_html)

# 懒加载代码如下
# def build_post_pages(title_map):
#     POSTS_DIR.mkdir(parents=True, exist_ok=True)
#     posts_meta = []

#     for md_file in sorted(MD_DIR.glob("*.md")):
#         threadid = md_file.stem
#         title = title_map.get(threadid, f"Thread {threadid}")

#         with open(md_file, "r", encoding="utf-8") as f:
#             md_text = f.read()

#         html_body = markdown.markdown(
#             md_text,
#             extensions=["extra", "tables", "fenced_code"]
#         )

#         post_html = f"""<!DOCTYPE html>
# <html lang="zh-CN">
# <head>
#   <meta charset="UTF-8">
#   <title>{title}</title>
#   <link rel="stylesheet" href="../style.css">
# </head>
# <body>
#   <header class="site-header">
#     <h1><a href="../index.html">板块帖子列表</a></h1>
#   </header>
#   <main class="post-container">
#     <article class="post">
#       <h2 class="post-title">{title}</h2>
#       <div class="post-content">
#         {html_body}
#       </div>
#     </article>
#   </main>
# </body>
# </html>
# """
#         out_file = POSTS_DIR / f"{threadid}.html"
#         with open(out_file, "w", encoding="utf-8") as f:
#             f.write(post_html)

#         posts_meta.append({
#             "threadid": threadid,
#             "title": title
#         })

#     return posts_meta


def build_index_page(posts_meta):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 简单懒加载：初始只显示前 20 条，点击“加载更多”再显示后面的
    posts_meta_sorted = sorted(posts_meta, key=lambda x: x["threadid"], reverse=True)
    posts_json = json.dumps(posts_meta_sorted, ensure_ascii=False)

    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>板块帖子列表</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="site-header">
    <h1>板块帖子列表</h1>
  </header>
  <main class="main-container">
    <div id="post-list"></div>
    <button id="load-more-btn">加载更多</button>
  </main>

  <script>
    const allPosts = {posts_json};
    const pageSize = 20;
    let currentIndex = 0;

    function renderMore() {{
      const list = document.getElementById('post-list');
      const end = Math.min(currentIndex + pageSize, allPosts.length);
      for (let i = currentIndex; i < end; i++) {{
        const p = allPosts[i];
        const item = document.createElement('div');
        item.className = 'post-item';
        item.innerHTML = `
          <a href="posts/${{p.threadid}}.html" class="post-link">
            <span class="post-title">${{p.title}}</span>
            <span class="post-id">#${{p.threadid}}</span>
          </a>
        `;
        list.appendChild(item);
      }}
      currentIndex = end;
      if (currentIndex >= allPosts.length) {{
        document.getElementById('load-more-btn').style.display = 'none';
      }}
    }}

    document.getElementById('load-more-btn').addEventListener('click', renderMore);

    // 初次加载
    renderMore();
  </script>
</body>
</html>
"""
    with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)


def build_style():
    css = """
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Microsoft YaHei", sans-serif;
  margin: 0;
  padding: 0;
  background: #f5f5f7;
  color: #222;
}

a {
  color: #0366d6;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.site-header {
  background: #24292e;
  color: #fff;
  padding: 16px 24px;
}

.site-header h1 {
  margin: 0;
  font-size: 20px;
}

.site-header a {
  color: #fff;
  text-decoration: none;
}

.main-container {
  max-width: 900px;
  margin: 24px auto;
  padding: 0 16px 40px;
}

#post-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.post-item {
  background: #fff;
  border-radius: 6px;
  padding: 10px 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.post-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-title {
  font-size: 15px;
}

.post-id {
  font-size: 12px;
  color: #666;
}

#load-more-btn {
  margin: 16px auto 0;
  display: block;
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid #ccc;
  background: #fff;
  cursor: pointer;
}

#load-more-btn:hover {
  background: #f0f0f0;
}

.post-container {
  max-width: 900px;
  margin: 24px auto;
  padding: 0 16px 40px;
}

.post-title {
  font-size: 22px;
  margin-bottom: 16px;
}

.post-content {
  background: #fff;
  border-radius: 6px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.post-content h1,
.post-content h2,
.post-content h3 {
  margin-top: 1.2em;
}

.post-content p {
  line-height: 1.6;
  margin: 0.5em 0;
}

.post-content pre {
  background: #f6f8fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.post-content code {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
"""
    with open(OUT_DIR / "style.css", "w", encoding="utf-8") as f:
        f.write(css)


def main():
    title_map = load_title_map()
    posts_meta = build_post_pages(title_map)
    build_index_page(posts_meta)
    build_style()
    print("静态站点构建完成：board_info/")


if __name__ == "__main__":
    main()
