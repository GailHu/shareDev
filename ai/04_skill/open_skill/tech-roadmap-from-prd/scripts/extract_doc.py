"""提取 .docx 的正文、表格与内嵌图片。

用法:
    python extract_doc.py <docx路径> <输出目录>

输出:
    <输出目录>/content.txt   正文段落与表格（表格按 " | " 分隔单元格）
    <输出目录>/media/        内嵌图片，按文档中的原始名称保存

仅依赖标准库，无需安装第三方包。
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TEXT_TAG = "{%s}t" % WORD_NS
STYLE_VAL_ATTR = "{%s}val" % WORD_NS
NS = {"w": WORD_NS}


def read_paragraph_text(paragraph):
    """拼接一个段落内的所有文本片段。"""
    return "".join(run.text or "" for run in paragraph.iter(TEXT_TAG))


def read_paragraph_style(paragraph):
    """读取段落样式名，用于识别标题层级。"""
    style = paragraph.find("w:pPr/w:pStyle", NS)
    return style.get(STYLE_VAL_ATTR) if style is not None else ""


def extract_body(archive):
    """遍历文档主体，输出段落与表格的纯文本行。"""
    document_root = ET.fromstring(archive.read("word/document.xml"))
    body = document_root.find("w:body", NS)
    if body is None:
        return []

    output_lines = []
    for node in body:
        tag_name = node.tag.split("}")[-1]
        if tag_name == "p":
            text = read_paragraph_text(node).strip()
            if not text:
                continue
            # 标题段落加前缀，便于阅读时快速定位章节
            if read_paragraph_style(node).lower().startswith("heading"):
                output_lines.append("\n### %s" % text)
            else:
                output_lines.append(text)
        elif tag_name == "tbl":
            output_lines.append("\n--- 表格开始 ---")
            for row in node.findall("w:tr", NS):
                cells = []
                for cell in row.findall("w:tc", NS):
                    # 单元格内可能有多个段落，合并为一格
                    cells.append(
                        " ".join(
                            read_paragraph_text(p).strip()
                            for p in cell.findall("w:p", NS)
                        ).strip()
                    )
                output_lines.append(" | ".join(cells))
            output_lines.append("--- 表格结束 ---\n")
    return output_lines


def extract_media(archive, media_dir):
    """导出 word/media 下的全部内嵌图片，返回文件名列表。"""
    saved_names = []
    for entry in archive.infolist():
        if entry.is_dir() or not entry.filename.startswith("word/media/"):
            continue
        file_name = os.path.basename(entry.filename)
        if not file_name:
            continue
        with archive.open(entry) as source, open(
            os.path.join(media_dir, file_name), "wb"
        ) as target:
            target.write(source.read())
        saved_names.append(file_name)
    return saved_names


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1

    docx_path, output_dir = sys.argv[1], sys.argv[2]
    if not os.path.isfile(docx_path):
        print("文件不存在: %s" % docx_path)
        return 1

    media_dir = os.path.join(output_dir, "media")
    os.makedirs(media_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(docx_path) as archive:
            output_lines = extract_body(archive)
            media_names = extract_media(archive, media_dir)
    except zipfile.BadZipFile:
        print("不是有效的 .docx 文件（可能是旧版 .doc，请先另存为 .docx）")
        return 1
    except KeyError:
        print("缺少 word/document.xml，文档结构异常")
        return 1

    content_path = os.path.join(output_dir, "content.txt")
    with open(content_path, "w", encoding="utf-8") as content_file:
        content_file.write("\n".join(output_lines))

    print("正文: %s（%d 行）" % (content_path, len(output_lines)))
    if media_names:
        print("图片: %s（%d 张）" % (media_dir, len(media_names)))
        for name in media_names:
            print("  " + name)
    else:
        print("文档无内嵌图片")
    return 0


if __name__ == "__main__":
    sys.exit(main())
