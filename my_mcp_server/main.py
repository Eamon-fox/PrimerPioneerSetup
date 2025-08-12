"""
MCP 服务器示例 - 提供基础数学运算和图片功能
注意：stdio 传输下不要向 stdout 打印任意文本，日志请输出到 stderr。
"""

import base64
import io

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from PIL import Image, ImageDraw


# 初始化 FastMCP 服务器
mcp = FastMCP("my-mcp-server")

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    将两个数字相加
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        两数之和
    """
    result = a + b
    return result

@mcp.tool()
def reverse(text: str) -> str:
    """
    反转输入的文本字符串
    
    Args:
        text: 要反转的文本
    
    Returns:
        反转后的文本
    """
    reversed_text = text[::-1]
    return reversed_text


def main():
    """启动 MCP 服务器"""
    # 显式使用 stdio 作为传输层（默认即为 stdio，此处为教学标注）
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
