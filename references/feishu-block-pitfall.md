# 飞书 Block 写入踩坑（2026-07-04 实测）

## 坑：block_type 编号错误导致 1770001 invalid param

**复现条件**：使用自增整数作为 block_type（如 1=text, 2=heading1, 3=heading2）。

**症状**：`{"code": 1770001, "msg": "invalid param"}`，所有 batch 全部失败。

**根因**：飞书 docx API 的 block_type 是**固定枚举值**，不是自增编号。

**正确速查表**：

| block_type | 含义 | elements 结构 |
|---|---|---|
| 2 | text（正文段落） | `{"text": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 3 | heading1 | `{"heading1": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 4 | heading2 | `{"heading2": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 5 | heading3 | `{"heading3": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 12 | bullet（无序列表） | `{"bullet": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 13 | ordered（有序列表） | `{"ordered": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 14 | code（代码块） | `{"code": {"elements": [{"text_run": {"content": "..."}}]}}` |
| 22 | divider（分割线） | `{}`（无需 elements） |

**关键陷阱**：
- `heading2` 的 block_type 是 **4**，不是 2 也不是 3
- elements 结构必须用 `text_run` 包裹，不能直接传字符串
- 粗体样式：`{"text_run": {"content": "...", "text_element_style": {"bold": true}}}`

**修法**：写入前先用 **1 个 block** 测试格式：

```python
test_data = {
    "children": [
        {
            "block_type": 2,
            "text": {
                "elements": [{"text_run": {"content": "测试段落"}}]
            }
        }
    ],
    "index": -1
}
resp = requests.post(write_url, headers=headers, json=test_data)
if resp.json().get('code') != 0:
    print(f'格式错误: {resp.json()}')
else:
    # 测试通过，开始批量写入
    ...
```

**验证方法**：

```bash
GET /open-apis/docx/v1/documents/{doc_id}/raw_content
# 返回的 content 长度 > 500 表示写入成功
# 返回 32 表示只有标题、内容为空
```
