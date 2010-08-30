from unittest import TestCase
from paginateanything import (Paginator, EmptyPage,
                              PageNotAnInteger)

class PaginatorTests(TestCase):
    """
    Tests for the Paginator and Page classes.
    """

    def check_paginator(self, params, output):
        """
        Helper method that instantiates a Paginator object from the passed
        params and then checks that its attributes match the passed output.
        """
        count, num_pages, page_range = output
        paginator = Paginator(*params)
        self.check_attribute('count', paginator, count, params)
        self.check_attribute('num_pages', paginator, num_pages, params)
        self.check_attribute('page_range', paginator, page_range, params)

    def check_attribute(self, name, paginator, expected, params):
        """
        Helper method that checks a single attribute and gives a nice error
        message upon test failure.
        """
        got = getattr(paginator, name)
        self.assertEqual(expected, got,
            "For '%s', expected %s but got %s.  Paginator parameters were: %s"
            % (name, expected, got, params))

    def test_paginator_validate_number(self):
        paginator = Paginator(10, 2)

        # Make sure invalid pages throw the appropriate errors
        self.assertRaises(PageNotAnInteger, paginator.validate_number, "wtf")
        self.assertRaises(EmptyPage, paginator.validate_number, 0)
        self.assertRaises(EmptyPage, paginator.validate_number, 100)

        # Make sure validate_number throws EmptyPage when
        # allow_empty_first_page is false and there are no items
        paginator = Paginator(0, 2, allow_empty_first_page=False)
        self.assertRaises(EmptyPage, paginator.validate_number, 1)
        

        # Can't seem to find the conditions for paginator that cause
        # line 30 to happen, so I'm forcing it.
        paginator = Paginator(0, 2, allow_empty_first_page=False)
        num_pages = paginator.num_pages # Pre-calculate the num-pages
        self.assertEqual(num_pages, 0)
        paginator.allow_empty_first_page = True
        paginator.validate_number(1)
        
    def test_paginator(self):
        """
        Tests the paginator attributes using varying inputs.
        """
        nine = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        ten = nine + [10]
        eleven = ten + [11]
        tests = (
            # Each item is two tuples:
            #     First tuple is Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is resulting Paginator attributes - count,
            #         num_pages, and page_range.
            # Ten items, varying orphans, no empty first page.
            ((ten, 4, 0, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, False), (10, 2, [1, 2])),
            ((ten, 4, 5, False), (10, 2, [1, 2])),
            ((ten, 4, 6, False), (10, 1, [1])),
            # Ten items, varying orphans, allow empty first page.
            ((ten, 4, 0, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, True), (10, 2, [1, 2])),
            ((ten, 4, 5, True), (10, 2, [1, 2])),
            ((ten, 4, 6, True), (10, 1, [1])),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1, [1])),
            (([1], 4, 1, False), (1, 1, [1])),
            (([1], 4, 2, False), (1, 1, [1])),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1, [1])),
            (([1], 4, 1, True), (1, 1, [1])),
            (([1], 4, 2, True), (1, 1, [1])),
            # Zero items, varying orphans, no empty first page.
            (([], 4, 0, False), (0, 0, [])),
            (([], 4, 1, False), (0, 0, [])),
            (([], 4, 2, False), (0, 0, [])),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 1, [1])),
            (([], 4, 1, True), (0, 1, [1])),
            (([], 4, 2, True), (0, 1, [1])),
            # Number if items one less than per_page.
            (([], 1, 0, True), (0, 1, [1])),
            (([], 1, 0, False), (0, 0, [])),
            (([1], 2, 0, True), (1, 1, [1])),
            ((nine, 10, 0, True), (9, 1, [1])),
            # Number if items equal to per_page.
            (([1], 1, 0, True), (1, 1, [1])),
            (([1, 2], 2, 0, True), (2, 1, [1])),
            ((ten, 10, 0, True), (10, 1, [1])),
            # Number if items one more than per_page.
            (([1, 2], 1, 0, True), (2, 2, [1, 2])),
            (([1, 2, 3], 2, 0, True), (3, 2, [1, 2])),
            ((eleven, 10, 0, True), (11, 2, [1, 2])),
            # Number if items one more than per_page with one orphan.
            (([1, 2], 1, 1, True), (2, 1, [1])),
            (([1, 2, 3], 2, 1, True), (3, 1, [1])),
            ((eleven, 10, 1, True), (11, 1, [1])),
        )
        for params, output in tests:
            params = list(params)
            params[0] = len(params[0])
            self.check_paginator(params, output)

    def check_indexes(self, params, page_num, indexes):
        """
        Helper method that instantiates a Paginator object from the passed
        params and then checks that the start and end indexes of the passed
        page_num match those given as a 2-tuple in indexes.
        """
        paginator = Paginator(*params)
        if page_num == 'first':
            page_num = 1
        elif page_num == 'last':
            page_num = paginator.num_pages
        page = paginator.page(page_num)
        start, end = indexes
        msg = ("For %s of page %s, expected %s but got %s."
               " Paginator parameters were: %s")
        self.assertEqual(start, page.start_index(),
            msg % ('start index', page_num, start, page.start_index(), params))
        self.assertEqual(end, page.end_index(),
            msg % ('end index', page_num, end, page.end_index(), params))

    def test_page_repr(self):
        paginator = Paginator(10, 2)
        page = paginator.page(1)

        result = page.__repr__()
        self.assertEqual("<Page 1 of 5>", result)

    def test_page_has_next(self):
        paginator = Paginator(10, 2)

        page = paginator.page(1)
        self.assertTrue(page.has_next())

        page = paginator.page(5)
        self.assertFalse(page.has_next())

    def test_page_has_previous(self):
        paginator = Paginator(10, 2)

        page = paginator.page(1)
        self.assertFalse(page.has_previous())

        page = paginator.page(5)
        self.assertTrue(page.has_previous())

    def test_page_has_other_pages(self):
        paginator = Paginator(10, 2)

        page = paginator.page(1)
        self.assertTrue(page.has_other_pages())

        page = paginator.page(5)
        self.assertTrue(page.has_other_pages())


        paginator = Paginator(1, 2)
        page = paginator.page(1)
        self.assertFalse(page.has_other_pages())

    def test_previous_page_number(self):
        paginator = Paginator(10, 2)

        page = paginator.page(5)

        self.assertEqual(page.previous_page_number(), 4)

    def test_next_page_number(self):
        paginator = Paginator(10, 2)

        page = paginator.page(1)

        self.assertEqual(page.next_page_number(), 2)


    def test_page_indexes(self):
        """
        Tests that paginator pages have the correct start and end indexes.
        """
        ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tests = (
            # Each item is three tuples:
            #     First tuple is Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is the start and end indexes of the first page.
            #     Third tuple is the start and end indexes of the last page.
            # Ten items, varying per_page, no orphans.
            ((ten, 1, 0, True), (1, 1), (10, 10)),
            ((ten, 2, 0, True), (1, 2), (9, 10)),
            ((ten, 3, 0, True), (1, 3), (10, 10)),
            ((ten, 5, 0, True), (1, 5), (6, 10)),
            # Ten items, varying per_page, with orphans.
            ((ten, 1, 1, True), (1, 1), (9, 10)),
            ((ten, 1, 2, True), (1, 1), (8, 10)),
            ((ten, 3, 1, True), (1, 3), (7, 10)),
            ((ten, 3, 2, True), (1, 3), (7, 10)),
            ((ten, 3, 4, True), (1, 3), (4, 10)),
            ((ten, 5, 1, True), (1, 5), (6, 10)),
            ((ten, 5, 2, True), (1, 5), (6, 10)),
            ((ten, 5, 5, True), (1, 10), (1, 10)),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1), (1, 1)),
            (([1], 4, 1, False), (1, 1), (1, 1)),
            (([1], 4, 2, False), (1, 1), (1, 1)),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1), (1, 1)),
            (([1], 4, 1, True), (1, 1), (1, 1)),
            (([1], 4, 2, True), (1, 1), (1, 1)),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 0), (0, 0)),
            (([], 4, 1, True), (0, 0), (0, 0)),
            (([], 4, 2, True), (0, 0), (0, 0)),
        )
        for params, first, last in tests:
            params = list(params)
            params[0] = len(params[0])
            self.check_indexes(params, 'first', first)
            self.check_indexes(params, 'last', last)
        # When no items and no empty first page, we should get EmptyPage error.
        self.assertRaises(EmptyPage, self.check_indexes, (0, 4, 0, False), 1, None)
        self.assertRaises(EmptyPage, self.check_indexes, (0, 4, 1, False), 1, None)
        self.assertRaises(EmptyPage, self.check_indexes, (0, 4, 2, False), 1, None)
