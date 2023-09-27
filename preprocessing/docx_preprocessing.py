import os
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph


def convert_docx_to_txt(directory_path: str = './document'):
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

    output_directory_path = './document_txt'
    file_names = [file_name for file_name in os.listdir(directory_path) if file_name.endswith(".docx")]
    file_names.sort()

    for file_name in file_names:
        print(f"processing {file_name}...", end="")
        doc = Document(f"{directory_path}/{file_name}")
        output_file_name = file_name.split(".")[0]

        text_content = []  # 初始化一个列表来存储提取的文字
        for block in iter_block_items(doc):
            # read Paragraph
            if isinstance(block, Paragraph):
                if block.text.strip() != "":
                    text_content.append(block.text.strip())
            # read table
            elif isinstance(block, Table):
                for row in block.rows:
                    pre_cell_text = ""
                    for cell in row.cells:
                        cell_text = " ".join([paragraph.text for paragraph in cell.paragraphs]).replace("\n", " ").strip()
                        if cell_text == pre_cell_text or cell_text == "":
                            continue
                        pre_cell_text = cell_text
                        text_content.append(cell_text)

        with open(f"{output_directory_path}/{output_file_name}.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write(file_name + "\n")
            write_content = False
            # 遍历文档中的段落并写入.txt文件
            for text in text_content:
                if not write_content and text == "目的":
                    txt_file.write(text + "\n")
                    write_content = True
                    continue
                if text == "附录":
                    break
                if write_content and text != "":
                    txt_file.write(text + "\n")

        print(f"Text extracted and saved to {output_file_name}")


if __name__ == "__main__":
    convert_docx_to_txt()
