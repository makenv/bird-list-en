# 直接构建目录

Mac OSX下面，打开终端，执行
```sh
sh v10_0_mkdir.sh
```
就可以创建目录.

# 定制化需求
可以修改s30__mkdirs.py中的DIR_PATTERN来控制目录名称, 比如需要中文名加英文名可以
```python
DIR_PATTERN='{kcn}_{ken}/{cn}_{en}'
```
这里需要注意，英文名中有`'`字符，可能需要特殊处理一下.
