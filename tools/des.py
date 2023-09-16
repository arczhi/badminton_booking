import execjs


def js_from_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as file:
        result = file.read()
    return result


def get_rsa(un, psd, lt):
    context = execjs.compile(js_from_file(r'./scripts/des.js'))
    result = context.call("strEnc", un + psd + lt, '1', '2', '3')
    return result
