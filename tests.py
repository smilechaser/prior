import unittest

import prior

# self.assertEqual(self.seq, range(10))
# self.assertRaises(TypeError, random.shuffle, (1,2,3))
# self.assertTrue(element in self.seq)
#
# with self.assertRaises(ValueError):
#     random.sample(self.seq, 20)


class BaseTest(unittest.TestCase):

    def make_ledger(self, data):

        self.ledger = prior.Ledger()

        load_data(self.ledger, data)


def load_data(ledger, data):

    ledger.records = []

    def provider():
        return data

    ledger._gather_files(provider)


class TestEmptyList(BaseTest):

    def setUp(self):

        items = []
        self.make_ledger(items)

    def test_search(self):

        with self.assertRaises(prior.RecordNotFoundException):
            self.ledger.get_record_by_name('xxx')

        with self.assertRaises(prior.RecordNotFoundException):
            self.ledger.get_record_by_name('')

        with self.assertRaises(prior.RecordNotFoundException):
            self.ledger.get_record_by_name(None)


class TestSingleItem(BaseTest):

    def setUp(self):

        items = ['01_foo']
        self.make_ledger(items)

    def test_all_actions(self):

        ledger = self.ledger

        ACTION_LIST = (
            ledger.up,
            ledger.down,
            ledger.top,
            ledger.bottom,
            ledger.top,
            ledger.bottom
        )

        self.assertTrue(len(self.ledger.records) == 1)

        record = self.ledger.records[0]

        for action in ACTION_LIST:

            action(record)

            self.assertTrue(len(self.ledger.records) == 1)

            self.assertTrue(self.ledger.records[0] == record)


class TestLimits(BaseTest):

    def setUp(self):

        items = ['01_foo', '02_foo']
        self.make_ledger(items)

    def test_top_limit(self):

        record = self.ledger.records[0]

        for action in (self.ledger.up, self.ledger.top):

            action(record)

            self.assertTrue(self.ledger.records[0] == record)

    def test_bottom_limit(self):

        record = self.ledger.records[-1]

        for action in (self.ledger.down, self.ledger.bottom):

            action(record)

            self.assertTrue(self.ledger.records[-1] == record)


class TestMultipleItems(BaseTest):

    def setUp(self):

        items = ['01_boo', '03_foo', '05_zoo']
        self.make_ledger(items)

    def test_up(self):

        record = self.ledger.records[-1]

        self.ledger.up(record)
        self.assertTrue(self.ledger.records[1] == record)

        self.ledger.up(record)
        self.assertTrue(self.ledger.records[0] == record)

    def test_down(self):

        record = self.ledger.records[1]

        self.ledger.down(record)
        self.assertTrue(self.ledger.records[-1] == record)

    def test_top(self):

        record = self.ledger.records[-1]

        self.ledger.top(record)
        self.assertTrue(self.ledger.records[0] == record)

    def test_bottom(self):

        record = self.ledger.records[0]

        self.ledger.bottom(record)
        self.assertTrue(self.ledger.records[-1] == record)


if __name__ == '__main__':
    unittest.main()
