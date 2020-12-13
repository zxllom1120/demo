# coding=utf-8



class DumpType(object):
    DEFAULT = 1
    FIRST_KEYS_AS_ATTR = 2


class PyDumper(object):
    """把一个数据对象导出成py文件"""

    INDENT = ' ' * 4
    NEW_LINE = '\n'

    _DUMP_HANDLER_DICT = {
        DumpType.DEFAULT: '_dump_default',
        DumpType.FIRST_KEYS_AS_ATTR: '_dump_first_keys_as_attr',
    }

    def __init__(self,
                 dump_type=DumpType.DEFAULT,
                 use_taggeddict=True,
                 list_as_tuple=True,
                 reload_all=True,
                 src_file='',
                 author='',
                 record_time=False,
                 one_line=False,
                 **kwargs):
        self.dump_type = dump_type
        self.use_taggeddict = use_taggeddict
        self.list_as_tuple = list_as_tuple
        self.src_file = src_file
        self.author = author
        self.record_time = record_time
        self.reload_all = reload_all
        self.one_line = one_line
        if one_line:
            self.INDENT = ""
            self.NEW_LINE = ""

    def dump(self, obj):
        data_dump_handler = getattr(self, self._DUMP_HANDLER_DICT.get(self.dump_type, '_dump_default'))
        lines = [self._get_head_line()]
        dump_info = self._get_dump_info_line()
        dump_info and lines.append(dump_info)
        dict_type = 'dict'
        if self.use_taggeddict:
            lines.append('from taggeddict import taggeddict')
            dict_type = 'taggeddict'
        lines.append('_d = %s' % dict_type)
        if self.author:
            lines.append('__author__ = "%s"' % self.author)
        if self.reload_all:
            lines.append('_reload_all = True')
        lines.append('')
        lines.append(data_dump_handler(obj))
        lines.append('')
        return '\n'.join(lines)

    def _get_head_line(self):
        return '# -*- coding:utf-8 -*-'

    def _get_dump_info_line(self):
        import time # noqa
        dump_info_list = []
        if self.src_file:
            dump_info_list.append('From %s' % self.src_file)
        if self.record_time:
            dump_info_list.append('At %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        if dump_info_list:
            dump_info_list.insert(0, '# Dump')
            return ' '.join(dump_info_list)
        return ''

    def _dump_default(self, obj):
        return 'data = %s' % self._dump_any(obj)

    def _dump_first_keys_as_attr(self, obj):
        def _attr_name_valid(name):
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            assert isinstance(name, str), '%s is not a valid attribute name' % name

        attr_contents = []
        for k, v in self._get_sorted_dict_items(obj):
            _attr_name_valid(k)
            attr_contents.append('%s = %s' % (k, self._dump_any(v)))

        return '\n\n'.join(attr_contents)

    def _dump_any(self, obj, indent=0, list_as_tuple=False):
        """

        Args:
            obj:
            indent(int):

        Returns:
            str

        """
        if self._is_dict(obj):
            return self._dump_dict(obj, indent)
        if isinstance(obj, tuple):
            return self._dump_sequence(obj, indent, '(', ')')
        if isinstance(obj, list):
            if list_as_tuple or self.list_as_tuple:
                return self._dump_sequence(obj, indent, '(', ')')
            return self._dump_sequence(obj, indent, '[', ']')
        if isinstance(obj, set):
            return self._dump_sequence(obj, indent, '{', '}')
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        if isinstance(obj, str):
            return self._dump_str(obj)
        return '%s' % obj

    def _dump_dict(self, obj, indent):
        """

        Args:
            obj(dict):
            indent(int):

        Returns:
            str

        """
        if not obj:
            return '_d({})'
        if indent == 0:
            new_line = '\n'
            indent_char = self.__class__.INDENT
        else:
            new_line = self.NEW_LINE
            indent_char = self.INDENT
        content = '_d({%s' % new_line
        data_lines = []
        for k, v in self._get_sorted_dict_items(obj):
            data_lines.append('{indent}{key}: {value}, {new_line}'.format(
                indent=indent_char * (indent + 1),
                key=self._dump_any(k, 0, list_as_tuple=True),
                value=self._dump_any(v, indent + 1),
                new_line=new_line,
            ))
        content += ''.join(data_lines)
        content += '%s})' % (self.INDENT * indent)
        return content

    def _dump_sequence(self, sequence, indent, start, end):
        """

        Args:
            sequence(list, tuple, set):
            indent:

        Returns:
            str

        """
        if not sequence:
            return '%s%s' % (start, end)

        if self._only_one_line(tuple({v.__class__ for v in sequence})):
            data_seg = ', '
            data_indent = ''
            if len(sequence) == 1:
                content_format = '{start}{data}, {end}'
            else:
                content_format = '{start}{data}{end}'
        else:
            data_seg = ',\n'
            data_indent = self.INDENT * (indent + 1)
            content_format = '{start}\n{data},\n{end}'
            end = '%s%s' % (self.INDENT * indent, end)

        data_lines = ['%s%s' % (data_indent, self._dump_any(value, indent + 1)) for value in sequence]
        return content_format.format(
            start=start,
            data=data_seg.join(data_lines),
            end=end
        )

    def _only_one_line(self, types):
        """通过类型判断是否单行导出"""
        if self.one_line:
            return True
        if len(types) == 1:
            fix_type = types[0]
            return fix_type in (long, int, float)

        for type_ in types:
            if type_ not in (long, int, float):
                return False

        return True

    def _dump_str(self, obj):
        """

        Args:
            obj(str):

        Returns:
            str

        """
        # 简单处理下换行符
        return '\'%s\'' % obj.replace('\n', '\\n').replace('\r', '')

    def _is_dict(self, obj):
        return isinstance(obj, dict)

    def _get_sorted_dict_items(self, obj):
        assert self._is_dict(obj), '%s is not a dict object' % obj
        items = obj.items()
        items.sort(key=lambda (k, v): k)
        return items


def dump(obj, filename, **kwargs):
    dumper = PyDumper(**kwargs)
    content = dumper.dump(obj)
    with open(filename, 'w') as f:
        f.write(content)


def _test_dump():
    data = {
        'base': {
            'name': 'name',
            'desc': u'来\n段\n中\n文'},
        'graph': {
            'a': [{'1': {1, 2, 3}}, {'2': (1, 3)}]
        }
    }
    dump(
        data, 'test.py',
        src_file='buff_1_1.bf',
        author='zxn5911',
        record_time=True,
        # dump_type=DumpType.FIRST_KEYS_AS_ATTR
    )


if __name__ == '__main__':
    _test_dump()
