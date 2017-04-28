#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test files gathered from json.org and yaml.org
from __future__ import absolute_import

try:
    from common import *
except ImportError:
    from .common import *


class TestBoxFunctional(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        try:
            os.mkdir(tmp_dir)
        except OSError:
            pass

    def tearDown(self):
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_box(self):
        box = Box(**test_dict)
        assert box.key1 == test_dict['key1']
        assert dict(getattr(box, 'Key 2')) == test_dict['Key 2']
        setattr(box, 'TEST_KEY', 'VALUE')
        assert box.TEST_KEY == 'VALUE'
        delattr(box, 'TEST_KEY')
        assert 'TEST_KEY' not in box.to_dict(), box.to_dict()
        assert isinstance(box['Key 2'].Key4, Box)
        assert "'key1': 'value1'" in str(box)
        assert repr(box).startswith("<Box:")
        box2 = Box([((3, 4), "A"), ("_box_config", 'test')])
        assert box2[(3, 4)] == "A"
        assert box2['_box_config'] == 'test'

    def test_box_modifiy_at_depth(self):
        box = Box(**test_dict)
        assert 'key1' in box
        assert 'key2' not in box
        box['Key 2'].new_thing = "test"
        assert box['Key 2'].new_thing == "test"
        box['Key 2'].new_thing += "2"
        assert box['Key 2'].new_thing == "test2"
        assert box['Key 2'].to_dict()['new_thing'] == "test2"
        assert box.to_dict()['Key 2']['new_thing'] == "test2"
        box.__setattr__('key1', 1)
        assert box['key1'] == 1
        box.__delattr__('key1')
        assert 'key1' not in box

    def test_error_box(self):
        box = Box(**test_dict)
        try:
            getattr(box, 'hello')
        except AttributeError:
            pass
        else:
            raise AssertionError("Should not find 'hello' in the test dict")

    def test_box_from_dict(self):
        ns = Box({"k1": "v1", "k2": {"k3": "v2"}})
        assert ns.k2.k3 == "v2"

    def test_box_from_bad_dict(self):
        try:
            Box('{"k1": "v1", "k2": {"k3": "v2"}}')
        except ValueError:
            assert True
        else:
            assert False, "Should have raised type error"

    def test_basic_box(self):
        a = Box(one=1, two=2, three=3)
        b = Box({'one': 1, 'two': 2, 'three': 3})
        c = Box((zip(['one', 'two', 'three'], [1, 2, 3])))
        d = Box(([('two', 2), ('one', 1), ('three', 3)]))
        e = Box(({'three': 3, 'one': 1, 'two': 2}))
        assert a == b == c == d == e

    def test_config_box(self):
        g = {"b0": 'no',
             "b1": 'yes',
             "b2": 'True',
             "b3": 'false',
             "b4": True,
             "i0": '34',
             "f0": '5.5',
             "f1": '3.333',
             "l0": '4,5,6,7,8',
             "l1": '[2 3 4 5 6]'}

        cns = ConfigBox(bb=g)
        assert cns.bb.list("l1", spliter=" ") == ["2", "3", "4", "5", "6"]
        assert cns.bb.list("l0", mod=lambda x: int(x)) == [4, 5, 6, 7, 8]
        assert not cns.bb.bool("b0")
        assert cns.bb.bool("b1")
        assert cns.bb.bool("b2")
        assert not cns.bb.bool("b3")
        assert cns.bb.int("i0") == 34
        assert cns.bb.float("f0") == 5.5
        assert cns.bb.float("f1") == 3.333
        assert cns.bb.getboolean("b4"), cns.bb.getboolean("b4")
        assert cns.bb.getfloat("f0") == 5.5
        assert cns.bb.getint("i0") == 34
        assert cns.bb.getint("Hello!", 5) == 5
        assert cns.bb.getfloat("Wooo", 4.4) == 4.4
        assert cns.bb.getboolean("huh", True) is True
        assert cns.bb.list("Waaaa", [1]) == [1]
        assert repr(cns).startswith("<ConfigBox")

    def test_protected_box_methods(self):
        my_box = Box(a=3)
        try:
            my_box.to_dict = 'test'
        except AttributeError:
            pass
        else:
            raise AttributeError("Should not be able to set 'to_dict'")

        try:
            del my_box.to_json
        except AttributeError:
            pass
        else:
            raise AttributeError("Should not be able to delete 'to_dict'")

    def test_bad_args(self):
        try:
            Box('123', '432')
        except TypeError:
            pass
        else:
            raise AssertionError("Shouldn't have worked")

    def test_box_inits(self):
        a = Box({'data': 2, 'count': 5})
        b = Box(data=2, count=5)
        c = Box({'data': 2, 'count': 1}, count=5)
        d = Box([('data', 2), ('count', 5)])
        e = Box({'a': [{'item': 3}, {'item': []}]})
        assert e.a[1].item == []
        assert a == b == c == d

    def test_bad_inits(self):
        try:
            Box("testing")
        except ValueError:
            pass
        else:
            raise AssertionError("Should raise Value Error")

        try:
            Box(22)
        except ValueError:
            pass
        else:
            raise AssertionError("Should raise Value Error")

        try:
            Box(22, 33)
        except TypeError:
            pass
        else:
            raise AssertionError("Should raise Type Error")

    def test_create_subdicts(self):
        a = Box({'data': 2, 'count': 5})
        a.brand_new = {'subdata': 1}
        assert a.brand_new.subdata == 1
        a.new_list = [{'sub_list_item': 1}]
        assert a.new_list[0].sub_list_item == 1
        assert isinstance(a.new_list, BoxList)
        a.new_list2 = [[{'sub_list_item': 2}]]
        assert a.new_list2[0][0].sub_list_item == 2
        b = a.to_dict()
        assert not isinstance(b['new_list'], BoxList)

    def test_to_json(self):
        a = Box(test_dict)
        assert json.loads(a.to_json(indent=0)) == test_dict

        a.to_json(tmp_json_file)
        with open(tmp_json_file) as f:
            data = json.load(f)
            assert data == test_dict

    def test_to_yaml(self):
        a = Box(test_dict)
        assert yaml.load(a.to_yaml()) == test_dict

    def test_to_yaml_file(self):
        a = Box(test_dict)
        a.to_yaml(tmp_yaml_file)
        with open(tmp_yaml_file) as f:
            data = yaml.load(f)
            assert data == test_dict

    def test_boxlist(self):
        new_list = BoxList({'item': x} for x in range(0, 10))
        new_list.extend([{'item': 22}])
        assert new_list[-1].item == 22
        new_list.append([{'bad_item': 33}])
        assert new_list[-1][0].bad_item == 33
        assert repr(new_list).startswith("<BoxList:")
        for x in new_list.to_list():
            assert not isinstance(x, (BoxList, Box))
        new_list.insert(0, {'test': 5})
        new_list.insert(1, ['a', 'b'])
        new_list.append('x')
        assert new_list[0].test == 5
        assert isinstance(str(new_list), str)
        assert isinstance(new_list[1], BoxList)
        assert not isinstance(new_list.to_list(), BoxList)

    def test_dir(self):
        test_dict = {'key1': 'value1',
                     'not$allowed': 'fine_value',
                     'BigCamel': 'hi',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        a = Box(test_dict, camel_killer_box=True)
        assert 'key1' in dir(a)
        assert 'not$allowed' not in dir(a)
        assert 'Key4' in a['Key 2']
        for item in ('to_yaml', 'to_dict', 'to_json'):
            assert item in dir(a)

        assert a.big_camel == 'hi'
        assert 'big_camel' in dir(a)

        b = ConfigBox(test_dict)

        for item in ('to_yaml', 'to_dict', 'to_json', 'int', 'list', 'float'):
            assert item in dir(b)

    def test_update(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        a = Box(test_dict)
        a.update({'key1': {'new': 5}, 'Key 2': {"add_key": 6},
                  'lister': ['a']})
        a.update([('asdf', 'fdsa')])
        a.update(testkey=66)

        assert a.key1.new == 5
        assert a['Key 2'].add_key == 6
        assert "Key5" in a['Key 2'].Key4
        assert isinstance(a.key1, Box)
        assert isinstance(a.lister, BoxList)
        assert a.asdf == 'fdsa'
        assert a.testkey == 66

    def test_auto_attr(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        a = Box(test_dict, default_box=True)
        assert a.a.a.a.a == Box()
        a.b.b = 4
        assert a.b.b == 4

    def test_set_default(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        a = Box(test_dict)

        new = a.setdefault("key3", {'item': 2})
        new_list = a.setdefault("lister", [{'gah': 7}])
        assert a.setdefault("key1", False) == 'value1'

        assert new == Box(item=2)
        assert new_list == BoxList([{'gah': 7}])
        assert a.key3.item == 2
        assert a.lister[0].gah == 7

    def test_from_json_file(self):
        bx = Box.from_json(filename=data_json_file)
        assert isinstance(bx, Box)
        assert bx.widget.window.height == 500

    def test_from_yaml_file(self):
        bx = Box.from_yaml(filename=data_yaml_file)
        assert isinstance(bx, Box)
        assert bx.total == 4443.52

    def test_from_json(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        bx = Box.from_json(json.dumps(test_dict))
        assert isinstance(bx, Box)
        assert bx.key1 == 'value1'

    def test_from_yaml(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}}}
        bx = Box.from_yaml(yaml.dump(test_dict),
                           conversion_box=False,
                           default_box=True)
        assert isinstance(bx, Box)
        assert bx.key1 == 'value1'
        assert bx.Key_2 == Box()

    def test_bad_from_json(self):
        try:
            Box.from_json()
        except BoxError as err:
            assert 'requires' in str(err)
        else:
            raise AssertionError("Box creation should have failed")

        try:
            Box.from_json(json_string="[1]")
        except BoxError as err:
            assert 'dict' in str(err)
        else:
            raise AssertionError("Box creation should have failed")

    def test_bad_from_yaml(self):
        try:
            Box.from_yaml()
        except BoxError as err:
            assert 'requires' in str(err)
        else:
            raise AssertionError("Box creation should have failed")

        try:
            Box.from_yaml('lol')
        except BoxError as err:
            assert 'dict' in str(err)
        else:
            raise AssertionError("Box creation should have failed")

    def test_conversion_box(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}},
                     3: 'howdy',
                     'not': 'true',
                     (3, 4): 'test',
                     False: 'tree'
                     }
        bx = Box(test_dict, conversion_box=True)
        assert bx.Key_2.Key_3 == "Value 3"
        assert bx.x3 == 'howdy'
        assert bx.xnot == 'true'
        assert bx.x3_4 == 'test'
        try:
            getattr(bx, "(3, 4)")
        except AttributeError:
            pass
        else:
            raise AssertionError("Should have failed")

    def test_frozen(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}},
                     3: 'howdy',
                     'not': 'true',
                     (3, 4): 'test',
                     'alist': ['a', 'b', 'c']
                     }
        bx = Box(test_dict, frozen_box=True)

        assert isinstance(bx.alist, tuple)
        assert bx.alist[0] == 'a'
        try:
            bx.new = 3
        except BoxError:
            pass
        else:
            raise AssertionError("It's supposed to be frozen")

        try:
            bx['new'] = 3
        except BoxError:
            pass
        else:
            raise AssertionError("It's supposed to be frozen")

        try:
            del bx['not']
        except BoxError:
            pass
        else:
            raise AssertionError("It's supposed to be frozen")

        try:
            delattr(bx, "key1")
        except BoxError:
            pass
        else:
            raise AssertionError("It's supposed to be frozen")

        assert hash(bx)

        bx2 = Box(test_dict)
        try:
            hash(bx2)
        except TypeError:
            pass
        else:
            raise AssertionError("Non frozen can't be hashed")

    def test_config(self):
        test_dict = {'key1': 'value1',
                     "Key 2": {"Key 3": "Value 3",
                               "Key4": {"Key5": "Value5"}},
                     3: 'howdy',
                     'not': 'true',
                     (3, 4): 'test',
                     '_box_config': True
                     }
        bx = Box(test_dict)
        assert bx['_box_config'] is True
        assert isinstance(bx._box_config, dict)
        try:
            delattr(bx, '_box_config')
        except BoxError:
            pass
        else:
            raise AttributeError("You can't delete that!")

    def test_default_box(self):
        bx = Box(test_dict, default_box=True, default_box_attr={'hi': 'there'})
        assert bx.key_88 == {'hi': 'there'}

        bx2 = Box(test_dict, default_box=True, default_box_attr=Box)
        assert isinstance(bx2.key_77, Box)

        bx3 = Box(default_box=True, default_box_attr=3)
        assert bx3.hello == 3

        bx4 = Box(default_box=True, default_box_attr=ConfigBox)
        assert isinstance(bx4.bbbbb, ConfigBox)

    def test_camel_killer_box(self):
        td = extended_test_dict.copy()
        td['CamelCase'] = 'Item'
        td['321CamelCaseFever!'] = 'Safe'

        kill_box = Box(td, camel_killer_box=True, conversion_box=False)
        assert kill_box.camel_case == 'Item'
        assert kill_box['321CamelCaseFever!'] == 'Safe'

        con_kill_box = Box(td, conversion_box=True, camel_killer_box=True)
        assert con_kill_box.camel_case == 'Item'
        assert con_kill_box.x321_camel_case_fever == 'Safe'

    def test_property_box(self):
        td = test_dict.copy()
        td['inner'] = {'CamelCase': 'Item'}

        pbox = SBox(td, camel_killer_box=True)
        assert isinstance(pbox.inner, SBox)
        assert pbox.inner.camel_case == 'Item'
        assert json.loads(pbox.json)['inner']['CamelCase'] == 'Item'
        assert yaml.load(pbox.yaml)['inner']['CamelCase'] == 'Item'
        assert repr(pbox['inner']).startswith('<ShorthandBox')
        assert not isinstance(pbox.dict, Box)
        assert pbox.dict['inner']['CamelCase'] == 'Item'

    def test_box_list_to_json(self):
        bl = BoxList([{'item': 1, 'CamelBad': 2}])
        assert json.loads(bl.to_json())[0]['item'] == 1

    def test_box_list_from_json(self):
        alist = [{'item': 1}, {'CamelBad': 2}]
        json_list = json.dumps(alist)
        bl = BoxList.from_json(json_list, camel_killer_box=True)
        assert bl[0].item == 1
        assert bl[1].camel_bad == 2

        try:
            BoxList.from_json(json.dumps({'a': 2}))
        except BoxError:
            pass
        else:
            raise AssertionError("Should have erred")

    def test_box_list_to_yaml(self):
        bl = BoxList([{'item': 1, 'CamelBad': 2}])
        assert yaml.load(bl.to_yaml())[0]['item'] == 1

    def test_box_list_from_yaml(self):
        alist = [{'item': 1}, {'CamelBad': 2}]
        yaml_list = yaml.dump(alist)
        bl = BoxList.from_yaml(yaml_list, camel_killer_box=True)
        assert bl[0].item == 1
        assert bl[1].camel_bad == 2

        try:
            BoxList.from_yaml(yaml.dump({'a': 2}))
        except BoxError:
            pass
        else:
            raise AssertionError("Should have erred")

    def test_boxlist_box_it_up(self):
        bxl = BoxList([extended_test_dict])
        bxl.box_it_up()
        assert "Key 3" in bxl[0].Key_2._box_config['__converted']

    def test_box_modify_tuples(self):
        bx = Box(extended_test_dict, modify_tuples_box=True)
        assert bx.tuples_galore[0].item == 3
        assert isinstance(bx.tuples_galore[0], Box)
        assert isinstance(bx.tuples_galore[1], tuple)

    def test_box_set_attribs(self):
        bx = Box(extended_test_dict, conversion_box=False, camel_killer_box=True)
        bx.camel_case = {'new': 'item'}
        assert bx['CamelCase'] == Box(new='item')

        bx2 = Box(extended_test_dict)
        bx2.Key_2 = 4
        assert bx2["Key 2"] == 4

    def test_functional_hearthstone_data(self):
        hearth = Box.from_json(filename=data_hearthstone,
                               conversion_box=True,
                               camel_killer_box=True,
                               default_box=False)
        assert hearth.the_jade_lotus

        try:
            hearth._bad_value
        except AttributeError:
            pass
        else:
            raise AssertionError("Should not exist")

        try:
            hearth.the_jade_lotus._bad_value
        except AttributeError:
            pass
        else:
            raise AssertionError("Should not exist")

        assert hearth._Box__box_config() == hearth.the_jade_lotus._Box__box_config(), "{} != {}".format(hearth._Box__box_config(), hearth.the_jade_lotus._Box__box_config())

    def test_functional_spaceballs(self):
        my_box = Box(movie_data)

        my_box.movies.Spaceballs.Stars.append({"name": "Bill Pullman", "imdb": "nm0000597", "role": "Lone Starr"})
        assert my_box.movies.Spaceballs.Stars[-1].role == "Lone Starr"
        assert my_box.movies.Robin_Hood_Men_in_Tights.length == 104
        my_box.movies.Robin_Hood_Men_in_Tights.Stars.pop(0)
        assert my_box.movies.Robin_Hood_Men_in_Tights.Stars[0].name == "Richard Lewis"

