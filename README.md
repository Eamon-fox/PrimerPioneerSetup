# PrimerPioneer MCP Server

## 项目概述

本项目是一个为 AI for Science 黑客松开发的 MCP (Model Context Protocol) 服务器，旨在为分子克隆实验流程提供一系列自动化的生物信息学工具。通过与大型语言模型（LLM）的交互，本服务器可以完成从基因序列检索、引物设计、酶切位点分析到实验方案生成的全流程任务。

本项目名为 "PrimerPioneer"，旨在成为AI在引物设计和分子克隆领域的先驱。

## 如何运行

1.  **安装依赖**:
    本项目使用 `uv` 作为包管理工具。请确保已安装 `uv`。
    ```bash
    pip install uv
    uv sync
    ```

2.  **设置环境变量 (可选)**:
    为了使用 NCBI 的 Entrez API，建议设置您的邮箱和 API 密钥。
    ```bash
    export NCBI_EMAIL="your.email@example.com"
    export NCBI_API_KEY="your_ncbi_api_key"
    ```

3.  **启动 MCP 服务器**:
    ```bash
    mcp run --file my_mcp_server/main.py
    ```

## MCP 工具概览

本服务器提供了一系列围绕分子克隆工作流的工具，所有工具都通过文件路径进行长序列的传递，以避免上下文窗口限制。

*   `read_fasta_file`: 读取FASTA文件并返回其序列内容。
*   `get_cds_sequence`: 从 NCBI 获取基因的 CDS 序列，并保存到临时文件，返回文件路径。
*   `select_restriction_sites`: 根据载体和插入片段的序列，选择合适的双酶切位点。
*   `design_primers`: 根据CDS序列、酶切位点和一系列生物信息学参数，设计最优的PCR引物。
*   `plan_pcr`: 根据引物Tm和产物长度，动态生成详细的高保真PCR扩增方案。
*   `plan_ligation`: 根据载体和插入片段的大小，自动计算连接反应中各组分的推荐用量。
*   `generate_plasmid_map_and_protocol`: 生成一个给LLM的详细提示词，指导LLM根据对话历史生成一份完整的质粒构建实验方案。

## 核心逻辑实现思路

### `my_mcp_server/main.py`

这是 MCP 服务器的入口文件，定义了所有可供 LLM 调用的工具。

*   **工具定义**: 使用 `@mcp.tool()` 装饰器将每个函数注册为一个 MCP 工具。
*   **参数传递**: 所有涉及长DNA序列的工具都使用文件路径 (`_path`) 作为参数，在函数内部调用 `read_fasta` 来读取序列，避免了在LLM上下文中传递长字符串。
*   **逻辑分离**: `main.py` 主要负责处理工具的输入输出和流程控制，而将核心的生物信息学计算委托给 `logic/` 目录下的各个模块。
*   **动态方案生成**: `plan_pcr` 和 `plan_ligation` 函数体现了动态计算的思想，它们不仅仅是返回静态模板，而是根据输入的参数（如Tm值、序列长度）实时计算出推荐的实验条件。
*   **LLM协同**: `generate_plasmid_map_and_protocol` 的实现是一个亮点，它不自己生成最终的protocol，而是生成一个给LLM的prompt，利用LLM的上下文整合能力来生成更完善、更连贯的最终报告。

### `my_mcp_server/logic/primer_design.py`

这是项目中最核心和最复杂的模块，负责引物的设计。

*   **`design_primers_logic`**: 这是主函数，协调整个引物设计流程。
*   **`_find_optimal_primer`**: 这是引物设计的核心算法。
    *   **迭代搜索**: 算法不再使用固定的结合区长度，而是在一个预设的长度范围（18-25 bp）内进行迭代搜索。
    *   **多目标优化**: 在每次迭代中，算法会计算当前候选引物结合区的**长度、GC含量**和**Tm值**。
    *   **退火参数**: 判断引物是否“最优”的标准是基于**结合区**的参数，因为这部分是决定退火效率的关键。
    *   **Tm计算**: Tm值使用 Biopython 的 `MeltingTemp.Tm_NN` 方法计算，这是一种基于最近邻热力学模型的精确算法。为了兼容性，代码移除了在旧版Biopython中不支持的 `dnac` 参数。
    *   **保护碱基**: 在构建完整引物时，会自动在5'端加上 "AATT" 作为保护碱基，以确保后续的酶切效率。
    *   **详细报告**: 函数的返回值是一个字典，其中包含了**结合区**和**完整引物**的各种参数（长度、GC含量、Tm值），为用户提供全面的信息。
    *   **次优解**: 如果在整个迭代过程中没有找到完全符合所有标准的引物，算法会返回一个“次优”解，并附上详细的说明，指出是哪个参数不满足标准。

### `my_mcp_server/logic/ncbi_cds.py`

该模块负责与 NCBI 数据库交互，获取基因的 CDS 序列。

*   **`get_cds_by_gene_simple`**:
    *   **三步法**: 整个过程分为三步：1. 基因名 -> Gene ID (`esearch`)；2. Gene ID -> RefSeq mRNA ID (`elink`)；3. RefSeq mRNA ID -> CDS FASTA (`efetch`)。
    *   **API使用**: 使用 Biopython 的 `Entrez` 模块来调用 NCBI 的 API。代码中设置了 `email` 和 `api_key`，并加入了 `time.sleep(0.34)` 以遵守 NCBI 的 API 调用频率限制。
    *   **文件保存**: 获取到FASTA格式的CDS序列后，函数会将其保存到一个临时文件中。
    *   **路径修正**: 文件保存路径被修正为项目根目录下的 `my_mcp_server/data/temp_cds/`，避免了在 `logic` 目录下创建新的 `data` 目录。
    *   **返回值**: 函数最终返回的是保存好的FASTA文件的**绝对路径字符串**。

### `my_mcp_server/logic/pick_restric_enzym_pairs.py`

该模块负责筛选合适的酶切位点。

*   **`pick_enzyme_pairs_from_dna`**:
    *   **文件解析**: 使用 `snapgene_reader` 库来解析 `.dna` 格式的载体文件，提取出全序列和特征（features）。
    *   **MCS定位**: 通过 `_get_mcs_range` 函数在特征列表中找到名为 "MCS" (Multiple Cloning Site) 的区域，并获取其起止位置。
    *   **酶切位点扫描**: 使用 Biopython 的 `Bio.Restriction.RestrictionBatch` 和 `CommOnly` 酶列表，在载体全序列上进行扫描。
    *   **单切点筛选**: 只保留那些在整个载体中只有一个酶切位点（unique cutter），且该位点位于MCS区域内的酶。
    *   **插入片段过滤**: 通过 `_filter_by_insert` 函数，进一步过滤掉那些会在插入片段内部进行切割的酶，确保插入片段的完整性。

### `my_mcp_server/logic/fasta_utils.py`

这是一个简单的工具模块，提供FASTA文件的读取功能。

*   **`read_fasta`**:
    *   **功能**: 接收一个文件路径，打开并读取文件内容。
    *   **解析**: 逐行读取，忽略以 `>` 开头的标题行，将所有其他行的序列拼接起来。
    *   **标准化**: 返回的序列会被转换为全大写，以方便后续处理。

## 文件结构

```
my_mcp_server/
├── data/                # 存放数据文件，如质粒.dna文件
│   └── temp_cds/        # 存放从NCBI下载的临时CDS序列
├── logic/               # 存放核心的生物信息学计算逻辑
│   ├── fasta_utils.py
│   ├── ncbi_cds.py
│   ├── pick_restric_enzym_pairs.py
│   └── primer_design.py
├── main.py              # MCP服务器入口，定义所有工具
├── pyproject.toml       # 项目依赖和配置
└── ...
