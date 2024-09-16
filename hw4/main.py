import xml.etree.ElementTree as ET
from template import template
import os
import json

current_directory = None

# ------------ UTILS -------------
def init_working_dir():
    global current_directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

def get_absolute_path(relative_path):
    if not current_directory:
        init_working_dir()
    file_path = os.path.join(current_directory, relative_path)
    return file_path
# ----------------------------------------


# ------------ GENERAL PURPOSE -------------
def get(root, element_expression, keep_p = False):
    element =  root.find(element_expression)
    if element is not None:
        if keep_p:
            return keep_paragraph(element)
        else:
            return element.text
    else:
        print("Element not found for expression: " + element_expression)
    
def get_from_element(element, child_element_expression, keep_p = False):
    child_element =  element.find(child_element_expression)
    if child_element is not None:
        if keep_p:
            return keep_paragraph(child_element)
        else:
            return child_element.text
    else:
        print("Element not found for expression: " + child_element_expression)
        return ""
    
def get_all(root, group_element_expression, element_expression, keep_p = False):
    group_element = root.find(group_element_expression)
    if group_element is not None:
        elements = group_element.findall(element_expression)
        if keep_p:
            return [keep_paragraph(element) for element in elements]
        else:
            return [element.text for element in elements]
    else:
        print("Group element not found for expression: " + group_element_expression)
        return []

def get_all_from_element(element, child_element_expression, keep_p = False):
    child_elements = element.findall(child_element_expression)
    if child_elements is not None:
        if keep_p:
            return [keep_paragraph(element) for element in child_elements]
        else:
            return [element.text for element in child_elements]
    else:
        print("Group element not found for expression: " + child_element_expression)

def get_attribute(element, attribute):
    return element.attrib[attribute]

def keep_paragraph(element):
    return str.replace(ET.tostring(element, encoding='unicode'), '  ', '')
# ------------------------


# -------- EXTRACT -----------
def extract_bibliography_citations(root, element):
    c_elements = element.findall('.//xref[@ref-type="bibr"]')
    result = []
    if c_elements is not None:
        for c_element in c_elements:
            c_rid = get_attribute(c_element, 'rid')
            ref_value = get(root, f'.//ref[@id="{c_rid}"]', True)
            result.append(ref_value)
    return result

def extract_table_paragraphs(root, target_rid):
    p_elements = root.findall(f'.//xref[@rid="{target_rid}"]/..')
    result = []
    if p_elements is not None:
        for p_element in p_elements:
            text = keep_paragraph(p_element)
            citations = extract_bibliography_citations(root, p_element)
            result.append({
                "text"      : text,
                "citations" : citations
            })
    return result

def extract_body(table):
    body_thead = get_from_element(table, './/thead', True)
    body_tbody = get_from_element(table, './/tbody', True)
    return body_thead + body_tbody

def extract_cells(root, table):
    cells = table.findall('.//td')
    paragraphs = root.findall('.//p')
    result = []
    for cell in cells:
        if cell.text is not None:
            content = cell.text.strip()
            cell_element = {
                "content" : content,
                "cited_in" : []
            }
            for p in paragraphs:
                text = keep_paragraph(p)
                if content in text:
                    cell_element["cited_in"].append(text)
            result.append(cell_element)
    return result
                    
def extract_tables(root):
    tables = root.findall('.//table-wrap')
    result = []
    for table in tables:
        id = get_attribute(table, 'id')
        caption = get_from_element(table, './/caption/p', True)
        body = extract_body(table)
        foots = get_all_from_element(table, './/table-wrap-foot/p', True)
        paragraphs = extract_table_paragraphs(root, id)
        cells = extract_cells(root, table)

        result.append({
            "table_id"  : id,
            "body"      : body,
            "caption"   : caption,
            "foots"     : foots,
            "paragraphs": paragraphs,
            "cells"     : cells
        })
    return result

def extract_figures(root, filename):
    figures = root.findall('.//fig')
    result = []
    for figure in figures:
        f_id = get_attribute(figure, 'id')
        f_caption = get_from_element(figure, './/caption', True)
        f_graphic = figure.find('.//graphic')
        f_source = "https://www.ncbi.nlm.nih.gov/pmc/articles/" + filename + "/bin/" + get_attribute(f_graphic, "{http://www.w3.org/1999/xlink}href") + ".jpg"
        result.append({
            "fig_id" : f_id,
            "caption"   : f_caption,
            "source"    : f_source
        })
    return result
# ----------------------------------------


def run():
    main_directory = get_absolute_path("")
    sources_directory = main_directory + "/sources"
    for filename in sorted(os.listdir(sources_directory)):
        print("Processing: " + filename)
        tree = ET.parse(sources_directory + "/" + filename)
        root = tree.getroot()
        truncated_filename = str.replace(filename, '.xml', '')

        id = get(root, './/article-id[@pub-id-type="pmc"]')
        title = get(root, './/title-group/article-title')
        abstract = "\n".join(get_all(root, './/abstract', './/p', True))
        keywords = get_all(root, './/kwd-group', 'kwd')
        tables = extract_tables(root)
        figures = extract_figures(root, truncated_filename)

        template["pmcid"] = id
        template["content"]["title"] = title
        template["content"]["abstract"] = abstract
        template["content"]["keywords"] = keywords
        template["content"]["tables"] = tables
        template["content"]["figures"] = figures

        with open(main_directory + f"/outputs/{truncated_filename}.json", "w") as json_file:
            json.dump(template, json_file, indent=4)

run()