"""
MCP 服务器示例 - 提供基础数学运算和图片功能
注意：stdio 传输下不要向 stdout 打印任意文本，日志请输出到 stderr。
"""

import base64
import io

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from PIL import Image, ImageDraw
from logic.pick_restric_enzym_pairs import pick_enzyme_pairs_from_dna
from logic.ncbi_cds import get_cds_by_gene_simple
from logic.primer_design import design_primers_logic
from logic.fasta_utils import read_fasta
from pathlib import Path # Needed for saving files

# 初始化 FastMCP 服务器
mcp = FastMCP("my-mcp-server")

@mcp.tool()
def read_fasta_file(path: str) -> str:
    """
    读取FASTA文件并返回其序列内容。

    Args:
        path: FASTA文件的路径。

    Returns:
        FASTA文件中的序列内容。
    """
    return read_fasta(path)


@mcp.tool()
def get_cds_sequence(gene_name: str, organism: str = "Homo sapiens") -> str:
    """
    从 NCBI 获取基因的 CDS 序列，并保存到临时文件，返回文件路径。
    Args:
        gene_name: 基因名称。
        organism: 物种名称，默认 "Homo sapiens"。
    Returns:
        保存CDS序列的FASTA文件路径。
    """
    return get_cds_by_gene_simple(gene_name, organism)
@mcp.tool()
def select_restriction_sites(vector_dna_path: str, insert_sequence_path: str) -> dict:
    """
    根据提供的载体和插入序列的文件路径，选择合适的双酶切位点。

    Args:
        vector_dna_path: 载体DNA文件的路径。
        insert_sequence_path: 插入片段FASTA文件的路径。

    Returns:
        包含推荐酶切位点和理由的字典。
    """
    insert_sequence = read_fasta(insert_sequence_path)
    # 调用 pick_enzyme_pairs_from_dna 函数
    enzymes = pick_enzyme_pairs_from_dna(vector_dna_path, insert_sequence)
    return {
        "available_enzymes": [{"name": e["name"], "site": e["site"], "pos0": e["pos0"]} for e in enzymes],
        "reason": "These enzymes are unique cutters within the MCS of the vector and do not cut within the insert."
    }

@mcp.tool()
def design_primers(cds_sequence: str, forward_enzyme_sequence: str, reverse_enzyme_sequence: str) -> dict:
    """
    根据CDS序列文件路径设计引物。

    Args:
        cds_sequence: CDS序列FASTA文件的路径。
        forward_enzyme_sequence: 正向引物酶切位点（DNA序列，例如 "GAATTC"）。请提供精确的DNA识别序列，区分大小写。
        reverse_enzyme_sequence: 反向引物酶切位点（DNA序列，例如 "CTCGAG"）。请提供精确的DNA识别序列，区分大小写。

    Returns:
        包含正向和反向引物信息的字典。
    """
    cds_content = read_fasta(cds_sequence) # Renamed variable for clarity
    return design_primers_logic(cds_content, forward_enzyme_sequence, reverse_enzyme_sequence)

@mcp.tool()
def plan_pcr(template_path: str, forward_primer: str, reverse_primer: str) -> str:
    """
    设计高保真PCR扩增方案。

    Args:
        template_path: cDNA模板FASTA文件的路径。
        forward_primer: 正向引物。
        reverse_primer: 反向引物。

    Returns:
        PCR扩增方案的文本描述。
    """
    template_sequence = read_fasta(template_path)
    # 假结果 (需要根据实际的 template_sequence, forward_primer, reverse_primer 来生成协议)
    return f"High-fidelity PCR protocol for template from {template_path} with primers {forward_primer} and {reverse_primer}: ... (fake protocol)"


@mcp.tool()
def plan_ligation(vector_name: str, insert_sequence_path: str, vector_size_bp: int, insert_size_bp: int) -> str:
    """
    制定连接（Ligation）方案。

    Args:
        vector_name: 载体名称。
        insert_sequence_path: 插入片段FASTA文件的路径。
        vector_size_bp: 载体大小 (bp)。
        insert_size_bp: 插入片段大小 (bp)。

    Returns:
        连接方案的文本描述。
    """
    insert_sequence = read_fasta(insert_sequence_path)
    # 假结果 (需要根据实际的 insert_sequence 来生成协议)
    return f"Ligation protocol for vector {vector_name} and insert from {insert_sequence_path} (Molar ratio 1:3 vector:insert): ... (fake protocol)"

@mcp.tool()
def generate_plasmid_map_and_protocol(plasmid_name: str, vector_name: str, insert_gene: str) -> dict:
    """
    生成质粒图谱和完整构建Protocol。

    Args:
        plasmid_name: 最终质粒名称。
        vector_name: 载体名称。
        insert_gene: 插入的基因名称。

    Returns:
        包含质粒图谱（图片）和构建Protocol（文本）的字典。
    """
    # 假结果
    return {
        "plasmid_map_image": "data:image/png;base64,...(fake image data)",
        "protocol": "Complete protocol for constructing plasmid... (fake protocol)"
    }


def main():
    """启动 MCP 服务器"""
    # 显式使用 stdio 作为传输层（默认即为 stdio，此处为教学标注）
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
