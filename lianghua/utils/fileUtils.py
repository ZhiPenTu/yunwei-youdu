import inspect

__all__ = ['get_current_filename']

def get_current_filename():
    return inspect.stack()[1][3]
     
# 使用示例
if __name__ == "__main__":
    name = get_current_filename()
    print(f"New path: {name}")