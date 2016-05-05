import attr
import sentaku
from .ux import TodoUX


@attr.s
class ViaAPI(sentaku.ApplicationImplementation):
    """access to the core api of the application"""
    api = attr.ib()


@attr.s
class ViaUX(sentaku.ApplicationImplementation):
    """access to the application via the basic api of the pseudo-ux"""
    ux = attr.ib()

    @classmethod
    def from_api(cls, api):
        """creates a ux for the given api before

        returning the implementation holder"""
        return cls(ux=TodoUX(api))


class TodoItem(sentaku.Element):
    """describing a todo list element"""
    def __init__(self, parent, name):
        super(TodoItem, self).__init__(parent=parent)
        self.name = name

    @property
    def completed(self):
        raise NotImplementedError

    set_completion_state = sentaku.ImplementationRegistry()

    @set_completion_state.implemented_for(ViaAPI)
    def set_completion_state(self, value):
        api = self.impl.api
        col = api.get_by(self.parent.name)
        elem = col.get_by(self.name)
        elem.completed = value

    @set_completion_state.implemented_for(ViaUX)
    def set_completion_state(self, value):
        ux = self.impl.ux
        col = ux.get_by(self.parent.name)
        elem = col.get_by(self.name)
        elem.completed = value

    @completed.setter
    def completed(self, value):
        self.set_completion_state(value)


class TodoCollection(sentaku.Collection):
    """domain object describing a todo list"""
    def __init__(self, parent, name):
        super(TodoCollection, self).__init__(parent=parent)
        self.name = name

    create_item = sentaku.ImplementationRegistry()

    @create_item.implemented_for(ViaAPI)
    def create_item(self, name):
        api = self.impl.api
        api_list = api.get_by(self.name)

        elem = api_list.create_item(name=name)
        assert elem
        return TodoItem(self, name=name)

    @create_item.implemented_for(ViaUX)
    def create_item(self, name):
        ux = self.impl.ux
        collection = ux.get_by(self.name)
        collection.create_item(name)
        return TodoItem(self, name=name)

    get_by = sentaku.ImplementationRegistry()

    @get_by.implemented_for(ViaAPI)
    def get_by(self, name):
        api = self.impl.api
        api_list = api.get_by(self.name)
        elem = api_list.get_by(name)
        if elem is not None:
            return TodoItem(self, name=name)

    @get_by.implemented_for(ViaUX)
    def get_by(self, name):
        ux = self.impl.ux
        ux_list = ux.get_by(self.name)
        elem = ux_list.get_by(name)
        if elem is not None:
            return TodoItem(self, name=name)

    clear_completed = sentaku.ImplementationRegistry()

    @clear_completed.implemented_for(ViaAPI)
    def clear_completed(self):
        api = self.impl.api
        api_list = api.get_by(self.name)
        api_list.clear_completed()

    @clear_completed.implemented_for(ViaUX)
    def clear_completed(self):
        ux = self.impl.ux
        ux_list = ux.get_by(self.name)
        ux_list.clear_completed()


class TodoApi(sentaku.ApplicationDescription):
    """example description for a simple todo application"""

    @classmethod
    def from_api(cls, api):
        """
        create an application description for the todo app,
        that based on the api can use either tha api or the ux for interaction
        """
        via_api = ViaAPI(api)
        via_ux = ViaUX.from_api(api)
        return cls.from_implementations([via_api, via_ux])

    create_collection = sentaku.ImplementationRegistry()

    @create_collection.implemented_for(ViaAPI)
    def create_collection(self, name):
        api = self.impl.api
        elem = api.create_item(name=name)
        assert elem
        return TodoCollection(self, name=name)

    @create_collection.implemented_for(ViaUX)
    def create_collection(self, name):
        ux = self.impl.ux
        ux.create_item(name)
        return TodoCollection(self, name=name)
