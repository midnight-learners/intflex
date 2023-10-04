import os
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph


def convert_docx_to_txt(root_path: str = '../document'):
    def iter_block_items(parent):
        if isinstance(parent, _Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        elif isinstance(parent, _Row):
            parent_elm = parent._tr
        else:
            raise ValueError("something's not right")
        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    output_root_path = '../document_txt'
    sub_paths = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]

    for sub_path in sub_paths:
        print(f"\nprocessing {root_path}/{sub_path}...")
        file_names = [file_name for file_name in os.listdir(f"{root_path}/{sub_path}") if file_name.endswith(".docx")]
        file_names.sort()

        for file_name in file_names:
            print(f"processing {file_name}...", end="")
            doc = Document(f"{root_path}/{sub_path}/{file_name}")
            output_file_name = file_name.split(".")[0]

            text_content = []  # 列表存储提取的文字
            for block in iter_block_items(doc):
                # 1. read Paragraph
                if isinstance(block, Paragraph):
                    para_text = block.text.replace(" ", "")
                    if para_text != "":
                        text_content.append(para_text)
                        # print(para_text)

                # 2. read table
                elif isinstance(block, Table):
                    skip_flag = False
                    for row in block.rows:
                        pre_cell_text = ""
                        if skip_flag:
                            break
                        for cell in row.cells:
                            cell_text = (".".join([paragraph.text for paragraph in cell.paragraphs])
                                         .replace("\n", ".").replace(" ", ""))
                            if cell_text == "更改标记":
                                skip_flag = True
                                break
                            if cell_text == pre_cell_text or cell_text == "":  # 去重
                                continue
                            pre_cell_text = cell_text
                            text_content.append(cell_text)
                        # print(pre_cell_text)

            # 判断输出文件夹是否存在，如果不存在则创建文件夹
            if not os.path.exists(f"{output_root_path}/{sub_path}"):
                os.makedirs(f"{output_root_path}/{sub_path}")

            with open(f"{output_root_path}/{sub_path}/{output_file_name}.txt", "w", encoding="utf-8") as txt_file:
                # 写入文档标题
                txt_file.write(file_name + "\n")
                # 遍历文档中的段落并写入.txt文件
                for text in text_content:
                    text = text.replace(" ", "").replace("\u00A0", "")
                    if text.endswith("附录") or text.startswith("相关表单"):
                        break
                    if text and text != "":
                        txt_file.write(text + "\n")

            print(f"Text extracted and saved to {output_file_name}")


if __name__ == "__main__":
    convert_docx_to_txt()
