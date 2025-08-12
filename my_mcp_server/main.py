"""
MCP 服务器示例 - 提供基础数学运算和图片功能
注意：stdio 传输下不要向 stdout 打印任意文本，日志请输出到 stderr。
"""

import base64
import io

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from PIL import Image, ImageDraw
from pick_restric_enzym_pairs import pick_enzyme_pairs_from_dna
from ncbi_cds import get_cds_by_gene_simple


# 初始化 FastMCP 服务器
mcp = FastMCP("my-mcp-server")


@mcp.tool()
def get_cds_sequence(gene_name: str, organism: str = "Homo sapiens") -> str:
    """
    从 NCBI 获取基因的 CDS 序列（FASTA 格式）。
    Args:
        gene_name: 基因名称。
        organism: 物种名称，默认 "Homo sapiens"。
    Returns:
        基因的CDS序列（FASTA格式）。
    """
    return get_cds_by_gene_simple(gene_name, organism)
@mcp.tool()
def select_restriction_sites(vector_dna_path: str, insert_sequence: str) -> dict:
    """
    选择合适的双酶切位点。

    Args:
        vector_dna_path: 载体DNA文件的路径。
        insert_sequence: 插入片段序列。

    Returns:
        包含推荐酶切位点和理由的字典。
    """
    # 调用 pick_enzyme_pairs_from_dna 函数
    enzymes = pick_enzyme_pairs_from_dna(vector_dna_path, insert_sequence)
    return {
        "available_enzymes": [{"name": e["name"], "site": e["site"], "pos0": e["pos0"]} for e in enzymes],
        "reason": "These enzymes are unique cutters within the MCS of the vector and do not cut within the insert."
    }

@mcp.tool()
def design_primers(cds_sequence: str, forward_enzyme: str, reverse_enzyme: str) -> dict:
    """
    根据CDS序列设计引物。

    Args:
        cds_sequence: CDS序列。
        forward_enzyme: 正向引物酶切位点。
        reverse_enzyme: 反向引物酶切位点。

    Returns:
        包含正向和反向引物信息的字典。
    """
    # 假结果
    return {
        "forward_primer": "5'-CGCGGATCCGCCACCATGGCC...-3'",
        "reverse_primer": "5'-CCGCTCGAGTCAGTG...-3'",
        "tm": {"forward": 65.5, "reverse": 66.0},
        "notes": "Primers designed with Kozak sequence and restriction sites."
    }

@mcp.tool()
def plan_pcr(template: str, forward_primer: str, reverse_primer: str) -> str:
    """
    设计高保真PCR扩增方案。

    Args:
        template: cDNA模板。
        forward_primer: 正向引物。
        reverse_primer: 反向引物。

    Returns:
        PCR扩增方案的文本描述。
    """
    # 假结果
    return "High-fidelity PCR protocol: ... (fake protocol)"


@mcp.tool()
def plan_ligation(vector_name: str, insert_sequence: str, vector_size_bp: int, insert_size_bp: int) -> str:
    """
    制定连接（Ligation）方案。

    Args:
        vector_name: 载体名称。
        insert_sequence: 插入片段序列。
        vector_size_bp: 载体大小 (bp)。
        insert_size_bp: 插入片段大小 (bp)。

    Returns:
        连接方案的文本描述。
    """
    # 假结果
    return "Ligation protocol: Molar ratio 1:3 (vector:insert)... (fake protocol)"

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
