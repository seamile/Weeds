from fontTools.ttLib import TTFont

# Base 字体的编码和数字的对应关系
BASE_FONT = {
    'x': '.',
    'uniE2AE': '7',
    'uniE450': '5',
    'uniE7B8': '9',
    'uniE90F': '8',
    'uniEA64': '0',
    'uniF0A1': '1',
    'uniF442': '6',
    'uniF662': '2',
    'uniF69D': '4',
    'uniF8B2': '3',
}


def get_glyf_data(glyf):
    '''将字形数据转化成 16 进制字符串'''
    if hasattr(glyf, 'coordinates'):
        return glyf.coordinates.array.tobytes().hex()
    else:
        return None


def gen_glyf_num_dict(font):
    '''
    根据字体生成 {字形: 数字} 的字典

    Args:
        font: 字体对象
    '''
    glyf_num_dict = {}
    for fcode in font['glyf'].keys():
        # 获取 16 进制字形数据
        glyf = font['glyf'][fcode]  # 字形数据
        hex_glyf = get_glyf_data(glyf)

        if hex_glyf != None:
            glyf_num_dict[hex_glyf] = BASE_FONT[fcode]
    return glyf_num_dict


def gen_glyf_fcode_dict(font):
    '''
    根据字体生成 {字形: 字体编码} 的字典

    Args:
        font: 字体对象
    '''
    glyf_fcode_dict = {}
    for fcode in font['glyf'].keys():
        glyf = font['glyf'][fcode]
        hex_glyf = get_glyf_data(glyf)
        if hex_glyf != None:
            glyf_fcode_dict[hex_glyf] = fcode
    return glyf_fcode_dict


def gen_fcode_num_dict(base_font, new_font):
    '''
    根据 base 字体，生成新字体中 {新编码: 数字} 的字典

    Args:
        base_font: Base字体对象
        new_font: 新字体对象
    '''
    glyf_num_dict = gen_glyf_num_dict(base_font)     # 获取 base 字体中 字形-数字 的对应关系
    glyf_fcode_dict = gen_glyf_fcode_dict(new_font)  # 获取新字体中 字形-编码 的对应关系

    # 根据字形，将 new_font 中的编码与 base_font 中的 num 对应起来
    fcode_num_dict = {}
    for glyf, fcode in glyf_fcode_dict.items():
        num = glyf_num_dict[glyf]    # 根据字形取出 base 中的 num
        fcode_num_dict[fcode] = num  # 构建 新编码 与 num 的对应关系
    return fcode_num_dict


def convert_num_code_to_fcodes(num_code):
    '''对字体编码做转义'''
    fcodes = []
    for char in num_code:
        if char == '.':
            fcode = 'x'  # 小数点转成 'x'
        else:
            code = ord(char)
            hex_code = '%x'.upper() % code
            fcode = 'uni%s' % hex_code
        fcodes.append(fcode)
    return fcodes


def get_real_num(base_font_path, new_font_path, num_code):
    '''
    获取实际数字

    Args:
        base_font_path: base 字体文件路径
        new_font_path: 新字体文件路径
        num_code: 页面上抓去来的数字 (直接打印会是一串乱码)
    '''
    # 读取字体文件
    base_font = TTFont(base_font_path)
    new_font = TTFont(new_font_path)

    fcode_num_mapper = gen_fcode_num_dict(base_font, new_font)  # 获取编码与数字的对应关系
    fcodes = convert_num_code_to_fcodes(num_code)

    print('编码与数字的映射关系')
    for fcode, num in fcode_num_mapper.items():
        print('%10s -> %s' % (fcode, num))
    print('页面抓取的字符串编码: %s\n' % fcodes)

    num = ''.join(fcode_num_mapper[k] for k in fcodes)
    return num



if __name__ == '__main__':
    # 每次将字体文件保存成 new_font.woff, 页面上的数字为 page_num
    page_num = '.'
    num = get_real_num('base.woff', 'new_font.woff', page_num)
    print('票房：%s' % num)
