paginateanything
-----------------

This is a simple paginator.  It doesn't care what you're paginating as
long as you know the count and the number of items per page::

    from paginateanything import Paginator, Page
    numbers = range(100)
    paginator = Paginator(len(numbers), 5)
    page = paginator.page(1)
    items = numbers[page.start:page.stop)]

