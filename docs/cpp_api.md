# 智学伴侣 Python ↔ C++ 接口文档（pybind11）

## 1. 概述

本文档描述 FastAPI 后端（Python）与 C++ 文件处理模块之间的调用接口。C++ 模块通过 **pybind11** 编译为 Python 扩展 `file_processor.so`（Linux / macOS）或 `file_processor.pyd`（Windows），后端通过 `import file_processor` 直接调用，无进程启动开销，所有参数和返回值以 Python 原生类型传递。

模块在 `bindings.cpp` 中统一注册所有对外接口，C++ 实现分散在各功能源文件中（`extractor.cpp`、`preprocessor.cpp`、`fingerprint.cpp`、`comparator.cpp`、`logger.cpp`）。

### 1.1 文档结构

本文档按功能分为以下几节：

| 节 | 内容 |
| --- | --- |
| 2 | 编译与安装 |
| 3 | 接口：文本提取（`extractor`） |
| 4 | 接口：文本预处理（`preprocessor`） |
| 5 | 接口：文本指纹（`fingerprint`） |
| 6 | 接口：批量相似度粗筛（`comparator`） |
| 7 | 接口：日志（`logger`） |
| 8 | 异常处理约定 |
| 9 | Python 端封装层（`file_processor_client.py`） |
| 10 | 完整 `bindings.cpp` 参考 |

### 1.2 类型对照表

| C++ 类型 | Python 类型 | 说明 |
| --- | --- | --- |
| `std::string` | `str` | 文件路径、文本内容 |
| `std::vector<std::string>` | `list[str]` | 段落列表、多份文本 |
| `std::vector<uint64_t>` | `list[int]` | 哈希指纹值列表 |
| `std::vector<std::tuple<int,int,double>>` | `list[tuple[int,int,float]]` | 相似对结果 |
| `int` | `int` | 窗口大小等整型参数 |
| `double` | `float` | 相似度阈值 |
| `void` | `None` | 无返回值（日志写入） |

---

## 2. 编译与安装

### 2.1 依赖

| 依赖 | 说明 |
| --- | --- |
| Python ≥ 3.10 | 后端运行时 |
| pybind11 ≥ 2.11 | C++ ↔ Python 绑定库 |
| C++17 兼容编译器 | GCC ≥ 9、Clang ≥ 10、MSVC ≥ 19.14 |
| cmake ≥ 3.15 | 可选，用于 CMake 构建方式 |

安装 pybind11（在 `backend/` 目录下，通过 uv）：

```bash
uv add pybind11 --dev
```

### 2.2 setup.py 构建（推荐）

`cpp_processor/setup.py`：

```python
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext = Pybind11Extension(
    "file_processor",
    sources=[
        "src/bindings.cpp",
        "src/extractor.cpp",
        "src/preprocessor.cpp",
        "src/fingerprint.cpp",
        "src/comparator.cpp",
        "src/logger.cpp",
    ],
    include_dirs=["include"],
    cxx_std=17,
)

setup(
    name="file_processor",
    ext_modules=[ext],
    cmdclass={"build_ext": build_ext},
)
```

编译命令（在 `cpp_processor/` 目录下执行）：

```bash
python setup.py build_ext --inplace
```

编译成功后在 `cpp_processor/` 目录下生成 `file_processor.so`（或 `.pyd`），将其复制或软链到 `backend/app/` 目录下供 Python 导入。

### 2.3 CMake 构建（备选）

```cmake
# cpp_processor/CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(file_processor)

find_package(pybind11 REQUIRED)

pybind11_add_module(file_processor
    src/bindings.cpp
    src/extractor.cpp
    src/preprocessor.cpp
    src/fingerprint.cpp
    src/comparator.cpp
    src/logger.cpp
)

target_include_directories(file_processor PRIVATE include)
set_target_properties(file_processor PROPERTIES CXX_STANDARD 17)
```

```bash
cmake -B build && cmake --build build
```

---

## 3. 文本提取接口（extractor）

### 3.1 `extract_text`

从本地文件中提取纯文本内容。当前支持 `.txt` 和 `.pdf` 格式；`.doc` / `.docx` 需在上传时由后端预先转换为 `.txt`。

**C++ 签名：**

```cpp
// include/extractor.h
std::string extract_text(const std::string& file_path);
```

**Python 调用：**

```python
text: str = file_processor.extract_text(file_path)
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| file_path | str | 是 | 待提取文件的绝对路径 |

**返回值：**

| 类型 | 说明 |
| --- | --- |
| str | 提取的纯文本，保留换行，去除二进制字符 |

**异常：**

| 异常类型 | 触发条件 |
| --- | --- |
| `RuntimeError` | 文件不存在或无读取权限 |
| `ValueError` | 文件扩展名不在支持列表中 |
| `RuntimeError` | PDF 解析失败（加密、损坏或不含文本层） |

**示例：**

```python
import file_processor

text = file_processor.extract_text("/uploads/submission_001.pdf")
# 返回: "进程是程序的一次执行过程，包含程序段、数据段和进程控制块..."
```

---

## 4. 文本预处理接口（preprocessor）

### 4.1 `preprocess_segments`

对输入文本进行去噪和分段，返回按段落切分的字符串列表。具体处理步骤：去除连续空白行、去除不可见字符、按段落（双换行）切分、过滤长度小于 10 个字符的空段。

**C++ 签名：**

```cpp
// include/preprocessor.h
std::vector<std::string> preprocess_segments(const std::string& text);
```

**Python 调用：**

```python
segments: list[str] = file_processor.preprocess_segments(text)
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| text | str | 是 | 待处理的原始文本，通常来自 `extract_text` 的返回值 |

**返回值：**

| 类型 | 说明 |
| --- | --- |
| list[str] | 段落列表，每个元素为一个完整段落，已去噪，顺序与原文一致 |

**异常：**

| 异常类型 | 触发条件 |
| --- | --- |
| `ValueError` | 输入为空字符串 |

**示例：**

```python
segments = file_processor.preprocess_segments(text)
# 返回: ["进程是资源分配的基本单位...", "线程是 CPU 调度的最小单位..."]
```

---

## 5. 文本指纹接口（fingerprint）

### 5.1 `compute_fingerprint`

使用滑动窗口哈希算法对文本计算指纹，返回哈希值列表。指纹用于在批量相似度粗筛阶段快速过滤明显不相似的提交对，减少送入 MiniMax 的请求量。

**C++ 签名：**

```cpp
// include/fingerprint.h
std::vector<uint64_t> compute_fingerprint(const std::string& text, int window_size = 5);
```

**Python 调用：**

```python
fingerprint: list[int] = file_processor.compute_fingerprint(text, window_size=5)
```

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| text | str | 是 | — | 待计算指纹的文本，建议使用预处理后的文本 |
| window_size | int | 否 | 5 | 滑动窗口大小（词数），取值范围 2~20 |

**返回值：**

| 类型 | 说明 |
| --- | --- |
| list[int] | 哈希值列表，每个值对应一个窗口的哈希，列表长度约为 `词数 - window_size + 1` |

**异常：**

| 异常类型 | 触发条件 |
| --- | --- |
| `ValueError` | 输入文本为空 |
| `ValueError` | `window_size` 不在 2~20 范围内 |

**示例：**

```python
fp = file_processor.compute_fingerprint("进程是资源分配的基本单位，线程是调度单位", window_size=5)
# 返回: [12345678901234567, 98765432109876543, ...]
```

---

## 6. 批量相似度粗筛接口（comparator）

### 6.1 `batch_compare`

对多份文本进行两两指纹相似度粗筛，返回相似度超过阈值的提交对。只返回需要进一步送入 MiniMax 精确分析的候选对，不返回所有组合。

**C++ 签名：**

```cpp
// include/comparator.h
std::vector<std::tuple<int, int, double>> batch_compare(
    const std::vector<std::string>& texts,
    double threshold = 0.8
);
```

**Python 调用：**

```python
pairs: list[tuple[int, int, float]] = file_processor.batch_compare(texts, threshold=0.8)
```

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| texts | list[str] | 是 | — | 参与比对的文本列表，每个元素对应一份提交的文本 |
| threshold | float | 否 | 0.8 | 指纹相似度阈值，取值范围 0.0~1.0，超过此值的对才会被返回 |

**返回值：**

每个元素为三元组 `(i, j, similarity)`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| i | int | 第一份文本在 `texts` 中的下标（`i < j`） |
| j | int | 第二份文本在 `texts` 中的下标 |
| similarity | float | 两份文本的指纹相似度，取值 0.0~1.0 |

**异常：**

| 异常类型 | 触发条件 |
| --- | --- |
| `ValueError` | `texts` 列表为空或只有一个元素 |
| `ValueError` | `threshold` 不在 0.0~1.0 范围内 |

**示例：**

```python
texts = [submission_a_text, submission_b_text, submission_c_text]
pairs = file_processor.batch_compare(texts, threshold=0.8)
# 返回: [(0, 1, 0.87), (1, 2, 0.82)]
# 表示 texts[0] 与 texts[1] 相似度 0.87，texts[1] 与 texts[2] 相似度 0.82
```

---

## 7. 日志接口（logger）

### 7.1 `write_log`

将一条日志消息追加写入指定日志文件。用于记录文件处理过程中的警告、错误和调试信息。

**C++ 签名：**

```cpp
// include/logger.h
void write_log(const std::string& log_path, const std::string& level, const std::string& message);
```

**Python 调用：**

```python
file_processor.write_log(log_path, level, message)
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| log_path | str | 是 | 日志文件的绝对路径，不存在则自动创建 |
| level | str | 是 | 日志级别：`INFO`、`WARN`、`ERROR` |
| message | str | 是 | 日志消息内容 |

**返回值：** `None`

**写入格式：**

```text
[2026-06-09T10:00:00] [ERROR] PDF 解析失败：文件已加密 /uploads/submission_002.pdf
```

**异常：**

| 异常类型 | 触发条件 |
| --- | --- |
| `RuntimeError` | 日志文件路径无写入权限 |
| `ValueError` | `level` 不是 `INFO` / `WARN` / `ERROR` 之一 |

**示例：**

```python
file_processor.write_log(
    "/logs/file_processor.log",
    "ERROR",
    "PDF 解析失败：文件已加密 /uploads/submission_002.pdf"
)
```

---

## 8. 异常处理约定

### 8.1 C++ 异常到 Python 异常的映射

pybind11 会自动将 C++ 标准异常转换为对应的 Python 异常：

| C++ 异常 | Python 异常 | 使用场景 |
| --- | --- | --- |
| `std::invalid_argument` | `ValueError` | 参数非法（路径为空、阈值越界、不支持的格式等） |
| `std::runtime_error` | `RuntimeError` | 运行期错误（文件不存在、解析失败、写入失败等） |
| `std::out_of_range` | `IndexError` | 下标越界（内部使用，通常不直接暴露） |

### 8.2 后端统一错误处理建议

在 `file_processor_client.py` 中统一捕获异常，避免 C++ 错误直接传播到 FastAPI 路由层：

```python
import file_processor
import logging

logger = logging.getLogger(__name__)

def safe_extract_text(file_path: str) -> str | None:
    try:
        return file_processor.extract_text(file_path)
    except (ValueError, RuntimeError) as e:
        logger.error("文件文本提取失败: %s, 原因: %s", file_path, e)
        file_processor.write_log("/logs/file_processor.log", "ERROR", str(e))
        return None
```

---

## 9. Python 端封装层（`file_processor_client.py`）

后端统一通过 `file_processor_client.py` 调用 C++ 扩展，不在业务代码中直接 `import file_processor`，便于后续替换实现（如升级为 gRPC 微服务）时只改动此文件。

完整封装示例：

```python
# backend/app/services/file_processor_client.py

import logging
import file_processor  # pybind11 扩展

logger = logging.getLogger(__name__)
LOG_PATH = "/logs/file_processor.log"


def extract_text(file_path: str) -> str | None:
    """
    从上传文件中提取纯文本。
    支持 .txt / .pdf，失败时返回 None 并写入日志。
    """
    try:
        return file_processor.extract_text(file_path)
    except (ValueError, RuntimeError) as e:
        logger.error("extract_text 失败 [%s]: %s", file_path, e)
        file_processor.write_log(LOG_PATH, "ERROR", f"extract_text: {e}")
        return None


def preprocess(text: str) -> list[str]:
    """
    对文本进行去噪和分段，返回段落列表。
    输入为空时返回空列表。
    """
    if not text:
        return []
    try:
        return file_processor.preprocess_segments(text)
    except ValueError as e:
        logger.warning("preprocess_segments 失败: %s", e)
        return []


def get_fingerprint(text: str, window_size: int = 5) -> list[int]:
    """
    计算文本指纹（滑动窗口哈希），用于相似度粗筛。
    失败时返回空列表。
    """
    try:
        return file_processor.compute_fingerprint(text, window_size=window_size)
    except ValueError as e:
        logger.warning("compute_fingerprint 失败: %s", e)
        return []


def batch_compare(
    texts: list[str], threshold: float = 0.8
) -> list[tuple[int, int, float]]:
    """
    对多份文本进行指纹相似度粗筛。
    返回相似度超过 threshold 的 (i, j, similarity) 三元组列表。
    失败时返回空列表。
    """
    try:
        return file_processor.batch_compare(texts, threshold=threshold)
    except (ValueError, RuntimeError) as e:
        logger.error("batch_compare 失败: %s", e)
        return []
```

---

## 10. 完整 `bindings.cpp` 参考

```cpp
// cpp_processor/src/bindings.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // std::vector / std::string 自动转换
#include <pybind11/pytypes.h>

#include "extractor.h"
#include "preprocessor.h"
#include "fingerprint.h"
#include "comparator.h"
#include "logger.h"

namespace py = pybind11;

PYBIND11_MODULE(file_processor, m) {
    m.doc() = "智学伴侣 C++ 文件处理模块（pybind11）";

    // ── 文本提取 ──────────────────────────────────────────────
    m.def(
        "extract_text",
        &extract_text,
        py::arg("file_path"),
        R"doc(
从本地文件中提取纯文本。

Args:
    file_path (str): 待提取文件的绝对路径，支持 .txt / .pdf。

Returns:
    str: 提取的纯文本内容。

Raises:
    ValueError: 文件格式不支持。
    RuntimeError: 文件不存在、无权限或解析失败。
)doc"
    );

    // ── 文本预处理 ────────────────────────────────────────────
    m.def(
        "preprocess_segments",
        &preprocess_segments,
        py::arg("text"),
        R"doc(
对输入文本进行去噪和分段。

Args:
    text (str): 原始文本，通常来自 extract_text 的返回值。

Returns:
    list[str]: 按段落切分的字符串列表。

Raises:
    ValueError: 输入为空字符串。
)doc"
    );

    // ── 文本指纹 ──────────────────────────────────────────────
    m.def(
        "compute_fingerprint",
        &compute_fingerprint,
        py::arg("text"),
        py::arg("window_size") = 5,
        R"doc(
使用滑动窗口哈希计算文本指纹。

Args:
    text (str): 待计算指纹的文本。
    window_size (int): 滑动窗口大小（词数），默认 5，范围 2~20。

Returns:
    list[int]: 哈希值列表。

Raises:
    ValueError: 输入文本为空或 window_size 越界。
)doc"
    );

    // ── 批量相似度粗筛 ────────────────────────────────────────
    m.def(
        "batch_compare",
        &batch_compare,
        py::arg("texts"),
        py::arg("threshold") = 0.8,
        R"doc(
对多份文本进行两两指纹相似度粗筛。

Args:
    texts (list[str]): 参与比对的文本列表。
    threshold (float): 相似度阈值，默认 0.8，范围 0.0~1.0。

Returns:
    list[tuple[int, int, float]]: 超过阈值的 (i, j, similarity) 三元组列表。

Raises:
    ValueError: texts 少于两个元素或 threshold 越界。
)doc"
    );

    // ── 日志写入 ──────────────────────────────────────────────
    m.def(
        "write_log",
        &write_log,
        py::arg("log_path"),
        py::arg("level"),
        py::arg("message"),
        R"doc(
向指定日志文件追加一条日志。

Args:
    log_path (str): 日志文件绝对路径，不存在则自动创建。
    level (str): 日志级别，INFO / WARN / ERROR 之一。
    message (str): 日志消息内容。

Returns:
    None

Raises:
    ValueError: level 不合法。
    RuntimeError: 日志文件无写入权限。
)doc"
    );
}
```
