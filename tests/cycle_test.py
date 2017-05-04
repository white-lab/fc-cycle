from unittest import TestCase

from fc_cycle import main


class ImportTest(TestCase):
    def test_total_tubes(self):
        self.assertEqual(
            main.get_total_tubes(85 * 60, 5 * 60, 60),
            80,
        )
        self.assertEqual(
            main.get_total_tubes(85 * 60, 0, 60),
            85,
        )

    def test_tube_pos(self):
        # Rack length * 2 tubes
        self.assertEqual(
            main.get_tube_pos(0, 22),
            1,
        )
        self.assertEqual(
            main.get_tube_pos(10, 22),
            11,
        )
        self.assertEqual(
            main.get_tube_pos(11, 22),
            12,
        )
        self.assertEqual(
            main.get_tube_pos(21, 22),
            22,
        )
        self.assertEqual(
            main.get_tube_pos(22, 22),
            1,
        )

        # 40 tubes
        self.assertEqual(
            main.get_tube_pos(0, 40),
            1,
        )
        self.assertEqual(
            main.get_tube_pos(10, 40),
            11,
        )
        self.assertEqual(
            main.get_tube_pos(11, 40),
            12,
        )
        self.assertEqual(
            main.get_tube_pos(21, 40),
            22,
        )
        self.assertEqual(
            main.get_tube_pos(22, 40),
            23,
        )
        self.assertEqual(
            main.get_tube_pos(32, 40),
            33,
        )
        self.assertEqual(
            main.get_tube_pos(33, 40),
            34,
        )
        self.assertEqual(
            main.get_tube_pos(39, 40),
            40,
        )
        self.assertEqual(
            main.get_tube_pos(40, 40),
            1,
        )

        # 12 tubes
        self.assertEqual(
            main.get_tube_pos(0, 12),
            1,
        )
        self.assertEqual(
            main.get_tube_pos(5, 12),
            6,
        )
        self.assertEqual(
            main.get_tube_pos(6, 12),
            17,
        )
        self.assertEqual(
            main.get_tube_pos(11, 12),
            22,
        )
        self.assertEqual(
            main.get_tube_pos(12, 12),
            1,
        )

        # 20 tubes
        self.assertEqual(
            main.get_tube_pos(0, 20),
            1,
        )
        self.assertEqual(
            main.get_tube_pos(9, 20),
            10,
        )
        self.assertEqual(
            main.get_tube_pos(10, 20),
            13,
        )
        self.assertEqual(
            main.get_tube_pos(19, 20),
            22,
        )
        self.assertEqual(
            main.get_tube_pos(20, 20),
            1,
        )

        # Odd number of tubes
        self.assertEqual(
            main.get_tube_pos(0, 5),
            1,
        )
        self.assertEqual(
            main.get_tube_pos(4, 5),
            22,
        )
        self.assertEqual(
            main.get_tube_pos(2, 5),
            3,
        )
        self.assertEqual(
            main.get_tube_pos(3, 5),
            21,
        )
        self.assertEqual(
            main.get_tube_pos(5, 5),
            1,
        )
