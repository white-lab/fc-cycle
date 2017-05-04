from unittest import TestCase


class ImportTest(TestCase):
    def test_tube_pos(self):
        from fc_cycle.main import get_tube_pos

        self.assertEqual(
            get_tube_pos(0, 22),
            1,
        )
        self.assertEqual(
            get_tube_pos(10, 22),
            11,
        )
        self.assertEqual(
            get_tube_pos(11, 22),
            12,
        )
        self.assertEqual(
            get_tube_pos(21, 22),
            22,
        )
        self.assertEqual(
            get_tube_pos(22, 22),
            1,
        )

        self.assertEqual(
            get_tube_pos(0, 12),
            1,
        )
        self.assertEqual(
            get_tube_pos(5, 12),
            6,
        )
        self.assertEqual(
            get_tube_pos(6, 12),
            17,
        )
        self.assertEqual(
            get_tube_pos(11, 12),
            22,
        )
        self.assertEqual(
            get_tube_pos(12, 12),
            1,
        )

        self.assertEqual(
            get_tube_pos(0, 20),
            1,
        )
        self.assertEqual(
            get_tube_pos(9, 20),
            10,
        )
        self.assertEqual(
            get_tube_pos(10, 20),
            13,
        )
        self.assertEqual(
            get_tube_pos(19, 20),
            22,
        )
        self.assertEqual(
            get_tube_pos(20, 20),
            1,
        )
