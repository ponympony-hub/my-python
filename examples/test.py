
if __name__ == '__main__':
    import json

    # 内置字典对象
    data = {
        "name": "张三",
        "age": 25,
        "skills": ["Python", "Java"]
    }

    # 转换为 JSON 字符串
    # ensure_ascii=False 可以让中文字符正常显示，而不是显示为 unicode 编码
    json_str = json.dumps(data, ensure_ascii=False, indent=4)

    print(json_str)
