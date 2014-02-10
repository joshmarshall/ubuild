from ubuild_modules.registry import Registry, InvalidModule
from unittest import TestCase


class TestRegistry(TestCase):

    def setUp(self):
        self._registry = Registry()

    def test_register(self):

        def foo(config):
            self.assertEqual({"foo": "bar"}, config)
            return {"qux": "baz"}

        self._registry.register("foo", foo)
        result = self._registry.execute("foo", {"foo": "bar"})
        self.assertEqual({"qux": "baz"}, result)

    def test_execute_raises_invalid_module(self):
        with self.assertRaises(InvalidModule):
            self._registry.execute("foo", lambda: None)
