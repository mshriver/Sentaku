import attr


@attr.s
class Element(object):
    """Base class for all application elements

    :param parent:
        controlling object of the element which is either a context
        or a surrounding element
    :type parent: :py:class:`Element` or :py:class:`ImplementationContext`
    """

    parent = attr.ib(repr=False)

    @property
    def context(self):
        """the context this element belongs to"""
        return self.parent.context

    @property
    def impl(self):
        """shortcut to get the currently active application implementation"""
        return self.context.impl


class Collection(Element):
    """base class for collections in the application

    :todo: generic helpers for querying
    """
